"""Unit tests for the generation pipeline."""

import pytest
import tempfile
from pathlib import Path
import torch
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wanvidgen.pipeline import GenerationPipeline, GenerationConfig, GenerationResult
from wanvidgen.exceptions import (
    ConfigError,
    GenerationError,
    PipelineError,
)


@pytest.fixture
def temp_model_paths():
    """Create temporary model paths for testing."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        
        # Create dummy model files
        clip_path = tmpdir / "clip.gguf"
        vae_path = tmpdir / "vae.gguf"
        unet_path = tmpdir / "unet.gguf"
        
        clip_path.touch()
        vae_path.touch()
        unet_path.touch()
        
        yield {
            "clip": clip_path,
            "vae": vae_path,
            "unet": unet_path,
        }


def test_pipeline_initialization(temp_model_paths):
    """Test pipeline initialization with valid paths."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    assert pipeline.device == "cpu"
    assert not pipeline.is_loaded()


def test_pipeline_initialization_missing_clip(temp_model_paths):
    """Test pipeline initialization fails with missing CLIP model."""
    with pytest.raises(ConfigError):
        GenerationPipeline(
            clip_config_path=Path("/nonexistent/clip.gguf"),
            vae_config_path=temp_model_paths["vae"],
            unet_config_path=temp_model_paths["unet"],
            device="cpu",
        )


def test_pipeline_initialization_missing_vae(temp_model_paths):
    """Test pipeline initialization fails with missing VAE model."""
    with pytest.raises(ConfigError):
        GenerationPipeline(
            clip_config_path=temp_model_paths["clip"],
            vae_config_path=Path("/nonexistent/vae.gguf"),
            unet_config_path=temp_model_paths["unet"],
            device="cpu",
        )


def test_pipeline_initialization_missing_unet(temp_model_paths):
    """Test pipeline initialization fails with missing UNet model."""
    with pytest.raises(ConfigError):
        GenerationPipeline(
            clip_config_path=temp_model_paths["clip"],
            vae_config_path=temp_model_paths["vae"],
            unet_config_path=Path("/nonexistent/unet.gguf"),
            device="cpu",
        )


def test_pipeline_load_unload(temp_model_paths):
    """Test loading and unloading models."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    assert not pipeline.is_loaded()
    
    pipeline.load()
    assert pipeline.is_loaded()
    
    pipeline.unload()
    assert not pipeline.is_loaded()


def test_pipeline_context_manager(temp_model_paths):
    """Test pipeline as context manager."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    with pipeline:
        assert pipeline.is_loaded()
    
    assert not pipeline.is_loaded()


def test_generate_without_loading(temp_model_paths):
    """Test that generate fails if models not loaded."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    config = GenerationConfig(prompt="Test prompt")
    
    with pytest.raises(PipelineError):
        pipeline.generate(config)


def test_generation_config_validation():
    """Test generation config validation."""
    # Valid config
    config = GenerationConfig(prompt="Test")
    assert config.prompt == "Test"
    
    # Test config with custom values
    config = GenerationConfig(
        prompt="A beautiful scene",
        negative_prompt="blurry",
        height=768,
        width=768,
        num_inference_steps=75,
        sampler="euler",
        scheduler="cosine",
        seed=123,
        fps=16,
        clip_guidance_scale=10.0,
    )
    assert config.height == 768
    assert config.width == 768
    assert config.num_inference_steps == 75
    assert config.seed == 123
    assert config.fps == 16


def test_generate_empty_prompt(temp_model_paths):
    """Test generation with empty prompt fails."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    with pipeline:
        config = GenerationConfig(prompt="")
        
        with pytest.raises(GenerationError):
            pipeline.generate(config)


def test_generate_invalid_height(temp_model_paths):
    """Test generation with invalid height fails."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    with pipeline:
        config = GenerationConfig(prompt="Test", height=-1)
        
        with pytest.raises(GenerationError):
            pipeline.generate(config)


def test_generate_invalid_steps(temp_model_paths):
    """Test generation with invalid steps fails."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    with pipeline:
        config = GenerationConfig(prompt="Test", num_inference_steps=0)
        
        with pytest.raises(GenerationError):
            pipeline.generate(config)


def test_generate_invalid_fps(temp_model_paths):
    """Test generation with invalid fps fails."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    with pipeline:
        config = GenerationConfig(prompt="Test", fps=0)
        
        with pytest.raises(GenerationError):
            pipeline.generate(config)


def test_generation_result_metadata(temp_model_paths):
    """Test generation result metadata."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    config = GenerationConfig(
        prompt="Test prompt",
        height=512,
        width=512,
        fps=8,
        num_inference_steps=50,
    )
    
    with pipeline:
        result = pipeline.generate(config)
        
        assert result.get_fps() == 8
        assert result.metadata["height"] == 512
        assert result.metadata["width"] == 512
        assert result.metadata["fps"] == 8
        assert "num_frames" in result.metadata
        assert "seed" in result.metadata


def test_generation_result_frames(temp_model_paths):
    """Test generation result frames."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
    )
    
    config = GenerationConfig(prompt="Test prompt")
    
    with pipeline:
        result = pipeline.generate(config)
        
        assert result.get_frame_count() > 0
        assert all(isinstance(f, torch.Tensor) for f in result.frames)


def test_quantization_parameters(temp_model_paths):
    """Test pipeline initialization with quantization parameters."""
    pipeline = GenerationPipeline(
        clip_config_path=temp_model_paths["clip"],
        vae_config_path=temp_model_paths["vae"],
        unet_config_path=temp_model_paths["unet"],
        device="cpu",
        clip_quantization="q5",
        vae_quantization="q6",
        unet_quantization="q5",
    )
    
    assert pipeline.clip_manager.quantization == "q5"
    assert pipeline.vae_manager.quantization == "q6"
    assert pipeline.unet_manager.quantization == "q5"


def test_generation_config_to_dict():
    """Test converting generation config to dictionary."""
    config = GenerationConfig(
        prompt="Test",
        height=512,
        width=512,
        fps=8,
    )
    
    config_dict = config.to_dict()
    assert config_dict["prompt"] == "Test"
    assert config_dict["height"] == 512
    assert config_dict["width"] == 512
    assert config_dict["fps"] == 8
