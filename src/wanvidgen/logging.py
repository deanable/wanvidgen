"""Structured logging configuration for wanvidgen.

Provides JSON/key-value structured logging with console and rotating file handlers.
Each module should obtain a child logger via get_logger(__name__).
"""

from __future__ import annotations

import json
from datetime import datetime
import logging
import logging.handlers
import sys
from pathlib import Path
from typing import Any


class StructuredFormatter(logging.Formatter):
    """Formatter that outputs structured log records.
    
    Outputs either JSON or key-value format depending on configuration.
    """
    
    def __init__(self, fmt_type: str = "json", *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.fmt_type = fmt_type.lower()
    
    def format(self, record: logging.LogRecord) -> str:
        log_data = {
            "timestamp": self.formatTime(record, self.datefmt),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }
        
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        extra_fields = getattr(record, "extra_fields", None)
        if extra_fields:
            log_data.update(extra_fields)
        
        if self.fmt_type == "json":
            return json.dumps(log_data)
        else:
            pairs = [f"{k}={v}" for k, v in log_data.items()]
            return " ".join(pairs)


class LogConfig:
    """Configuration for logging setup."""
    
    def __init__(
        self,
        log_dir: str | Path = "logs",
        log_level: str = "INFO",
        fmt_type: str = "json",
        max_bytes: int = 10 * 1024 * 1024,  # 10 MB
        backup_count: int = 5,
        console_output: bool = True,
        file_output: bool = True,
    ) -> None:
        self.log_dir = Path(log_dir)
        self.log_level = getattr(logging, log_level.upper(), logging.INFO)
        self.fmt_type = fmt_type
        self.max_bytes = max_bytes
        self.backup_count = backup_count
        self.console_output = console_output
        self.file_output = file_output


_configured = False
_log_config: LogConfig | None = None


def configure_logging(config: LogConfig | None = None) -> None:
    """Configure the root logger with structured logging handlers.
    
    Args:
        config: LogConfig instance. If None, uses default configuration.
    
    Sets up:
    - Console handler (stdout) with structured formatting
    - Rotating file handler in logs/ directory
    - Appropriate log levels for all handlers
    """
    global _configured, _log_config
    
    if _configured:
        return
    
    if config is None:
        config = LogConfig()
    
    _log_config = config
    
    root_logger = logging.getLogger()
    root_logger.setLevel(config.log_level)
    
    root_logger.handlers.clear()
    
    formatter = StructuredFormatter(fmt_type=config.fmt_type)
    
    if config.console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(config.log_level)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)
    
    if config.file_output:
        config.log_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = config.log_dir / f"{timestamp}.log"
        
        file_handler = logging.handlers.RotatingFileHandler(
            log_file,
            maxBytes=config.max_bytes,
            backupCount=config.backup_count,
            encoding="utf-8",
        )
        file_handler.setLevel(config.log_level)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
        
        # Create symlink to latest log
        latest_log = config.log_dir / "latest.log"
        try:
            if latest_log.exists() or latest_log.is_symlink():
                latest_log.unlink()
            latest_log.symlink_to(log_file.name)
        except OSError:
            # Symlinks might not be supported on Windows without admin rights
            # We skip creating the link in that case
            pass
    
    _configured = True
    
    root_logger.info("Logging configured", extra={"extra_fields": {
        "log_dir": str(config.log_dir),
        "log_level": logging.getLevelName(config.log_level),
        "fmt_type": config.fmt_type,
    }})


def get_logger(name: str) -> logging.Logger:
    """Get a child logger for a module.
    
    Args:
        name: Logger name, typically __name__ from the calling module.
    
    Returns:
        A logger instance that inherits from the configured root logger.
    
    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing started")
    """
    if not _configured:
        configure_logging()
    
    return logging.getLogger(name)


def set_log_level(level: str | int) -> None:
    """Change the log level for all handlers.
    
    Args:
        level: Log level as string (DEBUG, INFO, WARNING, ERROR) or int.
    """
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    for handler in root_logger.handlers:
        handler.setLevel(level)


def log_exception(logger: logging.Logger, message: str, exc: Exception) -> None:
    """Log an exception with full traceback.
    
    Args:
        logger: Logger instance.
        message: Descriptive message.
        exc: Exception to log.
    """
    logger.error(message, exc_info=exc)
