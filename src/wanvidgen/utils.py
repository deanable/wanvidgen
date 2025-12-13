"""
Utility functions for WanVidGen.
"""

import os
import sys
import platform
import logging
from pathlib import Path
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

def get_system_info() -> Dict[str, Any]:
    """Get system information."""
    info: Dict[str, Any] = {
        "os": platform.system(),
        "os_release": platform.release(),
        "python_version": sys.version.split()[0],
        "processor": platform.processor(),
    }
    try:
        import psutil  # type: ignore
        info["ram_total_gb"] = round(psutil.virtual_memory().total / (1024**3), 2)
    except ImportError:
        info["ram_total_gb"] = "Unknown (psutil not installed)"
        
    return info

def check_dependencies() -> Dict[str, bool]:
    """Check for required dependencies."""
    dependencies = {
        "torch": False,
        "numpy": False,
        "PIL": False,  # Pillow
        "huggingface_hub": False,
    }
    
    for dep in dependencies:
        try:
            __import__(dep)
            dependencies[dep] = True
        except ImportError:
            dependencies[dep] = False
            
    return dependencies

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