"""
Wan2.1 GGUF Video Generation Application

A modern video generation application built with PyTorch, CustomTkinter,
and support for GGUF quantized models.
"""

__version__ = "0.1.0"
__author__ = "WanVidGen Team"
__email__ = "team@wanvidgen.dev"

# Import main components for easy access
try:
    from .config import Config, load_config
    from .main import main
except ImportError:
    # During initial bootstrap, these modules might not be fully implemented
    pass

__all__ = [
    "__version__",
    "__author__", 
    "__email__",
]
