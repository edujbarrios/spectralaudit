import numpy as np

from spectralaudit import audit_pipeline, compare_masters


def test_equalized_gain(audio_factory):
    sr = 16000
    rng = np.random.default_rng(8)
    x = .1 * rng.normal(size=sr)
    a = audio_factory("a.wav", rate=sr, samples=x)
    b = audio_factory("b.wav", rate=sr, samples=x * .65)
    result = compare_masters(a, b)
    assert abs(result.metadata["estimated_gain"] - .65) < .005
    assert result.spectral_changes["gain_compensated_residual_rms"] < .0001
    assert result.metadata["estimated_shift_samples"] == 0


def test_stage_audit(audio_factory):
    sr = 16000
    t = np.arange(sr) / sr
    x = .1 * np.sin(2*np.pi * 400*t)
    a = audio_factory("source.wav", rate=sr, samples=x)
    b = audio_factory("master.wav", rate=sr, samples=x * .9)
    result = audit_pipeline({"premaster": a, "master": b})
    assert result["stage_comparisons"][0]["from"] == "premaster"
