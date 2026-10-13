"""Alignment and stage comparisons; causal attribution is intentionally excluded."""
from __future__ import annotations

from math import gcd
from pathlib import Path

import numpy as np
from scipy import signal

from .audio import Audio, load_audio
from .comb import detect_comb
from .models import MasterComparison
from .spectrum import analyze_frequencies, compute_psd


def _resample(x: np.ndarray, from_rate: int, to_rate: int) -> np.ndarray:
    if from_rate == to_rate:
        return x
    common = gcd(from_rate, to_rate)
    return signal.resample_poly(x, to_rate // common, from_rate // common, axis=0)


def _lag(a: np.ndarray, b: np.ndarray, sr: int) -> int:
    """Cross-correlate representative decimated mono snippets, returning shift in frames."""
    max_len = int(sr * 8)
    decimation = max(1, sr // 4000)
    aa, bb = a[:max_len:decimation], b[:max_len:decimation]
    aa = aa - np.mean(aa)
    bb = bb - np.mean(bb)
    if len(aa) < 16 or len(bb) < 16 or np.std(aa) < 1e-12 or np.std(bb) < 1e-12:
        return 0
    corr = signal.correlate(bb, aa, mode="full", method="fft")
    lags = signal.correlation_lags(len(bb), len(aa), mode="full")
    return int(lags[np.argmax(corr)] * decimation)


def _align(a: np.ndarray, b: np.ndarray, shift: int) -> tuple[np.ndarray, np.ndarray]:
    # positive lag: b is delayed relative to a
    if shift > 0:
        b = b[shift:]
    elif shift < 0:
        a = a[-shift:]
    n = min(len(a), len(b))
    if n < 32:
        raise ValueError("Signals have insufficient overlapping samples after alignment")
    return a[:n], b[:n]


def compare_masters(original: str | Path, master: str | Path) -> MasterComparison:
    """Compare two signals after time alignment and robust gain estimation."""
    a: Audio = load_audio(original)
    b: Audio = load_audio(master)
    aa = a.mono
    bb = _resample(b.mono, b.rate, a.rate)
    lag = _lag(aa, bb, a.rate)
    x, y = _align(aa, bb, lag)
    energy = float(np.dot(x, x))
    gain = float(np.dot(x, y) / energy) if energy > 1e-20 else None
    # Equalize predicted linear gain before residual measurement.
    residual = y - (gain or 0) * x
    rms_residual = float(np.sqrt(np.mean(residual ** 2)))
    f1, p1 = compute_psd(x, a.rate)
    f2, p2 = compute_psd(y, a.rate)
    assert np.allclose(f1, f2)
    # PSD dB ratio (reported as measurement only, not causal diagnosis).
    ratio_db = 10 * np.log10((p2 + 1e-20) / (p1 + 1e-20))
    bins = [(0, 200), (200, 2000), (2000, 8000), (8000, min(16000, a.rate / 2))]
    band_changes = []
    for lo, hi in bins:
        mask = (f1 >= lo) & (f1 <= hi)
        if hi <= lo or np.count_nonzero(mask) < 2:
            continue
        band_changes.append({"band_hz": [lo, hi], "median_delta_db": float(np.median(ratio_db[mask]))})
    c1, c2 = detect_comb(x, a.rate), detect_comb(y, a.rate)
    detected_new = bool(c2.get("candidate_periodicity") and not c1.get("candidate_periodicity"))
    new = ([{"type": "periodic_peaks_candidate", "description":
             "Periodic peak heuristic crossed threshold in the master but not original."}]
           if detected_new else [])
    return MasterComparison(
        metadata={"original": a.metadata, "master": b.metadata,
                  "aligned_frames": len(x), "analysis_rate_hz": a.rate,
                  "estimated_shift_samples": lag, "estimated_gain": gain},
        spectral_changes={"median_band_delta_db": band_changes,
                          "gain_compensated_residual_rms": rms_residual,
                          "original_cutoff": analyze_frequencies(x, a.rate)["candidate_cutoff"],
                          "master_cutoff": analyze_frequencies(y, a.rate)["candidate_cutoff"]},
        new_artifacts=new,
        limitations=["Cross-correlation estimates offset on a short early snippet; complex edits can invalidate alignment.",
                     "A new detected pattern is not proof that mastering created it: content and signal nonlinearities matter.",
                     "No provenance or AI-generation classification is performed."],
    )


def audit_pipeline(stages: dict[str, str | Path]) -> dict:
    """Compare consecutive stages in insertion order; all stages are supplied explicitly."""
    if len(stages) < 2:
        raise ValueError("Expected at least two named stages")
    names = list(stages)
    results = []
    for previous, current in zip(names, names[1:]):
        report = compare_masters(stages[previous], stages[current])
        results.append({"from": previous, "to": current,
                        "findings": report.spectral_changes, "new_artifacts": report.new_artifacts,
                        "limitations": report.limitations})
    return {"stage_comparisons": results, "caveat": "Sequence of measured differences, not proof of causation"}
