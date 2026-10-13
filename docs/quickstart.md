# Quickstart

```python
from spectralaudit import analyze, compare_masters, audit_pipeline

r = analyze('master.wav')
print(r.metadata['samplerate_hz'])
print(r.findings['high_frequency']['bands'])
print(r.interpretation)
r.to_json('report.json')
r.to_html('report.html')

comparison = compare_masters('premaster.wav', 'master.wav')
print(comparison.spectral_changes)

multi = audit_pipeline({'source': 'source.wav', 'premaster': 'premaster.wav', 'master': 'master.wav'})
print(multi['stage_comparisons'])
```

CLI:

```bash
spectralaudit analyze master.wav --json report.json --html report.html
spectralaudit compare premaster.wav master.wav --json comparison.json
```

Results are structured, inspectable numerical diagnostics, **not an AI verdict**.
