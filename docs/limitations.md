# Scope, interpretation and limitations

**No binary detection or model-based AI attribution is implemented.** The
program is an offline DSP measurement tool. Use `report.interpretation` rather
than inferring AI-origin probabilities from heuristic findings.

- A spectral cutoff at 17 kHz has many non-generative explanations.
- Repeated peaks can originate from harmonically rich instruments or synthesis.
- In a 32 kHz file, frequencies above 16 kHz cannot be observed.
- Prior codecs, resampling, filtering, and mastering can obscure provenance.
- The original encoding chain cannot be recovered from one processed WAV.
- The current implementation loads entire files into memory, which may be
  expensive for long songs or high sample rates.
- Peak spacing and cutoff heuristics lack real-dataset sensitivity and
  specificity evaluation; v0.1 makes no accuracy claims.
- Master comparison assumes sufficiently similar waveforms, gain and time
  alignment; remixes, extensive time-stretching and nonlinear editing can fail.
- HTML reports include a lightweight PSD figure when the source audio remains
  available; they do not show a full STFT spectrogram or interactive plots.

If decisions affect artists' livelihoods, intellectual property disputes or
platform enforcement, **do not use SpectralAudit alone** as evidence of provenance.
