"""Unit tests for exceptions."""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wanvidgen.exceptions import (
    WanVidGenException,
    ModelLoadError,
    ConfigError,
    GPUMemoryError,
    PipelineError,
    GenerationError,
)


class TestExceptions:
    """Tests for exception classes."""

    def test_wanvidgen_exception_basic(self):
        """Test basic exception creation."""
        exc = WanVidGenException("Technical message")
        assert str(exc) == "Technical message"
        assert exc.message == "Technical message"
        assert exc.user_message == "Technical message"

    def test_wanvidgen_exception_with_user_message(self):
        """Test exception with custom user message."""
        exc = WanVidGenException(
            "Technical error details",
            user_message="Something went wrong"
        )
        assert exc.message == "Technical error details"
        assert exc.user_message == "Something went wrong"
        assert str(exc) == "Technical error details"

    def test_model_load_error(self):
        """Test ModelLoadError."""
        exc = ModelLoadError("Failed to load model")
        assert isinstance(exc, WanVidGenException)
        assert exc.message == "Failed to load model"

    def test_config_error(self):
        """Test ConfigError."""
        exc = ConfigError("Invalid configuration", user_message="Config is wrong")
        assert isinstance(exc, WanVidGenException)
        assert exc.user_message == "Config is wrong"

    def test_gpu_memory_error(self):
        """Test GPUMemoryError."""
        exc = GPUMemoryError(
            "Insufficient GPU memory",
            user_message="Not enough GPU memory"
        )
        assert isinstance(exc, WanVidGenException)
        assert "Insufficient" in exc.message
        assert "Not enough" in exc.user_message

    def test_pipeline_error(self):
        """Test PipelineError."""
        exc = PipelineError("Pipeline failed")
        assert isinstance(exc, WanVidGenException)

    def test_generation_error(self):
        """Test GenerationError."""
        exc = GenerationError("Generation failed")
        assert isinstance(exc, WanVidGenException)

    def test_exception_inheritance_chain(self):
        """Test exception inheritance."""
        exceptions = [
            ModelLoadError(""),
            ConfigError(""),
            GPUMemoryError(""),
            PipelineError(""),
            GenerationError(""),
        ]
        
        for exc in exceptions:
            assert isinstance(exc, WanVidGenException)
            assert isinstance(exc, Exception)

    def test_exception_can_be_raised_and_caught(self):
        """Test raising and catching exceptions."""
        with pytest.raises(WanVidGenException):
            raise ConfigError("Test error")
        
        with pytest.raises(GenerationError):
            raise GenerationError("Generation error")

    def test_exception_message_preservation(self):
        """Test that exception messages are preserved."""
        original_msg = "This is a detailed error message"
        user_msg = "This is user friendly"
        
        exc = ModelLoadError(original_msg, user_message=user_msg)
        
        assert exc.message == original_msg
        assert exc.user_message == user_msg


import pytest
