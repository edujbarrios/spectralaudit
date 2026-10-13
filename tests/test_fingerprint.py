"""Deterministic test signals; not real-world generator validation."""
import json
import numpy as np
import pytest
from spectralaudit import analyze, analyze_fingerprint
from spectralaudit.cli import main, make_parser

def periodic_signal(rate=44100, seconds=9):
    rng = np.random.default_rng(19)
    t = np.arange(rate * seconds) / rate
    x = 0.03 * rng.normal(size=t.size)
    for f in np.arange(6100, 14900, 440):
        x += 0.013 * np.sin(2 * np.pi * f * t)
    return x

def test_controlled_periodic_high_frequency_comb():
    r = analyze_fingerprint(periodic_signal(), 44100)
    assert r["available"] and r["candidate_pattern"]
    assert r["peak_count"] >= 12
    assert abs(r["estimated_spacing_hz"] - 440) < 10
    assert r["persistence_fraction"] > .8
    assert r["autocorrelation_strength"] > .4
    assert r["origin_attribution"] == "not_supported"
    assert r["not_generator_specific"]

def test_white_noise_has_no_candidate():
    x = np.random.default_rng(25).normal(size=44100 * 9)
    assert not analyze_fingerprint(x, 44100)["candidate_pattern"]

def test_repeatability():
    x = periodic_signal()
    assert json.dumps(analyze_fingerprint(x,44100),sort_keys=True) == json.dumps(
        analyze_fingerprint(x,44100),sort_keys=True)

def test_unavailable_bands_and_short_audio():
    r = analyze_fingerprint(np.ones(8000 * 4),8000)
    assert not r["available"] and "Nyquist" in r["reason"]
    r = analyze_fingerprint(np.ones(44100),44100)
    assert not r["available"]

def test_silence():
    r=analyze_fingerprint(np.zeros(44100*6),44100)
    assert not r["available"] and r["origin_attribution"]=="not_supported"

@pytest.mark.parametrize("settings", [
    {"low_hz":17000,"high_hz":12000},{"window_seconds":0},
    {"max_windows":0},{"prominence_db":-1},{"min_peaks":2}
])
def test_bad_configuration(settings):
    with pytest.raises(ValueError):
        analyze_fingerprint(np.ones(44100*4),44100,**settings)

def test_public_api_and_cli(audio_factory,tmp_path):
    src=audio_factory()
    report=analyze(src)
    assert "synthetic_patterns" in report.findings
    assert "not_generator_specific" in report.findings["synthetic_patterns"]
    out=tmp_path/"fingerprint.json"
    assert main(["fingerprint",str(src),"--json",str(out)])==0
    assert list(json.loads(out.read_text())["findings"])==["synthetic_patterns"]
    with pytest.raises(SystemExit):
        make_parser().parse_args(["compare","old.wav","new.wav"])
