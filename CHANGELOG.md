# Changelog

All notable changes to WanVidGen will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-14

### Added
- Initial release with basic functionality
- GGUF model support via llama-cpp-python
- GUI and CLI interfaces for video generation
- Configuration management via environment variables
- Structured logging with JSON and key-value formats
- Output handlers for MP4, WEBM, WEBP, and PNG formats
- Timestamped output directories with metadata manifests
- Multi-device support (CPU, CUDA, MPS)
- Automatic model downloading from Hugging Face
- System compatibility checking

### Fixed
- **Logging Module Collision**: Renamed `logging.py` to `log_config.py` to avoid shadowing Python's standard library
  - Updated all imports in main.py, output/handlers.py, and test files
  - No functional changes, only import paths changed
  - Breaking change for external code importing from `wanvidgen.logging`

### Changed
- Streamlined output management by consolidating duplicate modules
- Improved error handling with graceful fallbacks
- Enhanced GUI with real-time preview and progress tracking

## [Unreleased]

### Planned
- Real video model integration beyond simulation
- Additional model backend support
- Batch generation capabilities
- Video editing and post-processing features
- Cloud storage integration
