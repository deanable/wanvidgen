"""GPU memory utilities for managing model weights and preventing OOM."""

import torch
from typing import Optional
from .exceptions import GPUMemoryError


class MemoryManager:
    """Manages GPU memory for model inference."""

    def __init__(self, device: str = "cuda", min_free_memory_mb: float = 256):
        """Initialize memory manager.

        Args:
            device: Device to monitor ("cuda" or "cpu").
            min_free_memory_mb: Minimum free memory required in MB.
        """
        self.device = device
        self.min_free_memory_mb = min_free_memory_mb
        self.is_cuda = device == "cuda" and torch.cuda.is_available()

    def get_free_gpu_memory_mb(self) -> float:
        """Get available GPU memory in MB.

        Returns:
            Free memory in MB. Returns float('inf') if not on CUDA.
        """
        if not self.is_cuda:
            return float("inf")

        torch.cuda.synchronize()
        return torch.cuda.get_device_properties(0).total_memory / 1024 / 1024 - (
            torch.cuda.memory_allocated() / 1024 / 1024
        )

    def check_available_memory(self, required_mb: float) -> bool:
        """Check if required memory is available.

        Args:
            required_mb: Required memory in MB.

        Returns:
            True if memory is available, False otherwise.
        """
        if not self.is_cuda:
            return True
        return self.get_free_gpu_memory_mb() >= required_mb

    def assert_memory_available(
        self, required_mb: float, operation_name: str = "operation"
    ) -> None:
        """Assert that required memory is available, raise exception otherwise.

        Args:
            required_mb: Required memory in MB.
            operation_name: Name of operation for error message.

        Raises:
            GPUMemoryError: If insufficient memory available.
        """
        if not self.is_cuda:
            return

        free_mb = self.get_free_gpu_memory_mb()
        if free_mb < required_mb:
            user_msg = (
                f"Insufficient GPU memory for {operation_name}. "
                f"Required: {required_mb:.0f}MB, Available: {free_mb:.0f}MB. "
                "Try reducing batch size or image resolution."
            )
            raise GPUMemoryError(
                f"GPU memory insufficient: {free_mb:.0f}MB < {required_mb:.0f}MB",
                user_message=user_msg,
            )

    def free_memory(self) -> None:
        """Free GPU memory."""
        if self.is_cuda:
            torch.cuda.empty_cache()

    def get_memory_stats(self) -> dict:
        """Get current memory statistics.

        Returns:
            Dictionary with memory stats.
        """
        if not self.is_cuda:
            return {"device": "cpu"}

        torch.cuda.synchronize()
        total_mb = torch.cuda.get_device_properties(0).total_memory / 1024 / 1024
        allocated_mb = torch.cuda.memory_allocated() / 1024 / 1024
        free_mb = total_mb - allocated_mb

        return {
            "device": "cuda",
            "total_mb": total_mb,
            "allocated_mb": allocated_mb,
            "free_mb": free_mb,
            "utilization_percent": (allocated_mb / total_mb * 100) if total_mb > 0 else 0,
        }
