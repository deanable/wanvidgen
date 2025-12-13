# WanVidGen - Video Generation Utilities

A Python package for video generation with structured logging and comprehensive output handling.

## Features

### Logging (`wanvidgen/logging.py`)

Structured logging with JSON or key-value formatting:

- **Log Levels**: DEBUG, INFO, WARNING, ERROR
- **Dual Output**: Console (stdout) and rotating file handlers
- **Structured Format**: JSON-formatted logs with timestamps and metadata
- **Child Loggers**: Each module gets its own logger instance
- **Rotating Files**: Automatic log rotation (10MB max, 5 backups)
- **Configurable**: Log directory, level, and format type

#### Usage

```python
from wanvidgen.logging import configure_logging, get_logger, LogConfig

# Configure logging (optional, uses defaults if not called)
configure_logging(LogConfig(
    log_dir="logs",
    log_level="INFO",
    fmt_type="json"
))

# Get a logger for your module
logger = get_logger(__name__)

# Log messages
logger.info("Processing started")
logger.warning("Resource usage high")
logger.error("Operation failed", exc_info=True)

# Log with extra fields
logger.info("Generation complete", extra={"extra_fields": {
    "frames": 120,
    "duration": 4.0
}})
```

### Output Handlers (`wanvidgen/output/handlers.py`)

Utilities to persist generated video sequences in multiple formats:

- **Video Formats**: MP4, WEBM (via moviepy)
- **Animation**: WEBP animations
- **Frame Dumps**: Individual PNG frames
- **Organization**: Timestamped directories for each generation
- **Metadata**: JSON manifest with parameters
- **Error Handling**: Graceful fallback when encoders are missing

#### Usage

```python
import numpy as np
from wanvidgen.output import save_generation

# Create or load your frames (H, W, C) with values 0-255
frames = np.random.randint(0, 255, (30, 256, 256, 3), dtype=np.uint8)

# Generation metadata
metadata = {
    "prompt": "a beautiful sunset",
    "model": "model_v1",
    "seed": 42,
    "steps": 50
}

# Save in all available formats
saved_files = save_generation(
    frames=frames,
    metadata=metadata,
    formats=["png", "webp", "mp4", "webm"],
    fps=30
)

# Result: outputs/{timestamp}/
#   - manifest.json
#   - frames/frame_0000.png, frame_0001.png, ...
#   - animation.webp
#   - video.mp4
#   - video.webm
```

#### Individual Format Handlers

```python
from pathlib import Path
from wanvidgen.output import (
    create_output_directory,
    save_frames_as_png,
    save_as_webp,
    save_as_video,
    save_metadata
)

# Create timestamped output directory
output_dir = create_output_directory("my_outputs")

# Save metadata
save_metadata(output_dir, {"prompt": "test", "seed": 123})

# Save PNG frames
png_paths = save_frames_as_png(frames, output_dir, prefix="frame")

# Save WEBP animation
webp_path = output_dir / "animation.webp"
save_as_webp(frames, webp_path, fps=30)

# Save video
mp4_path = output_dir / "video.mp4"
save_as_video(frames, mp4_path, fps=30, codec="libx264")
```

#### Error Handling

The output handlers gracefully handle missing encoders:

```python
from wanvidgen.output import save_as_video, EncoderMissingError

try:
    save_as_video(frames, output_path, fps=30)
except EncoderMissingError as e:
    print(f"Video encoder not available: {e}")
    # Fall back to PNG frames or WEBP
```

## Installation

### Dependencies

```bash
pip install numpy Pillow moviepy
```

### Optional Dependencies

- **moviepy**: Required for MP4/WEBM video export
- **Pillow with WEBP support**: Required for WEBP animations (usually included)

## Development

### Running Tests

```bash
python test_logging_output.py
```

This will:
1. Test logging to console and file
2. Create dummy frames
3. Save in all formats (PNG, WEBP, MP4, WEBM)
4. Verify files are created

### Project Structure

```
wanvidgen/
├── __init__.py
├── logging.py              # Structured logging configuration
└── output/
    ├── __init__.py
    └── handlers.py         # Output format handlers
```

## Log Output Example

Console and file logs are identical (JSON format):

```json
{"timestamp": "2025-12-13 17:01:11,342", "level": "INFO", "logger": "wanvidgen.output.handlers", "message": "Saved WEBP animation", "path": "outputs/20251213_170111/animation.webp", "frames": 30, "fps": 30}
```

## Directory Structure

Each generation creates a timestamped directory:

```
outputs/
└── 20251213_170111/
    ├── manifest.json       # Generation metadata
    ├── frames/             # Individual PNG frames
    │   ├── frame_0000.png
    │   ├── frame_0001.png
    │   └── ...
    ├── animation.webp      # WEBP animation
    ├── video.mp4           # MP4 video
    └── video.webm          # WEBM video
```

## License

This project is part of WanVidGen.
