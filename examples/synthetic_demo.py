"""Synthetic demonstration: not a recording from a music generator."""
from pathlib import Path
import tempfile
import numpy as np
import soundfile as sf
from spectralaudit import analyze

with tempfile.TemporaryDirectory() as folder:
    path=Path(folder)/"artificial_comb.wav"
    rate=44100
    t=np.arange(rate*9)/rate
    x=0.03*np.random.default_rng(2026).normal(size=len(t))
    for f in range(6100,14900,440):
        x+=0.013*np.sin(2*np.pi*f*t)
    sf.write(path,x,rate)
    r=analyze(path)
    print(r.interpretation)
    print(r.findings["synthetic_patterns"])
