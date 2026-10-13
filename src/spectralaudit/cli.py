"""Command-line interface for local JSON, Markdown and plain-text reports."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__, analyze
from .models import _json_default, format_payload


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="spectralaudit",
        description="Offline spectral diagnostics; not a validated AI-origin classifier")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("analyze", "spectrum", "fingerprint", "batch"):
        p = sub.add_parser(command)
        p.add_argument("directory" if command == "batch" else "file")
        output = p.add_mutually_exclusive_group()
        output.add_argument("--json", dest="json_output", metavar="PATH")
        output.add_argument("--markdown", "--md", dest="markdown_output", metavar="PATH")
        output.add_argument("--text", "--txt", dest="text_output", metavar="PATH")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        if args.command == "batch":
            root = Path(args.directory)
            if not root.is_dir():
                raise ValueError(f"Batch input is not a directory: {root}")
            paths = sorted(p for p in root.rglob("*") if p.is_file() and
                           p.suffix.lower() in {".wav", ".flac"})
            data = []
            for path in paths:
                try:
                    data.append({"path": str(path), "report": analyze(path).as_dict()})
                except (OSError, ValueError, RuntimeError) as exc:
                    data.append({"path": str(path), "error": str(exc)})
            payload = {"results": data}
            status = 1 if any("error" in item for item in data) else 0
            report = None
        else:
            modules = (["high_frequency"] if args.command == "spectrum" else
                       ["synthetic_patterns"] if args.command == "fingerprint" else
                       ["high_frequency", "spectral_comb", "synthetic_patterns",
                        "temporal", "confounders"])
            report = analyze(args.file, modules=modules)
            payload = report.as_dict()
            status = 0
        if args.json_output:
            output = json.dumps(payload, indent=2, default=_json_default,
                                ensure_ascii=False, allow_nan=False) + "\n"
            Path(args.json_output).write_text(output, encoding="utf-8")
        elif args.markdown_output:
            output = (report.as_markdown() if report else
                      format_payload(payload, format="markdown",
                                     title="SpectralAudit batch report"))
            Path(args.markdown_output).write_text(output, encoding="utf-8")
        elif args.text_output:
            output = (report.as_text() if report else
                      format_payload(payload, format="text",
                                     title="SpectralAudit batch report"))
            Path(args.text_output).write_text(output, encoding="utf-8")
        else:
            print(report.as_text() if report else
                  format_payload(payload, format="text",
                                 title="SpectralAudit batch report"), end="")
        return status
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"spectralaudit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
