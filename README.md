# WanVidGen

WanVidGen is a modern video generation application built with PyTorch and CustomTkinter, designed to work with GGUF quantized models for efficient video generation.

## Features

- **GGUF Model Support**: Compatible with GGUF quantized models for memory-efficient inference
- **Modern GUI**: Clean, intuitive interface built with CustomTkinter
- **Flexible Configuration**: Comprehensive environment variable configuration
- **Multiple Device Support**: CPU, CUDA (NVIDIA GPU), and MPS (Apple Silicon)
- **Video Pipeline**: Modular pipeline for text-to-video generation
- **Output Management**: Organized output saving with metadata tracking

## Installation

### Prerequisites

- Python 3.8 or higher
- PyTorch 2.0.0 or higher
- CUDA-compatible GPU (optional, for GPU acceleration)

### Install Dependencies

```bash
pip install -e .
```

Or install with development dependencies:

```bash
pip install -e ".[dev]"
```

### Environment Setup

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` to configure your settings:
- Set model path and name
- Configure device and precision settings
- Adjust video output parameters
- Customize logging and performance settings

## Quick Start

### Run the Application

The application can be started in several ways:

#### GUI Mode (Recommended)
```bash
python -m wanvidgen --gui
```

#### Command Line Generation
```bash
python -m wanvidgen --generate "A sunset over mountains"
```

#### Check System Compatibility
```bash
python -m wanvidgen --check-system
```

#### List Models
```bash
python -m wanvidgen --list-models
```

### Command Line Options

```bash
# Full command line reference
python -m wanvidgen --help

# Generate video with custom settings
python -m wanvidgen --generate "Your prompt here" \
    --model-path ./models/your_model.gguf \
    --device cuda \
    --precision Q5 \
    --output-dir ./my_outputs \
    --width 1024 --height 576 --fps 30

# Start GUI with custom config
python -m wanvidgen --gui --config custom_config.yaml
```

## Configuration

### Environment Variables

The application uses environment variables for configuration. Key categories:

#### Model Configuration
- `WANVIDGEN_MODEL_PATH`: Path to model file
- `WANVIDGEN_MODEL_NAME`: Model identifier
- `WANVIDGEN_PRECISION`: Model precision (Q5, Q6, FP16, FP32)
- `WANVIDGEN_DEVICE`: Compute device (auto, cpu, cuda, mps)
- `WANVIDGEN_GPU_ID`: Specific GPU device ID

#### Video Output
- `WANVIDGEN_OUTPUT_DIR`: Output directory
- `WANVIDGEN_WIDTH`/`WANVIDGEN_HEIGHT`: Video dimensions
- `WANVIDGEN_FPS`: Frames per second
- `WANVIDGEN_QUALITY`: Quality preset (low, medium, high, ultra)

#### Performance
- `WANVIDGEN_BATCH_SIZE`: Inference batch size
- `WANVIDGEN_NUM_WORKERS`: Data loading workers
- `WANVIDGEN_PIN_MEMORY`: GPU memory optimization

See `.env.example` for complete documentation.

### Configuration File

You can also use YAML configuration files:

```yaml
model:
  model_path: "./models/wan2.1.gguf"
  precision: "Q5"
  device: "auto"

output:
  width: 1024
  height: 576
  fps: 30
  quality: "high"

pipeline:
  batch_size: 1
  num_workers: 4
```

## Project Structure

```
src/wanvidgen/
├── __init__.py          # Package initialization
├── __main__.py          # Module entry point
├── config.py            # Configuration management
├── models.py            # Model loading and management
├── pipeline.py          # Video generation pipeline
├── outputs.py           # Output file management
├── utils.py             # Utility functions
├── gui.py               # Graphical user interface
└── main.py              # Main application logic
```

## Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
isort src/
```

### Type Checking
```bash
mypy src/
```

## Model Support

### Supported Formats
- **GGUF**: Quantized models (Q4, Q5, Q6, Q8)
- **PyTorch**: Standard PyTorch models (.bin, .safetensors)
- **ONNX**: Open Neural Network Exchange format (planned)

### Recommended Models
- Wan2.1 GGUF quantized models for memory efficiency
- Models with video generation capabilities
- Models supporting text-to-video or image-to-video tasks

## GPU Support

### NVIDIA CUDA
- Requires CUDA-compatible GPU
- Install CUDA toolkit
- Set `WANVIDGEN_DEVICE=cuda`

### Apple Silicon (MPS)
- Requires Apple Silicon Mac
- Set `WANVIDGEN_DEVICE=mps`

### CPU
- Works on all systems
- Slower but universal
- Set `WANVIDGEN_DEVICE=cpu`

## Troubleshooting

### Common Issues

#### Model Loading Failures
- Verify model file exists and is readable
- Check model format compatibility
- Ensure sufficient RAM for model size

#### GPU Memory Errors
- Reduce batch size (`WANVIDGEN_BATCH_SIZE=1`)
- Use quantized models (Q5, Q6)
- Close other GPU-intensive applications

#### GUI Not Starting
- Ensure CustomTkinter is installed
- Check display environment (for headless systems)
- Use command-line mode as fallback

#### Poor Performance
- Use GPU acceleration when available
- Adjust batch size and worker count
- Consider model quantization for memory efficiency

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Run linting and type checking
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Support

- GitHub Issues: Report bugs and feature requests
- Documentation: See inline code documentation
- Discussions: Community support and questions

## Version History

- **0.1.0**: Initial release with basic functionality
  - GGUF model support
  - GUI and CLI interfaces
  - Basic video generation pipeline
  - Configuration management
