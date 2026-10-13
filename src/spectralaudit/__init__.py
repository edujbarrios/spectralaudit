"""SpectralAudit: reproducible, offline spectral diagnostics for music and audio."""
from __future__ import annotations

from pathlib import Path

import numpy as np

from .audio import load_audio
from .comb import detect_comb
from .fingerprint import analyze_fingerprint
from .confounders import inspect_confounders
from .models import AuditReport
from .spectrum import analyze_frequencies
from .temporal import analyze_temporal

__version__ = "0.3.0"
__all__ = ["analyze", "analyze_frequencies", "detect_comb", "analyze_temporal",
           "load_audio", "analyze_fingerprint", "AuditReport"]


def analyze(path: str | Path, *, modules: tuple[str, ...] | list[str] = (
    "high_frequency", "spectral_comb", "synthetic_patterns", "temporal", "confounders"
)) -> AuditReport:
    """Analyze audio with explicitly requested DSP modules, never determine AI origin."""
    audio = load_audio(path)
    data = audio.mono
    selection = "mono" if audio.samples.shape[1] == 1 else "channel_average"
    if audio.samples.shape[1] > 1:
        powers = np.sqrt(np.mean(np.square(audio.samples), axis=0))
        strongest = int(np.argmax(powers))
        mono_power = float(np.sqrt(np.mean(data * data)))
        if powers[strongest] > 1e-9 and mono_power < 0.15 * powers[strongest]:
            data = audio.samples[:, strongest]
            selection = f"channel_{strongest}_anti_phase_fallback"
    valid = {"high_frequency", "spectral_comb", "synthetic_patterns", "temporal", "confounders"}
    if unknown := set(modules) - valid:
        raise ValueError(f"Unknown analysis modules: {sorted(unknown)}")
    findings: dict = {}
    freq = analyze_frequencies(data, audio.rate) if "high_frequency" in modules or "confounders" in modules else None
    comb = detect_comb(data, audio.rate) if "spectral_comb" in modules or "confounders" in modules else None
    if "high_frequency" in modules:
        findings["high_frequency"] = freq
    if "spectral_comb" in modules:
        findings["spectral_comb"] = comb
    if "synthetic_patterns" in modules:
        findings["synthetic_patterns"] = analyze_fingerprint(data, audio.rate)
    if "temporal" in modules:
        findings["temporal"] = analyze_temporal(data, audio.rate)
    if "confounders" in modules:
        findings["confounders"] = inspect_confounders(audio.metadata, freq, comb)
    return AuditReport(
        metadata={**audio.metadata, "analysis_signal": selection}, findings=findings,
        limitations=["Frequency-domain heuristics are not verified AI provenance indicators.",
                     "Lossy encoding, mastering, harmonic instruments, and source bandwidth can confound measurements.",
                     "Whole-file read may require substantial RAM; no streaming interface.",
                     "Cutoff and periodicity thresholds are experimental and not calibrated on real-world corpora.",
                     "Suno and other generators cannot be identified reliably from a single spectral test."],
    )
