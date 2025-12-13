"""Base manager for model lifecycle management."""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional
import torch
from ..exceptions import ModelLoadError, ConfigError


class BaseModelManager(ABC):
    """Base class for model managers handling GGUF weights and lifecycle."""

    def __init__(
        self,
        config_path: str | Path,
        device: str = "cuda",
        quantization: Optional[str] = None,
    ):
        """Initialize base model manager.

        Args:
            config_path: Path to model config or weights.
            device: Device to load model on ("cuda" or "cpu").
            quantization: Quantization format (e.g., "q5", "q6", None for full precision).

        Raises:
            ConfigError: If config_path is invalid.
        """
        self.config_path = Path(config_path)
        self.device = device
        self.quantization = quantization
        self.model = None
        self._validate_config()

    def _validate_config(self) -> None:
        """Validate config path exists.

        Raises:
            ConfigError: If config path doesn't exist.
        """
        if not self.config_path.exists():
            raise ConfigError(
                f"Model config/weights not found: {self.config_path}",
                user_message=f"Model file not found: {self.config_path}",
            )

    @abstractmethod
    def load(self) -> None:
        """Load model weights. Must be implemented by subclasses."""
        pass

    @abstractmethod
    def unload(self) -> None:
        """Unload model weights. Must be implemented by subclasses."""
        pass

    def is_loaded(self) -> bool:
        """Check if model is loaded.

        Returns:
            True if model is loaded, False otherwise.
        """
        return self.model is not None

    def move_to_device(self) -> None:
        """Move model to specified device."""
        if self.model is None:
            raise ModelLoadError("Cannot move unloaded model to device")
        self.model.to(self.device)

    def get_model(self):
        """Get loaded model.

        Returns:
            Model instance.

        Raises:
            ModelLoadError: If model not loaded.
        """
        if self.model is None:
            raise ModelLoadError(f"{self.__class__.__name__} model not loaded")
        return self.model

    def __enter__(self):
        """Context manager entry."""
        self.load()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.unload()
