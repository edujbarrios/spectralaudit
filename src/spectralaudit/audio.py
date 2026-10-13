"""Local audio ingestion and baseline measurements."""
from __future__ import annotations

from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import numpy as np
import soundfile as sf


@dataclass
class Audio:
    samples: np.ndarray  # (frames, channels), float64
    rate: int
    path: str
    metadata: dict

    @property
    def mono(self) -> np.ndarray:
        return np.mean(self.samples, axis=1)


def load_audio(path: str | Path, *, max_seconds: float | None = None) -> Audio:
    """Read audio without normalization; full-file load, optionally bounded by duration."""
    source = Path(path)
    if not source.is_file():
        raise FileNotFoundError(source)
    info = sf.info(str(source))
    if info.samplerate <= 0 or info.frames < 1:
        raise ValueError("Empty or invalid audio file")
    if max_seconds is not None and info.frames / info.samplerate > max_seconds:
        raise ValueError(f"Audio exceeds max_seconds={max_seconds}; no implicit truncation")
    samples, rate = sf.read(str(source), dtype="float64", always_2d=True)
    if samples.size == 0 or not np.all(np.isfinite(samples)):
        raise ValueError("Audio has no samples or contains non-finite values")
    h = sha256()
    with source.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    peak = float(np.max(np.abs(samples)))
    rms = float(np.sqrt(np.mean(np.square(samples))))
    metadata = {
        "path": str(source), "sha256": h.hexdigest(), "samplerate_hz": int(rate),
        "duration_s": float(len(samples) / rate), "frames": int(len(samples)),
        "channels": int(samples.shape[1]), "subtype": info.subtype,
        "peak_amplitude": peak, "rms_amplitude": rms,
        "clipped_sample_fraction": float(np.mean(np.abs(samples) >= 0.9999)),
        "sample_peak_only": True,
    }
    return Audio(samples, rate, str(source), metadata)
