"""Window-level spectral measurements and persistence summaries."""
from __future__ import annotations

import numpy as np

from .comb import detect_comb
from .spectrum import analyze_frequencies


def analyze_temporal(samples: np.ndarray, rate: int, *, window_seconds: float = 5.0,
                     max_windows: int = 48) -> dict:
    if window_seconds <= 0 or max_windows < 1:
        raise ValueError("window_seconds and max_windows must be positive")
    size = max(1, int(rate * window_seconds))
    n = len(samples) // size
    if n == 0:
        return {"available": False, "reason": "Audio is shorter than analysis window", "windows": []}
    # Deterministic representative window positions for long recordings.
    indices = np.unique(np.linspace(0, n - 1, min(n, max_windows)).astype(int))
    windows = []
    for idx in indices:
        start = int(idx * size)
        part = samples[start:start + size]
        combo = detect_comb(part, rate)
        spectrum = analyze_frequencies(part, rate)
        windows.append({"start_s": float(start / rate),
                        "end_s": float((start + size) / rate),
                        "periodicity_candidate": bool(combo.get("candidate_periodicity", False)),
                        "cutoff_candidate_hz": spectrum["candidate_cutoff"].get("candidate_hz")})
    return {"available": True, "windows": windows,
            "periodicity_candidate_fraction": float(np.mean([w["periodicity_candidate"] for w in windows])),
            "analyzed_window_count": len(windows),
            "total_full_windows": n,
            "method": "nonoverlapping_window_subsample"}
