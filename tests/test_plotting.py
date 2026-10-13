import numpy as np

from spectralaudit.plotting import spectral_svg


def test_svg_is_standalone():
    sr = 44100
    t = np.arange(sr) / sr
    svg = spectral_svg(0.5*np.sin(2*np.pi*440*t), sr)
    assert '<svg' in svg
    assert 'polyline' in svg
    assert 'http' not in svg
