"""Unit tests for model managers."""

import pytest
import tempfile
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wanvidgen.models import CLIPManager, VAEManager, UNetManager
from wanvidgen.exceptions import ConfigError, ModelLoadError


@pytest.fixture
def temp_model_path():
    """Create a temporary model file."""
    with tempfile.TemporaryDirectory() as tmpdir:
        model_path = Path(tmpdir) / "model.gguf"
        model_path.touch()
        yield model_path


@pytest.fixture
def missing_model_path():
    """Path to a non-existent model file."""
    return Path("/nonexistent/model.gguf")


class TestCLIPManager:
    """Tests for CLIPManager."""

    def test_clip_initialization_valid_path(self, temp_model_path):
        """Test CLIP manager initialization with valid path."""
        manager = CLIPManager(temp_model_path, device="cpu")
        assert manager.config_path == temp_model_path
        assert manager.device == "cpu"
        assert not manager.is_loaded()

    def test_clip_initialization_invalid_path(self, missing_model_path):
        """Test CLIP manager initialization with invalid path."""
        with pytest.raises(ConfigError):
            CLIPManager(missing_model_path, device="cpu")

    def test_clip_load_unload(self, temp_model_path):
        """Test loading and unloading CLIP model."""
        manager = CLIPManager(temp_model_path, device="cpu")
        
        assert not manager.is_loaded()
        manager.load()
        assert manager.is_loaded()
        manager.unload()
        assert not manager.is_loaded()

    def test_clip_context_manager(self, temp_model_path):
        """Test CLIP manager as context manager."""
        with CLIPManager(temp_model_path, device="cpu") as manager:
            assert manager.is_loaded()
        assert not manager.is_loaded()

    def test_clip_quantization(self, temp_model_path):
        """Test CLIP manager with quantization."""
        manager = CLIPManager(temp_model_path, device="cpu", quantization="q5")
        assert manager.quantization == "q5"

    def test_clip_encode_text_unloaded(self, temp_model_path):
        """Test text encoding fails on unloaded model."""
        manager = CLIPManager(temp_model_path, device="cpu")
        
        with pytest.raises(ModelLoadError):
            manager.encode_text("test")

    def test_clip_encode_text_loaded(self, temp_model_path):
        """Test text encoding on loaded model."""
        manager = CLIPManager(temp_model_path, device="cpu")
        manager.load()
        
        embeddings = manager.encode_text("test")
        assert embeddings is not None
        
        manager.unload()

    def test_clip_encode_text_batch(self, temp_model_path):
        """Test batch text encoding."""
        manager = CLIPManager(temp_model_path, device="cpu")
        manager.load()
        
        texts = ["test1", "test2", "test3"]
        embeddings = manager.encode_text(texts)
        assert embeddings is not None
        
        manager.unload()


class TestVAEManager:
    """Tests for VAEManager."""

    def test_vae_initialization_valid_path(self, temp_model_path):
        """Test VAE manager initialization with valid path."""
        manager = VAEManager(temp_model_path, device="cpu")
        assert manager.config_path == temp_model_path
        assert manager.device == "cpu"
        assert not manager.is_loaded()

    def test_vae_initialization_invalid_path(self, missing_model_path):
        """Test VAE manager initialization with invalid path."""
        with pytest.raises(ConfigError):
            VAEManager(missing_model_path, device="cpu")

    def test_vae_load_unload(self, temp_model_path):
        """Test loading and unloading VAE model."""
        manager = VAEManager(temp_model_path, device="cpu")
        
        assert not manager.is_loaded()
        manager.load()
        assert manager.is_loaded()
        manager.unload()
        assert not manager.is_loaded()

    def test_vae_context_manager(self, temp_model_path):
        """Test VAE manager as context manager."""
        with VAEManager(temp_model_path, device="cpu") as manager:
            assert manager.is_loaded()
        assert not manager.is_loaded()

    def test_vae_quantization(self, temp_model_path):
        """Test VAE manager with quantization."""
        manager = VAEManager(temp_model_path, device="cpu", quantization="q6")
        assert manager.quantization == "q6"

    def test_vae_encode_unloaded(self, temp_model_path):
        """Test encoding fails on unloaded model."""
        import torch
        
        manager = VAEManager(temp_model_path, device="cpu")
        image = torch.randn(1, 3, 512, 512)
        
        with pytest.raises(ModelLoadError):
            manager.encode(image)

    def test_vae_decode_unloaded(self, temp_model_path):
        """Test decoding fails on unloaded model."""
        import torch
        
        manager = VAEManager(temp_model_path, device="cpu")
        latent = torch.randn(1, 4, 64, 64)
        
        with pytest.raises(ModelLoadError):
            manager.decode(latent)

    def test_vae_encode_loaded(self, temp_model_path):
        """Test encoding on loaded model."""
        import torch
        
        manager = VAEManager(temp_model_path, device="cpu")
        manager.load()
        
        image = torch.randn(1, 3, 512, 512)
        latent = manager.encode(image)
        assert latent is not None
        assert latent.shape[1] == 4  # VAE latent has 4 channels
        
        manager.unload()

    def test_vae_decode_loaded(self, temp_model_path):
        """Test decoding on loaded model."""
        import torch
        
        manager = VAEManager(temp_model_path, device="cpu")
        manager.load()
        
        latent = torch.randn(1, 4, 64, 64)
        image = manager.decode(latent)
        assert image is not None
        assert image.shape[1] == 3  # Decoded image has 3 channels
        
        manager.unload()


