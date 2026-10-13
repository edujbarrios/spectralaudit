# Changelog

## [0.2.0] - 2026-10-13

- **Breaking change:** remove premaster/master comparison, its CLI, and public APIs.
- Add independent deterministic spectral fingerprint analysis of persistent high-frequency peaks (temporal median, frequency autocorrelation, and peak-spacing metrics).
- Add `spectralaudit fingerprint` CLI and `analyze_fingerprint` Python API.
- Add synthetic-signal tests and cautions against Suno/AI attribution claims.
- Add PyPI badges and full research citations directly to README.

## [0.1.0] - 2026-10-13

Initial implementation of offline spectral diagnostics: WAV/FLAC ingestion,
Welch PSD and Nyquist-aware frequency bands, candidate cutoff heuristic,
periodic spectral peak heuristic, temporal summaries, conventional confounder
flags, premaster/master comparison, JSON/HTML export, CLI, tests, and packaging.

No validated AI-origin classification is offered.

Initial public release: clarified README and research citation, fixed missing-directory batch input handling, and added release tag/version checks and tests to the publishing workflow.
