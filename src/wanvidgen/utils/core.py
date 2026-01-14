"""
Core utility functions for WanVidGen.

Common utility functions for system information, dependency checking,
and other shared functionality.
"""

import logging
from typing import Dict, Any, Optional, Tuple, Union, List
from pathlib import Path
import platform
import sys

logger = logging.getLogger(__name__)


def get_system_info() -> Dict[str, Any]:
    """Get basic system information."""
    info: Dict[str, Any] = {
        "platform": platform.platform(),
        "system": platform.system(),
        "os_release": platform.release(),
        "machine": platform.machine(),
        "python_version": platform.python_version(),
        "processor": platform.processor(),
    }
    try:
        import psutil  # type: ignore
        info["ram_total_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        info["ram_total_gb"] = "Unknown (psutil not installed)"
    return info


def detect_gpu_device() -> Optional[Dict[str, Any]]:
    """Detect GPU availability (placeholder)."""
    return {"gpu_available": False, "device": "cpu"}


def select_optimal_device(preferred_device: str = "auto") -> str:
    """Select optimal device for computation."""
    return "cpu"  # Placeholder


def check_dependencies() -> Dict[str, bool]:
    """Check if dependencies are available."""
    dependencies = {
        "torch": False,
        "numpy": False,
        "PIL": False,  # Pillow
        "customtkinter": False,
        "dotenv": False,  # python-dotenv
        "moviepy": False,
        "imageio": False,
        "huggingface_hub": False,
    }

    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False

    return dependencies


def setup_logging(config: Dict[str, Any]) -> None:
    """Setup logging configuration."""
    log_level = getattr(logging, config.get("level", "INFO").upper())
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=config.get("format", "%(asctime)s - %(name)s - %(levelname)s - %(message)s"),
        handlers=[logging.StreamHandler(sys.stdout)]
    )


def validate_config(config: Dict[str, Any]) -> Tuple[bool, List[str]]:
    """Validate configuration (placeholder)."""
    errors = []
    return len(errors) == 0, errors


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"


def sanitize_filename(filename: str) -> str:
    """Sanitize filename for cross-platform compatibility."""
    # Remove or replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing dots and spaces
    filename = filename.strip('. ')
    
    return filename