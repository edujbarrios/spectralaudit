"""Checked-in WAV and output snapshots must reflect actual signal analysis."""
import json
from pathlib import Path

from spectralaudit import analyze

ROOT = Path(__file__).resolve().parents[1]
SAMPLE = ROOT / "examples" / "assets" / "synthetic_spectral_comb.wav"
RESULTS = ROOT / "examples" / "results"


def test_deterministic_checked_in_example(monkeypatch):
    monkeypatch.chdir(ROOT)
    report = analyze("examples/assets/synthetic_spectral_comb.wav",
                     modules=["synthetic_patterns"])
    pattern = report.findings["synthetic_patterns"]
    assert SAMPLE.stat().st_size == 529244
    assert report.metadata["sha256"] == (
        "add58b1f1516f4f2993fd5f5c3a81a1a434159370cca9a78b78a5385220e1178"
    )
    assert pattern["candidate_pattern"]
    assert abs(pattern["estimated_spacing_hz"] - 440) < 5
    assert pattern["origin_attribution"] == "not_supported"
    assert json.loads((RESULTS / "synthetic_spectral_comb.json").read_text()) == report.as_dict()
    assert (RESULTS / "synthetic_spectral_comb.md").read_text() == report.as_markdown()
    assert (RESULTS / "synthetic_spectral_comb.txt").read_text() == report.as_text()
