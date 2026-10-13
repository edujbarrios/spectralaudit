# Installation

Requirements: Python 3.11+, NumPy, SciPy, and SoundFile. No LLM or GPU needed.

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -U pip
python -m pip install -e '.[dev]'
python -m pytest -q
spectralaudit --help
```

Windows PowerShell activation: `.venv\Scripts\Activate.ps1`.

For a published release, use `python -m pip install spectralaudit`.
Audio support relies on the libsndfile build supplied by your SoundFile
installation; WAV/FLAC availability may vary by platform.
