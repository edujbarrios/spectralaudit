# Reproducible validation

Run `python -m pytest -q` with dependencies installed.

The tests generate deterministic sine waves, harmonic tones, Gaussian noise,
filtered noise, silence, and gain-changed signals. They test supported sampling
rates and correct Nyquist availability handling, PSD frequency localization,
invalid inputs, deterministic periodic high-frequency signals, and conservative interpretation.

## How to validate provenance claims externally

To assess the strength of any artifact as an origin indicator, assemble an
independent rights-cleared corpus with matched sample rates, codecs,
compression, loudness, genres, and mastering. Use source-level held-out splits;
never put near-identical tracks on both sides. Report false-positive rates,
precision-recall, abstentions and confidence intervals. Include ordinary
synthesizers and electronic music as hard negatives. Maintain a separate
blindly held-out corpus from unseen generators.

The version 0.2.0 project currently has **no validated AI-detection sensitivity or
specificity**. The absence of such a benchmark is intentionally disclosed.
