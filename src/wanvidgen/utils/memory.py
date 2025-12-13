from __future__ import annotations

import gc
from dataclasses import dataclass
from typing import Any

try:
    import torch
except Exception:  # pragma: no cover
    torch = None  # type: ignore[assignment]


def torch_available() -> bool:
    return torch is not None


def cuda_available() -> bool:
    return bool(torch is not None and torch.cuda.is_available())


def mps_available() -> bool:
    return bool(
        torch is not None
        and hasattr(torch.backends, "mps")
        and torch.backends.mps.is_available()
    )


def best_device() -> str:
    if cuda_available():
        return "cuda"
    if mps_available():
        return "mps"
    return "cpu"


def cuda_device_count() -> int:
    if not cuda_available():
        return 0
    assert torch is not None
    return int(torch.cuda.device_count())


@dataclass(frozen=True, slots=True)
class DeviceRequest:
    name: str
    gpu_index: int | None = None


def normalize_device_name(device: str) -> str:
    d = device.strip().lower()
    if d in {"auto", "cpu", "cuda", "mps"}:
        return d
    raise ValueError(f"Unknown device '{device}'. Expected one of: auto, cpu, cuda, mps")


def validate_device_request(device: str, gpu_index: int | None = None) -> DeviceRequest:
    name = normalize_device_name(device)

    if name == "auto":
        name = best_device()

    if name == "cuda":
        if not cuda_available():
            raise ValueError("CUDA was requested but torch.cuda.is_available() is False")
        if gpu_index is not None:
            count = cuda_device_count()
            if count == 0:
                raise ValueError("CUDA was requested but no CUDA devices are visible")
            if gpu_index < 0 or gpu_index >= count:
                raise ValueError(
                    f"GPU index {gpu_index} is out of range; available CUDA devices: 0..{count - 1}"
                )

    if name == "mps" and not mps_available():
        raise ValueError("MPS was requested but torch.backends.mps.is_available() is False")

    return DeviceRequest(name=name, gpu_index=gpu_index)


def to_torch_device(device: str, gpu_index: int | None = None) -> Any:
    req = validate_device_request(device, gpu_index=gpu_index)

    if torch is None:
        return req.name

    if req.name == "cuda" and req.gpu_index is not None:
        return torch.device(f"cuda:{req.gpu_index}")
    return torch.device(req.name)


def clear_memory() -> int:
    """Free as much memory as possible.

    Mirrors common notebook cleanup logic:
    - triggers Python GC
    - clears CUDA allocator cache when available
    """

    collected = gc.collect()

    if torch is not None and torch.cuda.is_available():
        torch.cuda.empty_cache()
        if hasattr(torch.cuda, "ipc_collect"):
            try:
                torch.cuda.ipc_collect()
            except Exception:  # pragma: no cover
                pass

    return int(collected)
