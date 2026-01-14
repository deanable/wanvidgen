"""
Utility functions for WanVidGen.

This module re-exports utilities from the utils package for backward compatibility.
"""

import os
import sys
import platform
import logging
from pathlib import Path
from typing import Dict, Any, Optional

# Re-export from utils package
from .utils.core import (
    get_system_info,
    check_dependencies,
    format_file_size,
    sanitize_filename,
)
from .utils.memory import (
    torch_available,
    cuda_available,
    mps_available,
    best_device,
)

logger = logging.getLogger(__name__)

def ensure_model_availability(config) -> bool:
    """
    Check if model exists, download if missing.
    
    Args:
        config: Configuration object containing model settings.
        
    Returns:
        bool: True if model is available (exists or downloaded), False otherwise.
    """
    # Determine target path
    if config.model.model_path:
        model_path = Path(config.model.model_path)
    else:
        # Default location
        models_dir = Path("models")
        models_dir.mkdir(exist_ok=True)
        # Default filename if not specified
        filename = "Self-Forcing2.1-T2V-1.3B-F16.gguf"
        model_path = models_dir / filename
        config.model.model_path = str(model_path)

    if model_path.exists():
        logger.info(f"Model found at {model_path}")
        return True
        
    print(f"⚠️  Model not found at {model_path}")
    print("Attempting to download from Hugging Face...")
    
    try:
        from huggingface_hub import hf_hub_download  # type: ignore
        
        # Default repo if not specified in config
        repo_id = config.model.model_name or "Nichonauta/Self-Forcing2.1-T2V-1.3B-GGUF"
        filename = model_path.name
        
        print(f"Downloading {filename} from {repo_id}...")
        
        downloaded_path = hf_hub_download(
            repo_id=repo_id,
            filename=filename,
            local_dir=str(model_path.parent),
        )
        
        print(f"✓ Model downloaded successfully to {downloaded_path}")
        return True
        
    except ImportError:
        logger.error("huggingface_hub not installed.")
        print("❌ huggingface_hub not installed. Please install it to download models:")
        print("   pip install huggingface_hub")
        return False
    except Exception as e:
        logger.error(f"Failed to download model: {e}")
        print(f"❌ Failed to download model: {e}")
        if "401" in str(e):
            print("\n💡 This repository might be gated. Please run 'huggingface-cli login' or set HF_TOKEN environment variable.")
        return False