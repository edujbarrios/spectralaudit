# SpectralAudit

**Offline spectral analysis for music and final masters.** A Python library by **Eduardo J. Barrios**.

[![CI](https://github.com/edujbarrios/spectralaudit/actions/workflows/ci.yml/badge.svg)](https://github.com/edujbarrios/spectralaudit/actions/workflows/ci.yml)
[![License: Apache-2.0](https://img.shields.io/badge/license-Apache--2.0-blue)](LICENSE)

SpectralAudit measures **high-frequency energy, spectral cutoffs and regularly spaced spectral peaks** in WAV/FLAC audio. It also compares a premaster and final master to reveal measurable differences between versions. Processing runs **locally** with NumPy and SciPy: no LLMs, AI models or external APIs.

**Important:** SpectralAudit is **not a validated detector of AI-generated music**. Frequencies above 17 kHz, low-pass cutoffs and periodic peaks do **not** prove AI origin. Results are measurements with stated limitations.

## Install

Requires Python 3.11+.

```bash
pip install spectralaudit
```

Before the first PyPI release, install from the repository:

```bash
pip install git+https://github.com/edujbarrios/spectralaudit.git
```

## Quick start

Analyze a master and export an HTML and JSON report:

```bash
spectralaudit analyze final_master.wav --html report.html --json report.json
```

Inspect frequency bands, compare two versions, or analyze a folder:

```bash
spectralaudit spectrum final_master.wav
spectralaudit compare premaster.wav final_master.wav --html comparison.html
spectralaudit batch ./music --json batch.json
```

Python API:

```python
from spectralaudit import analyze, compare_masters

report = analyze("final_master.wav")
print(report.findings["high_frequency"]["candidate_cutoff"])
print(report.findings["spectral_comb"]["candidate_periodicity"])
print(report.interpretation)  # Origin inconclusive: ...
report.to_html("report.html")

comparison = compare_masters("premaster.wav", "final_master.wav")
print(comparison.spectral_changes)
```

## What it measures

- **Frequency bands:** Welch power spectrum, relative band energy and candidate high-frequency cutoff, respecting the file's Nyquist limit.
- **Periodic peaks:** spacing of narrow spectral peaks; also possible in conventional harmonic music.
- **Time:** persistence of candidate patterns in successive audio windows.
- **Alternative explanations:** flags for sample-rate and processing-related ambiguities.
- **Master comparison:** estimated time offset, gain and band-level spectral differences.

The same inputs and settings produce deterministic analyses. Detection thresholds are **exploratory heuristics**, not calibrated AI-origin probabilities. Large files are read into memory; input audio is never modified. See [Methods](docs/algorithms.md) and [Limitations](docs/limitations.md).

## Research, citation and license

If you use SpectralAudit in research, **please cite Eduardo J. Barrios and the version used**. See [CITATION.cff](CITATION.cff) and [how to cite](CITING.md).

Selected scientific references:

- Afchar et al. (2025), *A Fourier Explanation of AI-music Artifacts* ([paper](https://arxiv.org/abs/2506.19108)).
- Cros Vila et al. (2025), *The AI Music Arms Race* ([DOI](https://doi.org/10.5334/tismir.254)).
- Welch (1967), *The Use of Fast Fourier Transform for the Estimation of Power Spectra* ([DOI](https://doi.org/10.1109/TAU.1967.1161901)).

Full bibliography and implementation distinctions: [REFERENCES.md](REFERENCES.md).

**Copyright © 2026 Eduardo J. Barrios.** Open source under the [Apache License 2.0](LICENSE); see [NOTICE](NOTICE). Redistribution must preserve applicable notices. Academic citation is requested, not an additional legal condition of the license.
