# Quickstart (v0.2)

```bash
pip install -U spectralaudit
spectralaudit analyze song.wav --json report.json --html report.html
spectralaudit fingerprint song.wav --json fingerprint.json
```

```python
from spectralaudit import analyze, analyze_fingerprint, load_audio

report = analyze("song.wav")
print(report.findings["synthetic_patterns"]["candidate_pattern"])
print(report.findings["synthetic_patterns"]["interpretation"])
report.to_html("report.html")

audio = load_audio("song.wav")
print(analyze_fingerprint(audio.mono, audio.rate))
```

The output describes measured structures, not an AI/Suno provenance verdict.
