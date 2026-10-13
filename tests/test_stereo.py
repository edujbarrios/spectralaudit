"""Prevent near-zero downmix from erasing spectral evidence."""
import numpy as np
import soundfile as sf

from spectralaudit import analyze


def test_antiphase_signal_uses_strongest_channel(tmp_path):
    rate = 44100
    t = np.arange(rate * 6) / rate
    signal = .2 * np.sin(2 * np.pi * 6200 * t)
    path = tmp_path / "anti.wav"
    sf.write(path, np.column_stack((signal, -signal)), rate)
    report = analyze(path, modules=["synthetic_patterns"])
    assert report.metadata["analysis_signal"] == "channel_0_anti_phase_fallback"
    assert report.findings["synthetic_patterns"]["available"]


def test_normal_stereo_uses_average(tmp_path):
    rate = 44100
    signal = np.full(rate * 3, 0.2, dtype=np.float64)
    path = tmp_path / "normal.wav"
    sf.write(path, np.column_stack((signal, signal)), rate)
    report = analyze(path, modules=["synthetic_patterns"])
    assert report.metadata["analysis_signal"] == "channel_average"
