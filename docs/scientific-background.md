# Scientific background

A Fourier-domain analysis of machine-generated audio is motivated by research
into architectural reconstruction artifacts and the limitations of real-world
provenance detection (Afchar et al., 2025; Cros Vila et al., 2025).

SpectralAudit does not reproduce the commercial Deezer detector, does not
include its code, and has not validated a method that identifies generative
origin. The signal-processing formulas implemented here draw from conventional
Welch PSD and Fourier spectral analysis. See [REFERENCES.md](../REFERENCES.md).

Frequency-domain artifacts should always be interpreted with alternative
causes in mind. A low-pass cutoff near 17 kHz can result from MP3 encoding,
source format or EQ, not necessarily a generative pipeline.
