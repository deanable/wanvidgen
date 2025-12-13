from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, Sequence

from .utils import memory

try:
    from dotenv import load_dotenv
except Exception:  # pragma: no cover
    load_dotenv = None  # type: ignore[assignment]


class ConfigError(Exception):
    """A friendly configuration error.

    - In CLI contexts, `str(exc)` provides a human-readable multi-line message.
    - In GUI contexts, access `exc.title` and `exc.issues` for structured display.
    """

    def __init__(self, issues: Sequence[str], *, title: str = "Invalid configuration") -> None:
        super().__init__(title)
        self.title = title
        self.issues = list(issues)

    def to_cli(self) -> str:
        lines = [f"{self.title}:"]
        lines.extend(f"- {issue}" for issue in self.issues)
        return "\n".join(lines)

    def to_gui(self) -> dict[str, object]:
        return {"title": self.title, "issues": list(self.issues)}

    def __str__(self) -> str:  # pragma: no cover
        return self.to_cli()


Sampler = str
Scheduler = str


@dataclass(frozen=True, slots=True)
class WanvidgenConfig:
    device: str
    gpu_index: int | None
    gpu_memory_fraction: float
    allow_tf32: bool
    precision: str
    quantization: str
    sampler: Sampler
    scheduler: Scheduler
    model_dir: Path | None
    output_dir: Path
    cache_dir: Path
    temp_dir: Path
    batch_size: int
    num_workers: int
    log_level: str
    log_json: bool
    log_file: Path | None
    clear_memory_on_load: bool

    @property
    def torch_device(self):
        return memory.to_torch_device(self.device, gpu_index=self.gpu_index)


_ALLOWED_PRECISION = {"fp32", "fp16", "bf16"}
_ALLOWED_QUANT = {"none", "q5", "q6"}
_ALLOWED_SAMPLERS = {
    "euler",
    "euler_a",
    "ddim",
    "dpmpp_2m",
    "dpmpp_2m_sde",
}
_ALLOWED_SCHEDULERS = {"normal", "karras", "exponential"}
_ALLOWED_LOG_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}


def _env(name: str, default: str | None = None) -> str | None:
    val = os.environ.get(name)
    if val is None or val == "":
        return default
    return val


def _parse_bool(name: str, raw: str | None, *, default: bool) -> bool:
    if raw is None:
        return default
    v = raw.strip().lower()
    if v in {"1", "true", "t", "yes", "y", "on"}:
        return True
    if v in {"0", "false", "f", "no", "n", "off"}:
        return False
    raise ValueError(f"{name} must be a boolean (true/false), got {raw!r}")


def _parse_int(name: str, raw: str | None, *, default: int, min_: int | None = None, max_: int | None = None) -> int:
    if raw is None:
        val = default
    else:
        try:
            val = int(raw)
        except ValueError as e:
            raise ValueError(f"{name} must be an integer, got {raw!r}") from e

    if min_ is not None and val < min_:
        raise ValueError(f"{name} must be >= {min_}, got {val}")
    if max_ is not None and val > max_:
        raise ValueError(f"{name} must be <= {max_}, got {val}")
    return val


def _parse_float(name: str, raw: str | None, *, default: float, min_: float | None = None, max_: float | None = None) -> float:
    if raw is None:
        val = default
    else:
        try:
            val = float(raw)
        except ValueError as e:
            raise ValueError(f"{name} must be a number, got {raw!r}") from e

    if min_ is not None and val < min_:
        raise ValueError(f"{name} must be >= {min_}, got {val}")
    if max_ is not None and val > max_:
        raise ValueError(f"{name} must be <= {max_}, got {val}")
    return val


def _parse_choice(name: str, raw: str | None, *, default: str, allowed: Iterable[str], lower: bool = True) -> str:
    val = default if raw is None else raw
    val_norm = val.strip().lower() if lower else val.strip()

    allowed_set = set(a.lower() if lower else a for a in allowed)
    if val_norm not in allowed_set:
        opts = ", ".join(sorted(allowed_set))
        raise ValueError(f"{name} must be one of: {opts}; got {val!r}")

    return val_norm


