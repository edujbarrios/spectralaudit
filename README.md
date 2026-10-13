# SpectralAudit

**Explainable, offline spectral forensics for music and mastered audio.**

[![CI](https://github.com/edujbarrios/spectralaudit/actions/workflows/ci.yml/badge.svg)](https://github.com/edujbarrios/spectralaudit/actions/workflows/ci.yml)

**Author:** Eduardo J. Barrios · [How to cite](CITING.md) · [Scientific references](REFERENCES.md)

> **Not an AI music classifier.** No threshold at 17 kHz—or any single spectral
> artifact—proves that a recording was generated with artificial intelligence.
> This library reports numerical measurements and explicit limitations.

## What works in v0.1

- Analyze WAV/FLAC (local file), sample rate, peak, RMS and SHA-256.
- Measure Welch PSD across high-frequency bands, respecting Nyquist limits.
- Estimate candidate spectral cutoff knees using a documented heuristic.
- Inspect spectral-envelope residuals for regularly spaced peaks.
- Evaluate periodicity candidates across time windows.
- Flag possible conventional confounders, rather than assert AI origin.
- Compare aligned premaster/master audio, gain estimates and spectral changes.
- Export JSON and standalone HTML with detailed numerical evidence.
- CLI: `analyze`, `spectrum`, `compare`, and `batch`.

**Status:** early research software. Cutoff and periodicity thresholds are
experimental, uncalibrated heuristics. They are not a validated AI-origin detector.

## Install (development checkout)

```bash
python -m venv .venv
source .venv/bin/activate    # Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
pytest -q
```

Once released on PyPI, install with `pip install spectralaudit`.

## Python quickstart

```python
from spectralaudit import analyze, compare_masters

report = analyze("final_master.wav")
print(report.findings["high_frequency"])
print(report.interpretation)
report.to_json("master.json")
report.to_html("master.html")

comparison = compare_masters("premaster.wav", "final_master.wav")
print(comparison.spectral_changes)
```

## CLI

```bash
spectralaudit analyze final_master.wav --json result.json --html report.html
spectralaudit spectrum final_master.wav
spectralaudit compare premaster.wav final_master.wav --html comparison.html
spectralaudit batch music/ --json batch.json
```

## Implementation and limits

Algorithms are based on NumPy/SciPy/SoundFile; no LLM, neural model, API key or
network access is required. Welch PSD, robust smoothed log-spectrum slope and
peak-spacing heuristics are independently implemented. Spectral periodicity
also arises in normal musical instrument harmonics. Current full-file reading
uses RAM proportional to the file duration. Files remain unmodified.

See [Algorithm notes](docs/algorithms.md) and [Limitations](docs/limitations.md).

## Open source and scholarly citation

Copyright 2026 **Eduardo J. Barrios**. Licensed under **Apache-2.0**, with
applicable attribution/NOTICE retention obligations for redistributions.

**If you use SpectralAudit in research, please cite the author and the software
version using [`CITATION.cff`](CITATION.cff) or [`CITING.md`](CITING.md).**
Academic citation is requested; this is not an added legal restriction under
Apache-2.0. See [NOTICE](NOTICE).

## Scientific boundaries

A frequency cutoff, spectral periodicity, or anomalous high-frequency energy is
not a validated proof of synthetic origin. Low sample rates, EQ, lossy codecs,
and harmonically rich instruments can confound interpretation. Results should
be reported as measurements and limitations, not a probability of AI generation.
