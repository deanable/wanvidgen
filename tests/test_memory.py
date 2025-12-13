"""Unit tests for memory management."""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from wanvidgen.memory import MemoryManager
from wanvidgen.exceptions import GPUMemoryError


class TestMemoryManager:
    """Tests for MemoryManager."""

    def test_memory_manager_initialization_cpu(self):
        """Test memory manager initialization on CPU."""
        manager = MemoryManager(device="cpu")
        assert manager.device == "cpu"
        assert manager.is_cuda is False

    def test_memory_manager_initialization_cuda(self):
        """Test memory manager initialization on CUDA."""
        manager = MemoryManager(device="cuda")
        assert manager.device == "cuda"
        # is_cuda depends on torch.cuda availability

    def test_get_free_gpu_memory_cpu(self):
        """Test getting free GPU memory on CPU device."""
        manager = MemoryManager(device="cpu")
        free_mb = manager.get_free_gpu_memory_mb()
        assert free_mb == float("inf")

    def test_check_available_memory_cpu(self):
        """Test checking available memory on CPU."""
        manager = MemoryManager(device="cpu")
        assert manager.check_available_memory(1000000)  # Should always return True
        assert manager.check_available_memory(float("inf"))  # Should always return True

    def test_assert_memory_available_cpu(self):
        """Test asserting memory availability on CPU."""
        manager = MemoryManager(device="cpu")
        # Should not raise on CPU
        manager.assert_memory_available(1000000, "test operation")

    def test_free_memory_cpu(self):
        """Test freeing memory on CPU."""
        manager = MemoryManager(device="cpu")
        # Should not raise
        manager.free_memory()

    def test_get_memory_stats_cpu(self):
        """Test getting memory stats on CPU."""
        manager = MemoryManager(device="cpu")
        stats = manager.get_memory_stats()
        assert stats["device"] == "cpu"

    def test_memory_manager_custom_min_free(self):
        """Test memory manager with custom minimum free memory."""
        manager = MemoryManager(device="cpu", min_free_memory_mb=512)
        assert manager.min_free_memory_mb == 512

    def test_memory_manager_defaults(self):
        """Test memory manager default values."""
        manager = MemoryManager()
        assert manager.device == "cuda"
        assert manager.min_free_memory_mb == 256

    def test_check_available_memory_with_requirement(self):
        """Test checking specific memory requirements."""
        manager = MemoryManager(device="cpu")
        # CPU should always report sufficient memory
        assert manager.check_available_memory(100)
        assert manager.check_available_memory(10000)
        assert manager.check_available_memory(1000000)

    def test_multiple_operations_cpu(self):
        """Test multiple memory operations on CPU."""
        manager = MemoryManager(device="cpu")
        
        # All these should work without error
        stats1 = manager.get_memory_stats()
        assert "device" in stats1
        
        free1 = manager.get_free_gpu_memory_mb()
        assert free1 == float("inf")
        
        assert manager.check_available_memory(1000)
        
        manager.free_memory()
        
        stats2 = manager.get_memory_stats()
        assert stats2["device"] == "cpu"
