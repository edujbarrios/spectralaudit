"""Generate non-AI test audio and exercise the public API."""
from pathlib import Path
import tempfile

import numpy as np
import soundfile as sf

from spectralaudit import analyze, compare_masters

with tempfile.TemporaryDirectory() as folder:
    path = Path(folder)
    fs = 44100
    t = np.arange(2 * fs) / fs
    samples = 0.2 * np.sin(2 * np.pi * 440 * t)
    sf.write(path / "premaster.wav", samples, fs)
    sf.write(path / "master.wav", samples * .8, fs)
    report = analyze(path / "master.wav")
    print(report.interpretation)
    print(report.findings["high_frequency"]["nyquist_hz"])
    comparison = compare_masters(path / "premaster.wav", path / "master.wav")
    print(comparison.metadata["estimated_gain"])
