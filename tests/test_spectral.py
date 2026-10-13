import json

import numpy as np
import pytest

from spectralaudit import analyze, analyze_frequencies, detect_comb
from spectralaudit.audio import load_audio
from spectralaudit.spectrum import compute_psd, estimate_cutoff


@pytest.mark.parametrize("rate", [16000, 22050, 32000, 44100, 48000, 96000])
def test_nyquist_bands(audio_factory, rate):
    path = audio_factory(rate=rate)
    result = analyze_frequencies(load_audio(path).mono, rate)
    for band in result["bands"]:
        assert band["available"] == (band["band_hz"][1] <= rate / 2)
        if not band["available"]:
            assert band["power"] is None
    assert result["nyquist_hz"] == rate / 2


def test_conservative_origin(audio_factory, tmp_path):
    path = audio_factory()
    report = analyze(path)
    assert "inconclusive" in report.interpretation.lower()
    assert not any("ai_probability" in key for key in report.as_dict())
    assert report.metadata["sha256"]
    assert report.findings["high_frequency"]["bands"]
    json_path = report.to_json(tmp_path / "report.json")
    html_path = report.to_html(tmp_path / "report.html")
    data = json.loads(json_path.read_text())
    assert data["metadata"]["samplerate_hz"] == 44100
    assert "SpectralAudit" in html_path.read_text()
    assert "<svg" in html_path.read_text()


def test_peak_frequency():
    sr = 48000
    t = np.arange(sr) / sr
    f, psd = compute_psd(np.sin(2 * np.pi * 880 * t), sr)
    assert abs(f[np.argmax(psd)] - 880) < 10


def test_short_audio_and_silence(audio_factory):
    sr = 8000
    p = audio_factory("short.wav", rate=sr, samples=np.zeros(128))
    report = analyze(p)
    assert report.findings["temporal"]["available"] is False
    assert report.findings["spectral_comb"]["available"] is False
    assert report.metadata["rms_amplitude"] == 0


def test_cutoff_is_experimental_and_not_origin_proof():
    rate = 48000
    rng = np.random.default_rng(42)
    signal = rng.standard_normal(rate * 2)
    from scipy import signal as spsignal
    filtered = spsignal.sosfiltfilt(spsignal.butter(8, 14000, fs=rate, output="sos"), signal)
    f, p = compute_psd(filtered, rate)
    cutoff = estimate_cutoff(f, p)
    assert "method" in cutoff
    # Detection may vary with PSD resolution; no origin attribution is allowed.
    assert not any("ai" in key for key in cutoff)


def test_comb_regular_harmonics_do_not_claim_ai():
    rate = 48000
    t = np.arange(rate * 2) / rate
    x = sum(np.sin(2 * np.pi * (200 * k) * t) / k for k in range(25, 90))
    result = detect_comb(x, rate)
    assert "candidate_periodicity" in result
    assert "ai_probability" not in result


def test_invalid_frequency_and_modules(audio_factory):
    with pytest.raises(ValueError):
        detect_comb(np.ones(1000), 44100, low_hz=20000, high_hz=10000)
    with pytest.raises(ValueError):
        analyze(audio_factory(), modules=["bogus"])
