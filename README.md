# WanVidGen

A CustomTkinter GUI application for video generation with real-time progress monitoring and comprehensive logging.

## Features

- **Modern GUI**: Built with CustomTkinter for a clean, modern interface
- **Real-time Progress**: Progress bars and status updates during generation
- **Comprehensive Logging**: Live console with color-coded log messages
- **Flexible Configuration**: Save/load settings, customizable parameters
- **Threaded Generation**: Non-blocking UI during video generation
- **Error Handling**: User-friendly error dialogs and comprehensive logging
- **GPU Memory Management**: Option to clear GPU memory between runs

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Install WanVidGen (Development Mode)

```bash
pip install -e .
```

This installs the package in development mode, allowing you to run it directly.

## Usage

### Command Line

Run the application using the command line:

```bash
python -m wanvidgen
```

Or after installation:

```bash
wanvidgen
```

### Running from Source

```bash
python wanvidgen/main.py
```

### GUI Application

The application opens with a modern dark-themed interface containing:

1. **Generation Tab**: Main interface for configuring and running video generation
2. **Settings Tab**: Appearance and configuration management
3. **Console Tab**: Real-time log output and console

### Configuration Options

#### Generation Parameters
- **Prompt**: Text description for video generation
- **Negative Prompt**: What to avoid in generation
- **Sampler**: Algorithm for sampling (euler_ancestral, lms, heun, etc.)
- **Scheduler**: Step scheduling method (simple, karras, normalized)
- **Quantization**: Model quantization level (q5, q6)
- **Steps**: Number of generation steps (10-50)
- **FPS**: Frames per second (4-24)
- **Resolution**: Output resolution (512, 768, 1024)
- **Output Directory**: Where to save generated videos

#### GUI Settings
- **Theme**: Dark or light appearance
- **Window Size**: Configurable window dimensions

## Architecture

### Core Components

1. **Main Application** (`wanvidgen/main.py`): Entry point, logging, error handling
2. **GUI Application** (`wanvidgen/gui/app.py`): CustomTkinter interface, event handling
3. **Generation Pipeline** (`wanvidgen/pipeline/pipeline.py`): Core generation logic
4. **Configuration Manager** (`wanvidgen/config/config.py`): Settings persistence

### Key Features Implementation

- **Threading**: Generation runs in separate thread to keep UI responsive
- **Progress Callbacks**: Real-time progress updates via queue-based communication
- **Error Handling**: Comprehensive exception handling with user-friendly messages
- **Logging**: Dual logging to file and console with configurable levels
- **Configuration**: JSON-based settings with defaults and validation

## Development

### Project Structure

```
wanvidgen/
├── __init__.py
├── __main__.py
├── main.py                 # Entry point
├── gui/
│   ├── __init__.py
│   └── app.py             # Main GUI application
├── pipeline/
│   ├── __init__.py
│   └── pipeline.py        # Generation pipeline
└── config/
    ├── __init__.py
    └── config.py          # Configuration management
```

### Adding New Features

1. **New Parameters**: Add to `config.py` defaults and update GUI form in `app.py`
2. **Pipeline Changes**: Modify `pipeline.py` generation logic
3. **UI Enhancements**: Extend `app.py` GUI components and event handlers

### Running Tests

```bash
python -m pytest tests/
```

### Code Style

- Follow PEP 8 Python style guidelines
- Use type hints for function parameters and return values
- Document all public methods and classes
- Add comprehensive error handling

## Current Status

This is a **simulation/stub implementation** that demonstrates the GUI structure and user interface workflow. The generation pipeline currently simulates video generation with progress updates rather than performing actual video generation.

### What Works

- ✅ CustomTkinter GUI with tabbed interface
- ✅ Form fields for all generation parameters
- ✅ Real-time progress bars and status updates
- ✅ Live console logging with color coding
- ✅ Configuration save/load functionality
- ✅ Threaded generation with cancel support
- ✅ Error dialogs and exception handling
- ✅ Menu system with file operations
- ✅ GPU memory clearing simulation
- ✅ Output path display and file creation

### Next Steps (Future Development)

- 🔄 Integrate actual video generation models
- 🔄 Add video preview and playback
- 🔄 Implement batch processing
- 🔄 Add preset configurations
- 🔄 Include model downloading and management
- 🔄 Add support for custom model paths

## Dependencies

### Core Dependencies
- **customtkinter**: ModernTkinter widgets with styling
- **Pillow**: Image processing capabilities

### Optional Dependencies (Future)
- **torch**: Deep learning framework for models
- **diffusers**: Hugging Face diffusion models
- **transformers**: Transformer models for NLP
- **torchvision**: Computer vision utilities

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **CustomTkinter**: For the modern, customizable GUI framework
- **Python Community**: For the excellent ecosystem of libraries
- **Tkinter**: For the underlying GUI toolkit

## Support

For issues, questions, or contributions, please visit the [GitHub repository](https://github.com/your-org/wanvidgen) or open an issue.