def _parse_path(name: str, raw: str | None, *, default: Path | None = None) -> Path | None:
    if raw is None:
        return default
    p = Path(raw).expanduser()
    return p


def _ensure_dir(path: Path, *, create: bool, name: str) -> None:
    if path.exists():
        if not path.is_dir():
            raise ValueError(f"{name} must be a directory path; got {str(path)!r}")
        return
    if not create:
        raise ValueError(f"{name} directory does not exist: {str(path)!r}")
    path.mkdir(parents=True, exist_ok=True)


def load_config(dotenv_path: str | Path | None = None, *, override_dotenv: bool = False) -> WanvidgenConfig:
    """Load configuration from environment variables.

    Reads a .env file via python-dotenv when available, then validates values and
    returns a typed config object.

    Raises:
        ConfigError: with friendly, multi-issue output.
    """

    if load_dotenv is not None:
        load_dotenv(dotenv_path=dotenv_path, override=override_dotenv)

    issues: list[str] = []

    def capture(fn, *args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except ValueError as e:
            issues.append(str(e))
            return None

    device = capture(_parse_choice, "WANVIDGEN_DEVICE", _env("WANVIDGEN_DEVICE"), default="auto", allowed={"auto", "cpu", "cuda", "mps"}) or "auto"
    gpu_index = capture(_parse_int, "WANVIDGEN_GPU_INDEX", _env("WANVIDGEN_GPU_INDEX"), default=-1, min_=-1, max_=128)
    gpu_index_val = None if gpu_index in (None, -1) else gpu_index

    gpu_memory_fraction = capture(
        _parse_float,
        "WANVIDGEN_GPU_MEMORY_FRACTION",
        _env("WANVIDGEN_GPU_MEMORY_FRACTION"),
        default=1.0,
        min_=0.0,
        max_=1.0,
    )
    if gpu_memory_fraction is None:
        gpu_memory_fraction = 1.0

    allow_tf32 = capture(_parse_bool, "WANVIDGEN_ALLOW_TF32", _env("WANVIDGEN_ALLOW_TF32"), default=True)
    if allow_tf32 is None:
        allow_tf32 = True

    precision = capture(
        _parse_choice,
        "WANVIDGEN_PRECISION",
        _env("WANVIDGEN_PRECISION"),
        default="fp16",
        allowed=_ALLOWED_PRECISION,
    ) or "fp16"

    quantization = capture(
        _parse_choice,
        "WANVIDGEN_QUANTIZATION",
        _env("WANVIDGEN_QUANTIZATION"),
        default="none",
        allowed=_ALLOWED_QUANT,
    ) or "none"

    sampler = capture(
        _parse_choice,
        "WANVIDGEN_SAMPLER",
        _env("WANVIDGEN_SAMPLER"),
        default="euler",
        allowed=_ALLOWED_SAMPLERS,
    ) or "euler"

    scheduler = capture(
        _parse_choice,
        "WANVIDGEN_SCHEDULER",
        _env("WANVIDGEN_SCHEDULER"),
        default="karras",
        allowed=_ALLOWED_SCHEDULERS,
    ) or "karras"

    model_dir = capture(_parse_path, "WANVIDGEN_MODEL_DIR", _env("WANVIDGEN_MODEL_DIR"), default=None)
    if model_dir is not None:
        try:
            if not model_dir.exists():
                issues.append(f"WANVIDGEN_MODEL_DIR does not exist: {str(model_dir)!r}")
            elif not model_dir.is_dir():
                issues.append(f"WANVIDGEN_MODEL_DIR must be a directory: {str(model_dir)!r}")
        except OSError as e:
            issues.append(f"WANVIDGEN_MODEL_DIR is not accessible ({model_dir}): {e}")

    output_dir = capture(_parse_path, "WANVIDGEN_OUTPUT_DIR", _env("WANVIDGEN_OUTPUT_DIR"), default=Path("outputs"))
    cache_dir = capture(_parse_path, "WANVIDGEN_CACHE_DIR", _env("WANVIDGEN_CACHE_DIR"), default=Path("cache"))
    temp_dir = capture(_parse_path, "WANVIDGEN_TEMP_DIR", _env("WANVIDGEN_TEMP_DIR"), default=Path("tmp"))

    if output_dir is None:
        output_dir = Path("outputs")
    if cache_dir is None:
        cache_dir = Path("cache")
    if temp_dir is None:
        temp_dir = Path("tmp")

    for name, path, create in [
        ("WANVIDGEN_OUTPUT_DIR", output_dir, True),
        ("WANVIDGEN_CACHE_DIR", cache_dir, True),
        ("WANVIDGEN_TEMP_DIR", temp_dir, True),
    ]:
        try:
            _ensure_dir(path, create=create, name=name)
        except ValueError as e:
            issues.append(str(e))

    batch_size = capture(_parse_int, "WANVIDGEN_BATCH_SIZE", _env("WANVIDGEN_BATCH_SIZE"), default=1, min_=1, max_=1024)
    if batch_size is None:
        batch_size = 1

    num_workers = capture(_parse_int, "WANVIDGEN_NUM_WORKERS", _env("WANVIDGEN_NUM_WORKERS"), default=0, min_=0, max_=128)
    if num_workers is None:
        num_workers = 0

    log_level = capture(
        _parse_choice,
        "WANVIDGEN_LOG_LEVEL",
        _env("WANVIDGEN_LOG_LEVEL"),
        default="INFO",
        allowed=_ALLOWED_LOG_LEVELS,
        lower=False,
    ) or "INFO"

    log_json = capture(_parse_bool, "WANVIDGEN_LOG_JSON", _env("WANVIDGEN_LOG_JSON"), default=False)
    if log_json is None:
        log_json = False

    log_file = capture(_parse_path, "WANVIDGEN_LOG_FILE", _env("WANVIDGEN_LOG_FILE"), default=None)
    if log_file is not None:
        try:
            if log_file.exists() and log_file.is_dir():
                issues.append(f"WANVIDGEN_LOG_FILE must be a file path, not a directory: {str(log_file)!r}")
        except OSError as e:
            issues.append(f"WANVIDGEN_LOG_FILE is not accessible ({log_file}): {e}")

    clear_memory_on_load = capture(
        _parse_bool,
        "WANVIDGEN_CLEAR_MEMORY_ON_LOAD",
        _env("WANVIDGEN_CLEAR_MEMORY_ON_LOAD"),
        default=False,
    )
    if clear_memory_on_load is None:
        clear_memory_on_load = False

    try:
        req = memory.validate_device_request(device, gpu_index=gpu_index_val)
        resolved_device = req.name
        resolved_gpu_index = req.gpu_index
    except ValueError as e:
        issues.append(f"Device selection error: {e}")
        resolved_device = "cpu"
        resolved_gpu_index = None

    if issues:
        raise ConfigError(issues)

    cfg = WanvidgenConfig(
        device=resolved_device,
        gpu_index=resolved_gpu_index,
        gpu_memory_fraction=gpu_memory_fraction,
        allow_tf32=allow_tf32,
        precision=precision,
        quantization=quantization,
        sampler=sampler,
        scheduler=scheduler,
        model_dir=model_dir,
        output_dir=output_dir,
        cache_dir=cache_dir,
        temp_dir=temp_dir,
        batch_size=batch_size,
        num_workers=num_workers,
        log_level=log_level,
        log_json=log_json,
        log_file=log_file,
        clear_memory_on_load=clear_memory_on_load,
    )

    if cfg.clear_memory_on_load:
        memory.clear_memory()

    return cfg
