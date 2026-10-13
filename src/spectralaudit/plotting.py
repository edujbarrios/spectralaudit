"""Stand-alone inline SVG PSD plot, no JavaScript or network dependencies."""
from __future__ import annotations

import numpy as np

from .spectrum import compute_psd


def spectral_svg(samples: np.ndarray, sample_rate: int, *, max_points: int = 640) -> str:
    freq, psd = compute_psd(samples, sample_rate)
    db = 10 * np.log10(np.maximum(psd, 1e-20))
    lo = float(np.percentile(db, 5))
    hi = float(np.percentile(db, 99))
    if hi - lo < 1:
        hi = lo + 1
    indices = np.unique(np.linspace(0, len(freq)-1, min(len(freq), max_points)).astype(int))
    width, height = 860, 260
    points = []
    for idx in indices:
        x = 45 + 790 * float(freq[idx] / max(freq[-1], 1))
        y = 225 - 190 * np.clip((db[idx]-lo)/(hi-lo), 0, 1)
        points.append(f"{x:.1f},{y:.1f}")
    labels = "".join(
        f'<text x="{45+790*f/max(freq[-1],1):.0f}" y="245" font-size="11" '
        f'fill="#bac9cd" text-anchor="middle">{f/1000:.0f}k</text>'
        for f in [0, 5000, 10000, 15000, 20000] if f <= freq[-1]
    )
    return (
        '<figure><figcaption><strong>Power spectral density (dB/Hz)</strong>'
        ' — logarithmic power scale; visualization only</figcaption>'
        f'<svg viewBox="0 0 {width} {height}" role="img" '
        'aria-label="Spectral power density vs frequency" '
        'style="width:100%;background:#101923;border-radius:9px">'
        '<path d="M45 20 V225 H835" fill="none" stroke="#81939a"/>'
        f'<polyline points="{" ".join(points)}" fill="none" '
        'stroke="#32c0b4" stroke-width="1.6"/>'
        f'{labels}</svg></figure>'
    )
