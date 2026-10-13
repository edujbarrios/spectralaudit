"""SpectralAudit: reproducible, offline spectral diagnostics for music and audio."""
from __future__ import annotations

from pathlib import Path

from .audio import load_audio
from .comb import detect_comb
from .confounders import inspect_confounders
from .mastering import audit_pipeline, compare_masters
from .models import AuditReport
from .spectrum import analyze_frequencies
from .temporal import analyze_temporal

__version__ = "0.1.0"
__all__ = ["analyze", "analyze_frequencies", "detect_comb", "analyze_temporal",
           "load_audio", "compare_masters", "audit_pipeline", "AuditReport"]


def analyze(path: str | Path, *, modules: tuple[str, ...] | list[str] = (
    "high_frequency", "spectral_comb", "temporal", "confounders"
)) -> AuditReport:
    """Analyze audio with explicitly requested DSP modules, never determine AI origin."""
    audio = load_audio(path)
    valid = {"high_frequency", "spectral_comb", "temporal", "confounders"}
    if unknown := set(modules) - valid:
        raise ValueError(f"Unknown analysis modules: {sorted(unknown)}")
    findings: dict = {}
    freq = analyze_frequencies(audio.mono, audio.rate) if "high_frequency" in modules or "confounders" in modules else None
    comb = detect_comb(audio.mono, audio.rate) if "spectral_comb" in modules or "confounders" in modules else None
    if "high_frequency" in modules:
        findings["high_frequency"] = freq
    if "spectral_comb" in modules:
        findings["spectral_comb"] = comb
    if "temporal" in modules:
        findings["temporal"] = analyze_temporal(audio.mono, audio.rate)
    if "confounders" in modules:
        findings["confounders"] = inspect_confounders(audio.metadata, freq, comb)
    return AuditReport(
        metadata=audio.metadata, findings=findings,
        limitations=["Frequency-domain heuristics are not verified AI provenance indicators.",
                     "Lossy encoding, mastering, harmonic instruments, and source bandwidth can confound measurements.",
                     "Whole-file read may require substantial RAM; no streaming interface in v0.1.",
                     "Cutoff and periodicity thresholds are experimental and not calibrated on real-world corpora."],
    )
