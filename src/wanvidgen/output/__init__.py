"""Output handling package for wanvidgen."""

from .handlers import (
    EncoderMissingError,
    OutputError,
    create_output_directory,
    save_as_video,
    save_as_webp,
    save_frames_as_png,
    save_generation,
    save_metadata,
)

__all__ = [
    "EncoderMissingError",
    "OutputError",
    "create_output_directory",
    "save_as_video",
    "save_as_webp",
    "save_frames_as_png",
    "save_generation",
    "save_metadata",
]