class TestUNetManager:
    """Tests for UNetManager."""

    def test_unet_initialization_valid_path(self, temp_model_path):
        """Test UNet manager initialization with valid path."""
        manager = UNetManager(temp_model_path, device="cpu")
        assert manager.config_path == temp_model_path
        assert manager.device == "cpu"
        assert not manager.is_loaded()

    def test_unet_initialization_invalid_path(self, missing_model_path):
        """Test UNet manager initialization with invalid path."""
        with pytest.raises(ConfigError):
            UNetManager(missing_model_path, device="cpu")

    def test_unet_load_unload(self, temp_model_path):
        """Test loading and unloading UNet model."""
        manager = UNetManager(temp_model_path, device="cpu")
        
        assert not manager.is_loaded()
        manager.load()
        assert manager.is_loaded()
        manager.unload()
        assert not manager.is_loaded()

    def test_unet_context_manager(self, temp_model_path):
        """Test UNet manager as context manager."""
        with UNetManager(temp_model_path, device="cpu") as manager:
            assert manager.is_loaded()
        assert not manager.is_loaded()

    def test_unet_quantization(self, temp_model_path):
        """Test UNet manager with quantization."""
        manager = UNetManager(temp_model_path, device="cpu", quantization="q5")
        assert manager.quantization == "q5"

    def test_unet_denoise_unloaded(self, temp_model_path):
        """Test denoising fails on unloaded model."""
        import torch
        
        manager = UNetManager(temp_model_path, device="cpu")
        latent = torch.randn(1, 4, 64, 64)
        embeddings = torch.randn(1, 77, 768)
        
        with pytest.raises(ModelLoadError):
            manager.denoise(latent, 100, embeddings)

    def test_unet_forward_unloaded(self, temp_model_path):
        """Test forward pass fails on unloaded model."""
        import torch
        
        manager = UNetManager(temp_model_path, device="cpu")
        sample = torch.randn(1, 4, 64, 64)
        timestep = torch.tensor([100])
        embeddings = torch.randn(1, 77, 768)
        
        with pytest.raises(ModelLoadError):
            manager.forward(sample, timestep, embeddings)

    def test_unet_denoise_loaded(self, temp_model_path):
        """Test denoising on loaded model."""
        import torch
        
        manager = UNetManager(temp_model_path, device="cpu")
        manager.load()
        
        latent = torch.randn(1, 4, 64, 64)
        embeddings = torch.randn(1, 77, 768)
        result = manager.denoise(latent, 100, embeddings, guidance_scale=7.5)
        assert result is not None
        assert result.shape == latent.shape
        
        manager.unload()

    def test_unet_forward_loaded(self, temp_model_path):
        """Test forward pass on loaded model."""
        import torch
        
        manager = UNetManager(temp_model_path, device="cpu")
        manager.load()
        
        sample = torch.randn(1, 4, 64, 64)
        timestep = torch.tensor([100])
        embeddings = torch.randn(1, 77, 768)
        result = manager.forward(sample, timestep, embeddings)
        assert result is not None
        assert result.shape == sample.shape
        
        manager.unload()
