#!/usr/bin/env python3
"""Test key-value format for logging."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from wanvidgen.logging import configure_logging, get_logger, LogConfig

# Configure with key-value format
configure_logging(LogConfig(
    log_dir="logs",
    log_level="INFO",
    fmt_type="key-value",
))

logger = get_logger(__name__)

print("Testing key-value format:")
logger.info("This is an INFO message")
logger.warning("This is a WARNING message")
logger.info("Message with extras", extra={"extra_fields": {
    "key1": "value1",
    "key2": 42,
}})

print("\nKey-value format test complete!")
