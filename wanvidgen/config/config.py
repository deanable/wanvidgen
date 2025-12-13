"""
Configuration management for WanVidGen
"""

import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class Config:
    """Configuration manager for WanVidGen"""
    
    def __init__(self, config_file: str = "wanvidgen_config.json"):
        self.config_file = Path(config_file)
        self.default_config = {
            # Generation parameters
            "prompt": "",
            "negative_prompt": "",
            "sampler": "euler_ancestral",
            "scheduler": "simple", 
            "quantization": "q5",
            "steps": 20,
            "fps": 8,
            "resolution": 512,
            
            # GUI settings
            "output_directory": "output",
            "window_width": 1200,
            "window_height": 800,
            "theme": "dark",
            
            # Available options
            "available_samplers": [
                "euler_ancestral",
                "lms", 
                "heun",
                "dpm2",
                "dpm2_ancestral",
                "midpoint"
            ],
            "available_schedulers": [
                "simple",
                "karras",
                "normalized"
            ],
            "available_quantizations": [
                "q5",
                "q6"
            ],
            "available_resolutions": [
                512,
                768,
                1024
            ],
            "available_fps": [
                4,
                8,
                12,
                16,
                24
            ]
        }
        self.config = self.default_config.copy()
        self.load()
    
    def load(self) -> bool:
        """Load configuration from file"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                # Merge with defaults to handle new options
                self.config.update(self.default_config)
                self.config.update(loaded_config)
                return True
        except Exception as e:
            print(f"Failed to load config: {e}")
        
        return False
    
    def save(self) -> bool:
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            return True
        except Exception as e:
            print(f"Failed to save config: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value"""
        self.config[key] = value
    
    def get_all(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self.config.copy()
    
    def reset_to_defaults(self) -> None:
        """Reset configuration to defaults"""
        self.config = self.default_config.copy()
        self.save()