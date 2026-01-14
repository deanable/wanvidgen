"""Output handlers for persisting generated video sequences.

Provides utilities to export frames as:
- MP4/WEBM video files (via moviepy)
- WEBP animations
- PNG frame dumps

Each run is organized in timestamped directories with parameter metadata.
"""

from __future__ import annotations

import json
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Literal

import numpy as np
from PIL import Image

try:
    from ..log_config import get_logger
    logger = get_logger(__name__)
except ImportError:
    import logging
    logger = logging.getLogger(__name__)

VideoFormat = Literal["mp4", "webm"]


class OutputError(Exception):
    """Base exception for output handling errors."""
    pass


class EncoderMissingError(OutputError):
    """Raised when a required video encoder is not available."""
    pass


def _check_moviepy() -> tuple[bool, str | None]:
    """Check if moviepy is available and functional.
    
    Returns:
        Tuple of (available, error_message).
    """
    try:
        try:
            import moviepy.editor as mpy
        except (ImportError, AttributeError):
            from moviepy import ImageSequenceClip
        return True, None
    except ImportError as e:
        return False, f"moviepy not installed: {e}"
    except Exception as e:
        return False, f"moviepy error: {e}"


def _check_pillow_webp() -> tuple[bool, str | None]:
    """Check if Pillow has WEBP support.
    
    Returns:
        Tuple of (available, error_message).
    """
    try:
        from PIL import features
        if features.check("webp"):
            return True, None
        return False, "Pillow compiled without WEBP support"
    except Exception as e:
        return False, f"Error checking WEBP support: {e}"


def create_output_directory(base_dir: str | Path = "outputs") -> Path:
    """Create a timestamped output directory.
    
    Args:
        base_dir: Base directory for outputs.
    
    Returns:
        Path to the created timestamped directory.
    """
    base_path = Path(base_dir)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = base_path / timestamp
    output_path.mkdir(parents=True, exist_ok=True)
    
    logger.info("Created output directory", extra={"extra_fields": {
        "path": str(output_path),
    }})
    
    return output_path


def save_metadata(output_dir: Path, metadata: dict[str, Any]) -> Path:
    """Save generation parameters and metadata as JSON manifest.
    
    Args:
        output_dir: Directory to save metadata in.
        metadata: Dictionary of parameters and metadata.
    
    Returns:
        Path to the saved manifest file.
    """
    manifest_path = output_dir / "manifest.json"
    
    metadata_with_timestamp = {
        "timestamp": datetime.now().isoformat(),
        **metadata,
    }
    
    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(metadata_with_timestamp, f, indent=2)
    
    logger.info("Saved metadata manifest", extra={"extra_fields": {
        "path": str(manifest_path),
        "keys": list(metadata.keys()),
    }})
    
    return manifest_path


def save_frames_as_png(
    frames: list[np.ndarray] | np.ndarray,
    output_dir: Path,
    prefix: str = "frame",
) -> list[Path]:
    """Save frames as individual PNG files.
    
    Args:
        frames: List or array of frames (H, W, C) with values 0-255.
        output_dir: Directory to save frames in.
        prefix: Filename prefix for frames.
    
    Returns:
        List of paths to saved PNG files.
    """
    frames_dir = output_dir / "frames"
    frames_dir.mkdir(exist_ok=True)
    
    if isinstance(frames, np.ndarray) and frames.ndim == 4:
        frames = list(frames)
    
    saved_paths = []
    
    for i, frame in enumerate(frames):
        frame_path = frames_dir / f"{prefix}_{i:04d}.png"
        
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)
        
        img = Image.fromarray(frame)
        img.save(frame_path)
        saved_paths.append(frame_path)
    
    logger.info("Saved PNG frames", extra={"extra_fields": {
        "count": len(frames),
        "directory": str(frames_dir),
    }})
    
    return saved_paths


def save_as_webp(
    frames: list[np.ndarray] | np.ndarray,
    output_path: Path,
    fps: int = 30,
    duration: int | None = None,
) -> Path:
    """Save frames as animated WEBP.
    
    Args:
        frames: List or array of frames (H, W, C) with values 0-255.
        output_path: Path to save the WEBP file.
        fps: Frames per second.
        duration: Duration per frame in milliseconds. If None, calculated from fps.
    
    Returns:
        Path to the saved WEBP file.
    
    Raises:
        EncoderMissingError: If WEBP support is not available.
    """
    available, error_msg = _check_pillow_webp()
    if not available:
        logger.error("WEBP encoder not available", extra={"extra_fields": {
            "error": error_msg,
        }})
        raise EncoderMissingError(f"Cannot save WEBP: {error_msg}")
    
    if isinstance(frames, np.ndarray) and frames.ndim == 4:
        frames = list(frames)
    
    if duration is None:
        duration = int(1000 / fps)
    
    images = []
    for frame in frames:
        if frame.dtype != np.uint8:
            frame = np.clip(frame, 0, 255).astype(np.uint8)
        images.append(Image.fromarray(frame))
    
    if not images:
        raise OutputError("No frames to save")
    
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=0,
    )
    
    logger.info("Saved WEBP animation", extra={"extra_fields": {
        "path": str(output_path),
        "frames": len(frames),
        "fps": fps,
    }})
    
    return output_path


