"""Generate real JSON/Markdown/text reports from the checked-in example WAV.

Run from the project root: python examples/synthetic_demo.py
"""
from pathlib import Path
from spectralaudit import analyze

SOURCE = Path("examples/assets/synthetic_spectral_comb.wav")
RESULTS = Path("examples/results")


def main() -> None:
    RESULTS.mkdir(exist_ok=True, parents=True)
    report = analyze(SOURCE, modules=["synthetic_patterns"])
    report.to_json(RESULTS / "synthetic_spectral_comb.json")
    report.to_markdown(RESULTS / "synthetic_spectral_comb.md")
    report.to_text(RESULTS / "synthetic_spectral_comb.txt")
    print(report.as_text())


if __name__ == "__main__":
    main()
