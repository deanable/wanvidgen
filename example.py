#!/usr/bin/env python3
"""Example usage of wanvidgen log_config and output handlers."""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent / "src"))

from wanvidgen.log_config import configure_logging, get_logger, LogConfig
from wanvidgen.output import save_generation


def main():
    configure_logging(LogConfig(
        log_dir="logs",
        log_level="INFO",
        fmt_type="json",
    ))
    
    logger = get_logger(__name__)
    logger.info("Starting example generation")
    
    frames = np.random.randint(0, 255, (10, 128, 128, 3), dtype=np.uint8)
    logger.info(f"Generated {len(frames)} random frames")
    
    metadata = {
        "prompt": "example generation",
        "model": "random_v1",
        "seed": 42,
        "steps": 10,
    }
    
    logger.info("Saving generation...")
    saved_files = save_generation(
        frames=frames,
        metadata=metadata,
        formats=["png", "webp", "mp4"],
        fps=10
    )
    
    logger.info("Generation complete", extra={"extra_fields": {
        "saved_files": list(saved_files.keys()),
    }})
    
    print("\nSaved files:")
    for fmt, path in saved_files.items():
        print(f"  {fmt}: {path}")


if __name__ == "__main__":
    main()
