# Quickstart (v0.3)

```bash
pip install -U spectralaudit
spectralaudit analyze song.wav --json report.json
spectralaudit analyze song.wav --markdown report.md
spectralaudit analyze song.wav --text report.txt
spectralaudit fingerprint song.wav
spectralaudit fingerprint song.wav --json fingerprint.json
```

```python
from spectralaudit import analyze, analyze_fingerprint, load_audio

report = analyze("song.wav")
print(report.findings["synthetic_patterns"]["candidate_pattern"])
print(report.findings["synthetic_patterns"]["interpretation"])
report.to_json("report.json")
report.to_markdown("report.md")
report.to_text("report.txt")

audio = load_audio("song.wav")
print(analyze_fingerprint(audio.mono, audio.rate))
```

The output describes measured structures, not an AI/Suno provenance verdict.

A reproducible WAV and all three reports are checked into [`examples/`](../examples/).
