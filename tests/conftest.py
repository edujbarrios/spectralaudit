from __future__ import annotations

import numpy as np
import pytest
import soundfile as sf


@pytest.fixture
def audio_factory(tmp_path):
    def make(name="audio.wav", *, rate=44100, seconds=1., frequency=440., samples=None):
        if samples is None:
            t = np.arange(int(seconds * rate)) / rate
            samples = .3 * np.sin(2 * np.pi * frequency * t)
        path = tmp_path / name
        sf.write(path, samples, rate)
        return path
    return make
