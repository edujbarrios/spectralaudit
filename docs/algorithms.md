# Numerical algorithms (v0.2.0)

These are reproducible **measurements**, not AI-origin classifications.

## Welch PSD and band energy

For real-valued waveform samples, Welch PSD uses Hann-windowed modified
periodograms averaged over overlapping windows (`scipy.signal.welch`). PSD
units are amplitude-squared per Hz. Band energy is approximated by trapezoid
integration, and relative band power is normalized by the full-band integral.

A band is **unavailable** when its upper boundary exceeds the Nyquist
frequency; unavailable is not a zero-valued observation. If there is no signal
power, relative band fractions are `null`.

## Spectral cutoff heuristic

We divide the log-PSD above 3 kHz into 150 Hz bins, take the median of each bin,
apply a 5-bin median filter, and compute the frequency derivative in dB/kHz.
The steepest negative derivative is a *candidate* knee only when it is below
-35 dB/kHz, an **uncalibrated heuristic**. Test frequencies, averaging, bins,
and signal content strongly affect this value. It is not a codec or origin detector.

## Periodic peak heuristic

We estimate the spectral envelope by Gaussian smoothing the log-PSD (smoothing
scale ~180 Hz). Narrow peaks in the residual are found using prominence and
frequency-separation thresholds. For consecutive peak spacings `d_i`, the
reported central spacing is `median(d_i)` and irregularity is
`median(|d_i - median(d_i)|) / median(d_i)`.

`candidate_periodicity=True` requires at least five peaks and an irregularity
below 0.20. This flag is **not** a published synthetic-music detection method:
ordinary harmonic music, oscillators, and other tonal signals can produce a
similar effect. Peak spacing may be poorly estimated when intermediate peaks
are absent. Treat it as an exploratory diagnostic only.

## Temporal summary

Nonoverlapping 5-second windows (up to 48 uniformly spaced representatives)
measure candidate cutoff and peak-spacing flags. Persistence is the fraction
of analyzed windows flagged, not evidence of AI provenance.

## Persistent high-frequency fingerprint (v0.2)

The `synthetic_patterns` module inspects nonoverlapping 3-second excerpts
in 5–16 kHz (configurable). For each excerpt it computes a Welch PSD,
removes a Gaussian-smoothed spectral envelope from the log-power spectrum,
and aggregates residuals using the median across non-silent excerpts.

Prominent peaks are found in the median residual. Temporal persistence
means the fraction of analyzed excerpts that support these fixed-frequency
peaks. The algorithm estimates median adjacent peak separation, its relative
median absolute deviation, and normalized autocorrelation of the residual over
60–1800 Hz frequency offsets.

The experimental `candidate_pattern` requires two non-silent windows,
five peaks, relative spacing MAD <= 0.20, peak persistence >= 0.50,
and frequency autocorrelation >= 0.15. These are **not calibrated thresholds**.
Purely harmonic electronic music can meet them. The method is independently
implemented and **not a Suno model detector**. `origin_attribution` is
always `not_supported`. When the band exceeds Nyquist or excerpts are too
short, results are unavailable, not negative.

## References

See [REFERENCES.md](../REFERENCES.md) for sources, attribution and the Deezer
code licensing notice. All DSP implementations are independent; the project
makes no claim to reproduce a published classifier or its accuracy.
