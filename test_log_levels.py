#!/usr/bin/env python3
"""Quick test to verify DEBUG level logging works."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from wanvidgen.logging import configure_logging, get_logger, LogConfig, set_log_level

# Configure with DEBUG level
configure_logging(LogConfig(
    log_dir="logs",
    log_level="DEBUG",
    fmt_type="json",
))

logger = get_logger(__name__)

print("Testing all log levels:")
logger.debug("This is a DEBUG message - should be visible")
logger.info("This is an INFO message")
logger.warning("This is a WARNING message")
logger.error("This is an ERROR message")

print("\nChanging to WARNING level...")
set_log_level("WARNING")

logger.debug("This DEBUG message should NOT appear")
logger.info("This INFO message should NOT appear")
logger.warning("This WARNING message SHOULD appear")
logger.error("This ERROR message SHOULD appear")

print("\nLog level test complete!")
