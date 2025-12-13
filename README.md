# WanVidGen - Video Generation Pipeline

A modular video generation pipeline with support for CLIP, VAE, and UNet models with GGUF quantization support (Q5/Q6).

## Features

- **Model Managers**: Specialized managers for CLIP, VAE, and UNet models
  - Support for GGUF format weights
  - Q5 and Q6 quantization support
  - Lifecycle management (load/unload)
  - GPU device placement

- **Generation Pipeline**: Orchestrates model inference for video generation
  - Synchronous and asynchronous APIs
  - Full parameter preservation (prompt, negative prompt, resolution, steps, sampler, scheduler, seed, fps, clip guidance, etc.)
  - Frame sequence generation with metadata

- **Memory Management**: GPU memory utilities
  - Memory availability checking before operations
  - Automatic memory cleanup
  - OOM prevention with user-friendly error messages

- **Structured Exceptions**: User-friendly error handling
  - Separate technical and user-facing messages
  - GUI-ready error information

## Project Structure

```
src/wanvidgen/
├── __init__.py
├── exceptions.py          # Exception classes
├── memory.py              # GPU memory management
├── pipeline.py            # Main generation pipeline
└── models/
    ├── __init__.py
    ├── base_manager.py    # Base model manager
    ├── clip_manager.py    # CLIP model manager
    ├── vae_manager.py     # VAE model manager
    └── unet_manager.py    # UNet model manager

tests/
├── test_pipeline.py       # Pipeline tests
├── test_models.py         # Model manager tests
├── test_memory.py         # Memory management tests
└── test_exceptions.py     # Exception tests

examples/
└── basic_generation.py    # Basic usage example
```

## Installation

```bash
pip install -e .
```

## Usage

### Basic Example

```python
from wanvidgen.pipeline import GenerationPipeline, GenerationConfig

# Initialize pipeline
pipeline = GenerationPipeline(
    clip_config_path="./models/clip.gguf",
    vae_config_path="./models/vae.gguf",
    unet_config_path="./models/unet.gguf",
    device="cuda",
    clip_quantization="q5",
    vae_quantization="q5",
    unet_quantization="q6",
)

# Use context manager for automatic model loading/unloading
with pipeline:
    config = GenerationConfig(
        prompt="A beautiful landscape at sunset",
        negative_prompt="blurry, low quality",
        height=512,
        width=512,
        num_inference_steps=50,
        sampler="ddim",
        scheduler="linear",
        seed=42,
        fps=8,
        clip_guidance_scale=7.5,
    )
    
    result = pipeline.generate(config)
    
    print(f"Generated {result.get_frame_count()} frames")
    print(f"FPS: {result.get_fps()}")
```

### Asynchronous Generation

```python
import asyncio

async def generate_async():
    async with pipeline:
        result = await pipeline.generate_async(config)
        return result

# Run async generation
result = asyncio.run(generate_async())
```

### Manual Model Management

```python
# Load models explicitly
pipeline = GenerationPipeline(...)
pipeline.load()

try:
    result = pipeline.generate(config)
finally:
    pipeline.unload()
```

## API Reference

### GenerationPipeline

Main class for orchestrating video generation.

#### Methods

- `load()`: Load all models
- `unload()`: Unload all models and free memory
- `is_loaded()`: Check if models are loaded
- `generate(config)`: Generate video synchronously
- `generate_async(config)`: Generate video asynchronously

### GenerationConfig

Configuration for generation parameters.

#### Fields

- `prompt`: Main generation prompt
- `negative_prompt`: Negative prompt (default: "")
- `height`: Output height in pixels (default: 512)
- `width`: Output width in pixels (default: 512)
- `num_inference_steps`: Number of diffusion steps (default: 50)
- `sampler`: Sampling method (default: "ddim")
- `scheduler`: Noise scheduler (default: "linear")
- `seed`: Random seed (default: 42)
- `fps`: Frames per second (default: 8)
- `clip_guidance_scale`: CLIP guidance strength (default: 7.5)
- `extra_params`: Additional parameters (default: {})

### Model Managers

#### CLIPManager

Text encoding model manager.

- `load()`: Load CLIP model
- `unload()`: Unload CLIP model
- `encode_text(text)`: Encode text to embeddings

#### VAEManager

Latent space encoding/decoding model manager.

- `load()`: Load VAE model
- `unload()`: Unload VAE model
- `encode(image)`: Encode image to latent
- `decode(latent)`: Decode latent to image

#### UNetManager

Diffusion denoising model manager.

- `load()`: Load UNet model
- `unload()`: Unload UNet model
- `denoise(latent, timestep, encoder_hidden_states, guidance_scale)`: Run denoising step
- `forward(sample, timestep, encoder_hidden_states)`: Forward pass

### Memory Management

#### MemoryManager

GPU memory management utilities.

- `get_free_gpu_memory_mb()`: Get available GPU memory
- `check_available_memory(required_mb)`: Check if memory available
- `assert_memory_available(required_mb, operation_name)`: Assert with error
- `free_memory()`: Free GPU memory
- `get_memory_stats()`: Get memory statistics

### Exceptions

- `WanVidGenException`: Base exception
- `ModelLoadError`: Model loading failure
- `ConfigError`: Configuration error
- `GPUMemoryError`: Insufficient GPU memory
- `PipelineError`: Pipeline-related errors
- `GenerationError`: Generation-related errors

## Testing

Run the test suite:

```bash
pytest tests/
```

Run specific test file:

```bash
pytest tests/test_pipeline.py -v
```

Run with coverage:

```bash
pytest tests/ --cov=src/wanvidgen --cov-report=html
```

## Requirements

- Python >= 3.8
- PyTorch >= 1.9
- numpy

## License

MIT
