"""Power spectral density, band energy, and candidate low-pass knees."""
from __future__ import annotations

import numpy as np
from scipy import signal
from scipy.integrate import trapezoid

DEFAULT_BANDS = [(5000, 10000), (10000, 12000), (12000, 16000),
                 (16000, 17000), (17000, 19000), (19000, 21000)]


def compute_psd(samples: np.ndarray, rate: int, *, nperseg: int = 8192) -> tuple[np.ndarray, np.ndarray]:
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1 or not x.size or rate <= 0:
        raise ValueError("Expected nonempty 1D samples and positive sample rate")
    f, p = signal.welch(x, fs=rate, nperseg=min(nperseg, x.size),
                        window="hann", detrend="constant", scaling="density")
    return f, p


def _power(f: np.ndarray, p: np.ndarray, lo: float, hi: float) -> float:
    mask = (f >= lo) & (f <= hi)
    if np.count_nonzero(mask) < 2:
        return 0.0
    return float(trapezoid(p[mask], f[mask]))


def estimate_cutoff(f: np.ndarray, p: np.ndarray, *, min_hz: float = 3000) -> dict:
    """Find steep high-frequency drops via smoothing and log-power derivative.

    Heuristic, not a proven codec detector or generative-origin classifier.
    """
    valid = (f >= min_hz) & (f <= f[-1] * .98)
    if np.count_nonzero(valid) < 30:
        return {"candidate_hz": None, "steepness_db_per_khz": None, "method": "insufficient_band"}
    ff, pp = f[valid], p[valid]
    # Aggregate into 150 Hz bins to avoid narrow tonal peaks.
    bw = 150.0
    bin_ids = np.floor((ff - ff[0]) / bw).astype(int)
    centers, db = [], []
    for idx in np.unique(bin_ids):
        vals = pp[bin_ids == idx]
        centers.append(float(np.median(ff[bin_ids == idx])))
        db.append(float(10 * np.log10(max(float(np.median(vals)), 1e-20))))
    centers, db = np.asarray(centers), np.asarray(db)
    if len(db) < 9:
        return {"candidate_hz": None, "steepness_db_per_khz": None, "method": "insufficient_bins"}
    from scipy.ndimage import median_filter
    smooth = median_filter(db, size=5, mode="nearest")
    slopes = np.gradient(smooth, centers) * 1000
    # Sharp knee must exceed an intentionally conservative heuristic threshold.
    i = int(np.argmin(slopes))
    return {"candidate_hz": round(float(centers[i]), 1) if slopes[i] < -35 else None,
            "steepness_db_per_khz": round(float(slopes[i]), 2),
            "heuristic_threshold_db_per_khz": -35.0, "method": "median_binned_log_psd_slope"}


def analyze_frequencies(samples: np.ndarray, rate: int, *, bands=None) -> dict:
    f, p = compute_psd(samples, rate)
    bands = DEFAULT_BANDS if bands is None else bands
    nyquist = rate / 2
    total = _power(f, p, 0, nyquist)
    output = []
    for lo, hi in bands:
        if lo < 0 or hi <= lo:
            raise ValueError("Band limits must satisfy 0 <= lower < upper")
        if hi > nyquist:
            output.append({"band_hz": [lo, hi], "available": False,
                           "power": None, "relative_power": None})
        else:
            power = _power(f, p, lo, hi)
            output.append({"band_hz": [lo, hi], "available": True,
                           "power": power, "relative_power": power / total if total > 0 else None})
    mask = (f >= 1000) & (f <= nyquist)
    flatness = None
    if np.count_nonzero(mask) > 2:
        pp = p[mask]
        flatness = float(np.exp(np.mean(np.log(pp + 1e-20))) / (np.mean(pp) + 1e-20))
    return {"nyquist_hz": nyquist, "bands": output, "spectral_flatness_above_1khz": flatness,
            "candidate_cutoff": estimate_cutoff(f, p), "method": "Welch PSD; Hann window"}
