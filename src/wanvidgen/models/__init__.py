"""Model managers for WanVidGen."""

from .main_model_manager import ModelManager, create_model_manager

# Optional imports - may not be available if torch is not installed
try:
    from .clip_manager import CLIPManager
    from .vae_manager import VAEManager
    from .unet_manager import UNetManager
    __all__ = ["CLIPManager", "VAEManager", "UNetManager", "ModelManager", "create_model_manager"]
except ImportError:
    __all__ = ["ModelManager", "create_model_manager"]
