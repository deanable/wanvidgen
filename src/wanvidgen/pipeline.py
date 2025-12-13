"""Generation pipeline for video creation."""

import asyncio
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional, Tuple, List
import torch
import numpy as np

from .models import CLIPManager, VAEManager, UNetManager
from .memory import MemoryManager
from .exceptions import PipelineError, GenerationError


@dataclass
class GenerationConfig:
    """Configuration for generation parameters."""

    prompt: str
    negative_prompt: str = ""
    height: int = 512
    width: int = 512
    num_inference_steps: int = 50
    sampler: str = "ddim"
    scheduler: str = "linear"
    seed: int = 42
    fps: int = 8
    clip_guidance_scale: float = 7.5
    extra_params: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        """Convert config to dictionary."""
        return asdict(self)


@dataclass
class GenerationResult:
    """Result from generation."""

    frames: List[torch.Tensor]
    metadata: dict
    generation_config: GenerationConfig

    def get_frame_count(self) -> int:
        """Get number of generated frames."""
        return len(self.frames)

    def get_fps(self) -> int:
        """Get frames per second from metadata."""
        return self.metadata.get("fps", self.generation_config.fps)


class GenerationPipeline:
    """Main pipeline for coordinating model inference and generation.

    Orchestrates CLIP, VAE, and UNet models for video generation.
    Manages memory, device placement, and provides sync/async APIs.
    """

    def __init__(
        self,
        clip_config_path: str | Path,
        vae_config_path: str | Path,
        unet_config_path: str | Path,
        device: str = "cuda",
        clip_quantization: Optional[str] = None,
        vae_quantization: Optional[str] = None,
        unet_quantization: Optional[str] = None,
    ):
        """Initialize generation pipeline.

        Args:
            clip_config_path: Path to CLIP model config/weights.
            vae_config_path: Path to VAE model config/weights.
            unet_config_path: Path to UNet model config/weights.
            device: Device to use ("cuda" or "cpu").
            clip_quantization: Quantization for CLIP (q5, q6, or None).
            vae_quantization: Quantization for VAE (q5, q6, or None).
            unet_quantization: Quantization for UNet (q5, q6, or None).

        Raises:
            PipelineError: If model initialization fails.
        """
        self.device = device
        self.memory_manager = MemoryManager(device=device)

        try:
            self.clip_manager = CLIPManager(
                clip_config_path, device=device, quantization=clip_quantization
            )
            self.vae_manager = VAEManager(
                vae_config_path, device=device, quantization=vae_quantization
            )
            self.unet_manager = UNetManager(
                unet_config_path, device=device, quantization=unet_quantization
            )
        except Exception as e:
            raise PipelineError(
                f"Failed to initialize pipeline: {str(e)}",
                user_message="Failed to initialize generation pipeline",
            )

        self._models_loaded = False

    def load(self) -> None:
        """Load all models into memory.

        Raises:
            PipelineError: If model loading fails.
        """
        try:
            self.clip_manager.load()
            self.vae_manager.load()
            self.unet_manager.load()
            self._models_loaded = True
        except Exception as e:
            self.unload()
            raise PipelineError(
                f"Failed to load models: {str(e)}",
                user_message="Failed to load generation models",
            )

    def unload(self) -> None:
        """Unload all models and free memory."""
        self.clip_manager.unload()
        self.vae_manager.unload()
        self.unet_manager.unload()
        self._models_loaded = False
        self.memory_manager.free_memory()

    def is_loaded(self) -> bool:
        """Check if all models are loaded.

        Returns:
            True if all models are loaded.
        """
        return self._models_loaded

    def _validate_generation_config(self, config: GenerationConfig) -> None:
        """Validate generation configuration.

        Args:
            config: Configuration to validate.

        Raises:
            GenerationError: If config is invalid.
        """
        if not config.prompt:
            raise GenerationError(
                "Prompt cannot be empty",
                user_message="Please provide a prompt for generation",
            )

        if config.height <= 0 or config.width <= 0:
            raise GenerationError(
                "Height and width must be positive",
                user_message="Invalid image dimensions",
            )

        if config.num_inference_steps < 1:
            raise GenerationError(
                "Number of inference steps must be positive",
                user_message="Invalid number of steps",
            )

        if config.fps < 1:
            raise GenerationError(
                "FPS must be positive",
                user_message="Invalid frames per second",
            )

    def _check_memory_requirements(self, config: GenerationConfig) -> None:
        """Check if sufficient memory is available for generation.

        Args:
            config: Generation configuration.

        Raises:
            GPUMemoryError: If insufficient memory.
        """
        # Rough estimation: CLIP + VAE + UNet require ~15-20GB for 512x512
        # This is a conservative estimate
        estimated_required_mb = 15000

        self.memory_manager.assert_memory_available(
            estimated_required_mb,
            f"video generation ({config.width}x{config.height})",
        )

    def generate(self, config: GenerationConfig) -> GenerationResult:
        """Generate video frames (synchronous).

        Args:
            config: Generation configuration.

        Returns:
            GenerationResult with frames and metadata.

        Raises:
            GenerationError: If generation fails.
            PipelineError: If models not loaded.
        """
        if not self.is_loaded():
            raise PipelineError(
                "Models not loaded. Call load() first.",
                user_message="Pipeline not ready. Please initialize models first.",
            )

        self._validate_generation_config(config)
        self._check_memory_requirements(config)

        try:
            memory_before = self.memory_manager.get_memory_stats()

            # Encode prompt
            prompt_embeddings = self.clip_manager.encode_text(config.prompt)
            negative_embeddings = (
                self.clip_manager.encode_text(config.negative_prompt)
                if config.negative_prompt
                else None
            )

            # Generate frames
            frames = self._generate_frames(
                config, prompt_embeddings, negative_embeddings
            )

            memory_after = self.memory_manager.get_memory_stats()

            metadata = {
                "fps": config.fps,
                "height": config.height,
                "width": config.width,
                "num_frames": len(frames),
                "sampler": config.sampler,
                "scheduler": config.scheduler,
                "num_inference_steps": config.num_inference_steps,
                "seed": config.seed,
                "memory_before_mb": memory_before.get("allocated_mb", 0),
                "memory_after_mb": memory_after.get("allocated_mb", 0),
            }

            return GenerationResult(frames=frames, metadata=metadata, generation_config=config)

        except Exception as e:
            if isinstance(e, GenerationError):
                raise
            raise GenerationError(
                f"Generation failed: {str(e)}",
                user_message="Video generation failed. Please try again with different parameters.",
            )

    async def generate_async(self, config: GenerationConfig) -> GenerationResult:
        """Generate video frames (asynchronous).

        Args:
            config: Generation configuration.

        Returns:
            GenerationResult with frames and metadata.

        Raises:
            GenerationError: If generation fails.
            PipelineError: If models not loaded.
        """
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, self.generate, config)

    def _generate_frames(
        self,
        config: GenerationConfig,
        prompt_embeddings: torch.Tensor,
        negative_embeddings: Optional[torch.Tensor],
        num_frames: int = 8,
    ) -> List[torch.Tensor]:
        """Generate frame sequence.

        Args:
            config: Generation configuration.
            prompt_embeddings: Encoded prompt embeddings.
            negative_embeddings: Encoded negative prompt embeddings.
            num_frames: Number of frames to generate.

        Returns:
            List of frame tensors.
        """
        frames = []

        # Initialize latent code
        latent = torch.randn(
            1, 4, config.height // 8, config.width // 8, device=self.device
        )

        # Diffusion loop (placeholder)
        for step in range(config.num_inference_steps):
            timestep = int((1 - step / config.num_inference_steps) * 1000)

            # Denoise latent
            denoised = self.unet_manager.denoise(
                latent,
                timestep,
                prompt_embeddings,
                guidance_scale=config.clip_guidance_scale,
            )

            # Update latent (placeholder for actual scheduler)
            latent = denoised

        # Decode latent to frames
        for i in range(num_frames):
            # Decode current latent state
            frame = self.vae_manager.decode(latent)
            # Normalize to [0, 1]
            frame = (frame + 1) / 2
            frame = torch.clamp(frame, 0, 1)
            frames.append(frame)

        return frames

    def __enter__(self):
        """Context manager entry."""
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.unload()
