"""Cautious alternative explanations grounded in observable signal properties."""
from __future__ import annotations


def inspect_confounders(metadata: dict, frequency: dict, comb: dict) -> list[dict]:
    result: list[dict] = []
    nyquist = frequency["nyquist_hz"]
    if nyquist < 21000:
        result.append({"type": "limited_bandwidth", "observation": f"Nyquist is {nyquist:g} Hz",
                       "explanation": "High-frequency bands above Nyquist cannot be measured."})
    cutoff = frequency["candidate_cutoff"].get("candidate_hz")
    if cutoff is not None:
        result.append({"type": "spectral_cutoff", "observation": f"Candidate knee at {cutoff:g} Hz",
                       "explanation": "EQ, low-pass filtering, prior encoding or content may explain the drop. Codec and origin unknown."})
    if metadata["clipped_sample_fraction"] > 0.001:
        result.append({"type": "sample_clipping", "observation": "Sample values approach full scale",
                       "explanation": "Clipping and limiting may change the spectrum."})
    if comb.get("candidate_periodicity"):
        result.append({"type": "tonal_confounder", "observation": "Regularly spaced spectral peaks",
                       "explanation": "Harmonic instruments and oscillators can create similar structures."})
    if not result:
        result.append({"type": "none_detected", "observation": "No configured flags raised",
                       "explanation": "Absence of flags is not evidence of human origin."})
    return result
