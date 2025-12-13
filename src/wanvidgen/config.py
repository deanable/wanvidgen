"""
Configuration management for WanVidGen application.

Handles loading and managing configuration from environment variables
and configuration files.
"""

import os
from typing import Optional, Dict, Any
from dataclasses import dataclass, field

# Optional imports - handle gracefully during bootstrap
try:
    from dotenv import load_dotenv
    HAS_DOTENV = True
except ImportError:
    HAS_DOTENV = False
    load_dotenv = lambda: None  # Placeholder function

# Load environment variables from .env file if it exists
if HAS_DOTENV:
    load_dotenv()


@dataclass
class ModelConfig:
    """Configuration for model settings."""
    model_path: str = ""
    model_name: str = ""
    precision: str = "Q5"  # Q5, Q6, FP16, FP32
    device: str = "auto"  # auto, cpu, cuda, mps
    gpu_id: Optional[int] = None
    context_length: int = 2048
    max_tokens: int = 512


@dataclass
class OutputConfig:
    """Configuration for output settings."""
    output_dir: str = "./outputs"
    video_format: str = "mp4"
    fps: int = 30
    width: int = 1024
    height: int = 576
    quality: str = "high"  # low, medium, high, ultra
    compression: str = "medium"  # none, low, medium, high


@dataclass
class PipelineConfig:
    """Configuration for pipeline settings."""
    batch_size: int = 1
    num_workers: int = 4
    prefetch_factor: int = 2
    pin_memory: bool = True
    persistent_workers: bool = False
    timeout: int = 30


@dataclass
class LoggingConfig:
    """Configuration for logging settings."""
    level: str = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    file_logging: bool = False
    log_file: str = "./logs/wanvidgen.log"
    console_logging: bool = True


@dataclass
class Config:
    """Main configuration class."""
    model: ModelConfig = field(default_factory=ModelConfig)
    output: OutputConfig = field(default_factory=OutputConfig)
    pipeline: PipelineConfig = field(default_factory=PipelineConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    # Additional settings
    debug: bool = False
    gui_enabled: bool = True
    env_file: Optional[str] = None
    
    def __post_init__(self):
        """Initialize configuration from environment variables."""
        self._load_from_env()
    
    def _load_from_env(self):
        """Load configuration values from environment variables."""
        # Model configuration
        self.model.model_path = os.getenv("WANVIDGEN_MODEL_PATH", "")
        self.model.model_name = os.getenv("WANVIDGEN_MODEL_NAME", "")
        self.model.precision = os.getenv("WANVIDGEN_PRECISION", "Q5")
        self.model.device = os.getenv("WANVIDGEN_DEVICE", "auto")
        self.model.gpu_id = int(os.getenv("WANVIDGEN_GPU_ID", "-1")) if os.getenv("WANVIDGEN_GPU_ID") else None
        self.model.context_length = int(os.getenv("WANVIDGEN_CONTEXT_LENGTH", "2048"))
        self.model.max_tokens = int(os.getenv("WANVIDGEN_MAX_TOKENS", "512"))
        
        # Output configuration
        self.output.output_dir = os.getenv("WANVIDGEN_OUTPUT_DIR", "./outputs")
        self.output.video_format = os.getenv("WANVIDGEN_VIDEO_FORMAT", "mp4")
        self.output.fps = int(os.getenv("WANVIDGEN_FPS", "30"))
        self.output.width = int(os.getenv("WANVIDGEN_WIDTH", "1024"))
        self.output.height = int(os.getenv("WANVIDGEN_HEIGHT", "576"))
        self.output.quality = os.getenv("WANVIDGEN_QUALITY", "high")
        self.output.compression = os.getenv("WANVIDGEN_COMPRESSION", "medium")
        
        # Pipeline configuration
        self.pipeline.batch_size = int(os.getenv("WANVIDGEN_BATCH_SIZE", "1"))
        self.pipeline.num_workers = int(os.getenv("WANVIDGEN_NUM_WORKERS", "4"))
        self.pipeline.prefetch_factor = int(os.getenv("WANVIDGEN_PREFETCH_FACTOR", "2"))
        self.pipeline.pin_memory = os.getenv("WANVIDGEN_PIN_MEMORY", "true").lower() == "true"
        self.pipeline.persistent_workers = os.getenv("WANVIDGEN_PERSISTENT_WORKERS", "false").lower() == "true"
        self.pipeline.timeout = int(os.getenv("WANVIDGEN_TIMEOUT", "30"))
        
        # Logging configuration
        self.logging.level = os.getenv("WANVIDGEN_LOG_LEVEL", "INFO")
        self.logging.format = os.getenv("WANVIDGEN_LOG_FORMAT", "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        self.logging.file_logging = os.getenv("WANVIDGEN_FILE_LOGGING", "false").lower() == "true"
        self.logging.log_file = os.getenv("WANVIDGEN_LOG_FILE", "./logs/wanvidgen.log")
        self.logging.console_logging = os.getenv("WANVIDGEN_CONSOLE_LOGGING", "true").lower() == "true"
        
        # Additional settings
        self.debug = os.getenv("WANVIDGEN_DEBUG", "false").lower() == "true"
        self.gui_enabled = os.getenv("WANVIDGEN_GUI_ENABLED", "true").lower() == "true"
        self.env_file = os.getenv("WANVIDGEN_ENV_FILE")
    
    def validate(self) -> bool:
        """Validate configuration settings."""
        # TODO: Implement validation logic
        return True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        return {
            "model": self.model.__dict__,
            "output": self.output.__dict__,
            "pipeline": self.pipeline.__dict__,
            "logging": self.logging.__dict__,
            "debug": self.debug,
            "gui_enabled": self.gui_enabled,
            "env_file": self.env_file,
        }


def load_config(env_file: Optional[str] = None) -> Config:
    """Load configuration from environment variables."""
    if env_file:
        load_dotenv(env_file)
    return Config()


# Global configuration instance
_config = None


def get_config() -> Config:
    """Get the global configuration instance."""
    global _config
    if _config is None:
        _config = Config()
    return _config


def set_config(config: Config):
    """Set the global configuration instance."""
    global _config
    _config = config