def save_as_video(
    frames: list[np.ndarray] | np.ndarray,
    output_path: Path,
    fps: int = 30,
    codec: str | None = None,
    bitrate: str | None = None,
) -> Path:
    """Save frames as MP4 or WEBM video using moviepy.
    
    Args:
        frames: List or array of frames (H, W, C) with values 0-255.
        output_path: Path to save the video file.
        fps: Frames per second.
        codec: Video codec. Auto-detected from extension if None.
        bitrate: Video bitrate (e.g., "5000k"). None uses default.
    
    Returns:
        Path to the saved video file.
    
    Raises:
        EncoderMissingError: If moviepy is not available.
    """
    available, error_msg = _check_moviepy()
    if not available:
        logger.error("moviepy not available", extra={"extra_fields": {
            "error": error_msg,
        }})
        raise EncoderMissingError(f"Cannot save video: {error_msg}")
    
    try:
        import moviepy.editor as mpy
        ImageSequenceClip = mpy.ImageSequenceClip
    except (ImportError, AttributeError):
        from moviepy import ImageSequenceClip
    
    if isinstance(frames, list):
        frames = np.array(frames)
    
    if frames.dtype != np.uint8:
        frames = np.clip(frames, 0, 255).astype(np.uint8)
    
    if frames.size == 0:
        raise OutputError("No frames to save")
    
    try:
        clip = ImageSequenceClip(list(frames), fps=fps)
        
        write_kwargs: dict[str, Any] = {"fps": fps}
        if codec:
            write_kwargs["codec"] = codec
        if bitrate:
            write_kwargs["bitrate"] = bitrate
        
        suffix = output_path.suffix.lower()
        if suffix == ".webm" and codec is None:
            write_kwargs["codec"] = "libvpx-vp9"
        elif suffix == ".mp4" and codec is None:
            write_kwargs["codec"] = "libx264"
        
        clip.write_videofile(str(output_path), logger=None, **write_kwargs)
        clip.close()
        
        logger.info("Saved video file", extra={"extra_fields": {
            "path": str(output_path),
            "frames": len(frames),
            "fps": fps,
            "codec": write_kwargs.get("codec"),
        }})
        
        return output_path
    
    except Exception as e:
        logger.error("Failed to save video", extra={"extra_fields": {
            "error": str(e),
            "path": str(output_path),
        }})
        raise OutputError(f"Video encoding failed: {e}") from e


def save_generation(
    frames: list[np.ndarray] | np.ndarray,
    metadata: dict[str, Any],
    output_dir: Path | None = None,
    formats: list[str] | None = None,
    fps: int = 30,
) -> dict[str, Path]:
    """Save a complete generation with frames and metadata.
    
    Args:
        frames: List or array of frames to save.
        metadata: Generation parameters and metadata.
        output_dir: Output directory. If None, creates a new timestamped directory.
        formats: List of formats to save ("mp4", "webm", "webp", "png"). 
                 If None, saves all available formats.
        fps: Frames per second for video/animation.
    
    Returns:
        Dictionary mapping format names to saved file paths.
    """
    if output_dir is None:
        output_dir = create_output_directory()
    
    if formats is None:
        formats = ["png"]
    
    saved_files: dict[str, Path] = {}
    
    save_metadata(output_dir, metadata)
    saved_files["metadata"] = output_dir / "manifest.json"
    
    for fmt in formats:
        try:
            if fmt == "png":
                save_frames_as_png(frames, output_dir)
                saved_files["png"] = output_dir / "frames"
            
            elif fmt == "webp":
                webp_path = output_dir / "animation.webp"
                save_as_webp(frames, webp_path, fps=fps)
                saved_files["webp"] = webp_path
            
            elif fmt in ("mp4", "webm"):
                video_path = output_dir / f"video.{fmt}"
                save_as_video(frames, video_path, fps=fps)
                saved_files[fmt] = video_path
            
            else:
                logger.warning("Unknown format requested", extra={"extra_fields": {
                    "format": fmt,
                }})
        
        except EncoderMissingError as e:
            logger.warning("Skipping format due to missing encoder", extra={"extra_fields": {
                "format": fmt,
                "reason": str(e),
            }})
        
        except Exception as e:
            logger.error("Failed to save format", extra={"extra_fields": {
                "format": fmt,
                "error": str(e),
            }}, exc_info=e)
    
    logger.info("Generation saved", extra={"extra_fields": {
        "output_dir": str(output_dir),
        "formats": list(saved_files.keys()),
    }})
    
    return saved_files
