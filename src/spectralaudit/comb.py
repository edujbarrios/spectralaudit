"""Independent heuristic for approximately periodic narrow peaks in PSD residuals."""
from __future__ import annotations

import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter1d

from .spectrum import compute_psd


def detect_comb(samples: np.ndarray, rate: int, *, low_hz: float = 5000,
                high_hz: float = 16000, nperseg: int = 16384,
                prominence_db: float = 5.0, min_peaks: int = 5) -> dict:
    """Diagnostic spectral periodicity, not proof of synthetic origin.

    Computes residuals after spectral-envelope subtraction and inspects the
    distances between local peaks. A stationary harmonic instrument can also
    generate a regular comb: this is not an origin classifier.
    """
    if low_hz < 0 or low_hz >= high_hz:
        raise ValueError("Invalid frequency bounds")
    f, p = compute_psd(samples, rate, nperseg=nperseg)
    max_hz = min(high_hz, f[-1])
    mask = (f >= low_hz) & (f <= max_hz)
    if np.count_nonzero(mask) < 40:
        return {"available": False, "reason": "Insufficient spectral bandwidth or resolution",
                "peak_frequencies_hz": [], "estimated_spacing_hz": None, "regularity": None}
    ff, pp = f[mask], p[mask]
    db = 10 * np.log10(np.maximum(pp, 1e-20))
    bin_hz = float(np.median(np.diff(ff)))
    baseline = gaussian_filter1d(db, sigma=max(2.0, 180.0 / bin_hz))
    residual = db - baseline
    peaks, properties = signal.find_peaks(residual, prominence=prominence_db,
                                          distance=max(1, int(30 / bin_hz)))
    freqs = ff[peaks]
    if len(freqs) < min_peaks:
        return {"available": True, "peak_frequencies_hz": freqs.tolist(),
                "peak_count": int(len(freqs)), "estimated_spacing_hz": None,
                "regularity": None, "candidate_periodicity": False,
                "reason": "Too few prominent peaks for periodicity estimation"}
    # Peak sequences can have missing members. Report consecutive spacing as a
    # descriptive statistic, not a validated synthetic-audio signature.
    spacings = np.diff(freqs)
    spacing = float(np.median(spacings))
    dispersion = float(np.median(np.abs(spacings - spacing)) / max(spacing, 1e-10))
    regularity = float(1 / (1 + dispersion))
    # Conservative upper bound: consistency alone is not an AI indicator.
    return {"available": True, "peak_frequencies_hz": freqs.tolist(),
            "peak_count": int(len(freqs)), "estimated_spacing_hz": spacing,
            "relative_spacing_mad": dispersion, "regularity": regularity,
            "mean_prominence_db": float(np.mean(properties["prominences"])),
            "candidate_periodicity": bool(len(freqs) >= min_peaks and dispersion < .20),
            "reason": "Regular tonal/harmonic peaks are an alternative explanation; origin unknown"}
