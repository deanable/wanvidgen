#!/usr/bin/env python3
"""Test custom log directory configuration."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from wanvidgen.log_config import configure_logging, get_logger, LogConfig

# Test custom log directory
custom_log_dir = Path("custom_logs")

configure_logging(LogConfig(
    log_dir=custom_log_dir,
    log_level="INFO",
    fmt_type="json",
))

logger = get_logger(__name__)
logger.info("Testing custom log directory")

log_file = custom_log_dir / "wanvidgen.log"
if log_file.exists():
    print(f"✓ Log file created at: {log_file}")
else:
    print(f"✗ Log file not found at: {log_file}")
