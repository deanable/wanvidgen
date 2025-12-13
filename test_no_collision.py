#!/usr/bin/env python3
"""Test that there's no module name collision between standard logging and log_config."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

# Import standard library logging first
import logging

# Import our custom log_config module
from wanvidgen.log_config import configure_logging, get_logger, LogConfig

# Test standard library logging
print("Testing standard library logging...")
std_logger = logging.getLogger("standard_test")
std_logger.info("Standard library logging works!")

# Test our custom logging
print("\nTesting custom log_config...")
configure_logging(LogConfig(
    log_dir="logs",
    log_level="INFO",
    fmt_type="json",
    console_output=True,
    file_output=False,
))

custom_logger = get_logger("custom_test")
custom_logger.info("Custom log_config works!")

print("\n✓ SUCCESS: No module name collision detected!")
print("✓ Both standard library logging and wanvidgen.log_config work correctly")
