"""Create a reproducible WAV spectral-comb test fixture; this is NOT AI music."""
from pathlib import Path
import numpy as np
import soundfile as sf

RATE = 44100
SECONDS = 6
OUT = Path(__file__).parent / "assets" / "synthetic_spectral_comb.wav"


def main() -> None:
    frames = RATE * SECONDS
    t = np.arange(frames) / RATE
    audio = np.zeros(frames, dtype=np.float64)
    for freq in range(6100, 14901, 440):
        audio += 0.013 * np.sin(2 * np.pi * freq * t)
    state = 19
    for i in range(frames):
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        state &= 0xFFFFFFFF
        audio[i] += (state / 2**32 - 0.5) * 0.104
    OUT.parent.mkdir(exist_ok=True, parents=True)
    sf.write(OUT, audio, RATE, subtype="PCM_16")
    print(OUT)


if __name__ == "__main__":
    main()
