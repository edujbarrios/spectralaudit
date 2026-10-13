"""Deterministic, independent DSP for persistent high-frequency patterns."""
from __future__ import annotations

import numpy as np
from scipy import signal
from scipy.ndimage import gaussian_filter1d

def analyze_fingerprint(samples: np.ndarray, rate: int, *, low_hz: float = 5000,
                        high_hz: float = 16000, window_seconds: float = 3.0,
                        max_windows: int = 32, prominence_db: float = 5.0,
                        min_peaks: int = 5) -> dict:
    """Measure persistent spectral peaks; never attribute music to a generator.

    Independent Welch-PSD, log-spectral envelope removal, temporal median
    residual, spacing and autocorrelation heuristic. Not Deezer's detector.
    """
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1 or rate <= 0 or not np.all(np.isfinite(x)):
        raise ValueError("Expected finite 1D samples and a positive sample rate")
    if not (0 <= low_hz < high_hz) or window_seconds <= 0 or max_windows < 1:
        raise ValueError("Invalid band or window parameters")
    if prominence_db <= 0 or min_peaks < 3:
        raise ValueError("prominence_db must be positive and min_peaks >= 3")
    common = {
        "method": "Welch log-PSD; Gaussian envelope removal; temporal median; "
                  "residual peak spacing and autocorrelation",
        "band_hz": [float(low_hz), float(high_hz)],
        "sample_rate_hz": rate,
        "not_generator_specific": True,
        "origin_attribution": "not_supported",
        "research_context": "Architecture-linked spectral artifacts studied in Suno/Udio; not a Suno detector",
    }

    def unavailable(reason: str) -> dict:
        return {**common, "available": False, "reason": reason,
                "candidate_pattern": False, "peak_frequencies_hz": [],
                "estimated_spacing_hz": None, "persistence_fraction": None,
                "regularity": None, "autocorrelation_strength": None, "window_count": 0}

    nyquist = rate / 2
    if high_hz > nyquist:
        return unavailable(f"Requested {high_hz:g} Hz exceeds Nyquist {nyquist:g} Hz")
    window_size = int(rate * window_seconds)
    if window_size < 1024 or len(x) < window_size:
        return unavailable("Audio is shorter than the required analysis window")
    n = len(x) // window_size
    positions = np.unique(np.linspace(0, n - 1, min(n, max_windows)).astype(int))
    residuals: list[np.ndarray] = []
    ff: np.ndarray | None = None
    for position in positions:
        chunk = x[int(position * window_size):int((position + 1) * window_size)]
        if float(np.sqrt(np.mean(chunk * chunk))) < 1e-5:
            continue
        frequencies, psd = signal.welch(
            chunk, fs=rate, nperseg=min(8192, len(chunk)), window="hann",
            scaling="density", detrend="constant",
        )
        selection = (frequencies >= low_hz) & (frequencies <= high_hz)
        if selection.sum() < 64:
            return unavailable("Insufficient spectral resolution in the selected band")
        ff = frequencies[selection]
        log_power = 10 * np.log10(np.maximum(psd[selection], 1e-20))
        hz_per_bin = float(np.median(np.diff(ff)))
        smooth = gaussian_filter1d(log_power, sigma=max(2.0, 170.0 / hz_per_bin))
        residuals.append(np.clip(log_power - smooth, -25, 35))
    if ff is None or not residuals:
        return unavailable("No non-silent windows available")
    matrix = np.stack(residuals)
    median_residual = np.median(matrix, axis=0)
    hz_per_bin = float(np.median(np.diff(ff)))
    peaks, properties = signal.find_peaks(
        median_residual, prominence=prominence_db,
        distance=max(1, round(55 / hz_per_bin)),
    )
    freqs = ff[peaks]
    peak_strengths = median_residual[peaks]
    persistence = float(np.mean(np.mean(
        matrix[:, peaks] >= max(2.0, prominence_db * 0.5), axis=0,
    ))) if len(peaks) else 0.0
    spacings = np.diff(freqs)
    spacing = float(np.median(spacings)) if spacings.size else None
    dispersion = float(np.median(np.abs(spacings - spacing)) / spacing) if (
        spacing is not None and spacing > 0
    ) else None
    regularity = 1.0 / (1.0 + dispersion) if dispersion is not None else None

    centered = median_residual - np.mean(median_residual)
    numerator = signal.correlate(centered, centered, mode="full", method="fft")
    pos = numerator[len(centered) - 1:]
    den = max(float(pos[0]), 1e-20)
    lag_min = max(1, int(60 / hz_per_bin))
    lag_max = min(len(pos) - 1, int(1800 / hz_per_bin))
    if lag_max >= lag_min and den > 1e-18:
        loc = int(np.argmax(pos[lag_min:lag_max + 1])) + lag_min
        autocorr = max(0.0, min(1.0, float(pos[loc] / den)))
        autocorr_spacing = float(loc * hz_per_bin)
    else:
        autocorr = 0.0
        autocorr_spacing = None

    candidate = bool(len(residuals) >= 2 and len(peaks) >= min_peaks
                     and dispersion is not None and dispersion <= 0.2
                     and persistence >= 0.5 and autocorr >= 0.15)
    return {
        **common, "available": True,
        "analyzed_window_count": len(residuals), "total_full_windows": int(n),
        "peak_frequencies_hz": np.round(freqs, 2).tolist(),
        "peak_count": int(len(peaks)), "estimated_spacing_hz": spacing,
        "relative_spacing_mad": dispersion, "regularity": regularity,
        "mean_peak_residual_db": float(np.mean(peak_strengths)) if len(peaks) else None,
        "mean_peak_prominence_db": float(np.mean(properties["prominences"])) if len(peaks) else None,
        "persistence_fraction": persistence, "autocorrelation_spacing_hz": autocorr_spacing,
        "autocorrelation_strength": round(autocorr, 12), "candidate_pattern": candidate,
        "interpretation": (
            "Persistent periodic high-frequency structure found; may be compatible with "
            "architecture-linked artifacts but is not unique to AI music or Suno."
            if candidate else
            "No persistent pattern met these experimental thresholds; AI origin cannot be excluded."
        ),
    }
