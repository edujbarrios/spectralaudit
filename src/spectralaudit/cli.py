"""Command-line interface with explicit file outputs."""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

from . import __version__, analyze
from .models import _json_default


def make_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="spectralaudit", description="Offline audio spectral forensics (NOT an AI-origin classifier)")
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("analyze", "spectrum", "fingerprint"):
        p = sub.add_parser(command)
        p.add_argument("file")
        p.add_argument("--json", dest="json_output")
        p.add_argument("--html")
    p = sub.add_parser("batch")
    p.add_argument("directory")
    p.add_argument("--json", dest="json_output")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = make_parser().parse_args(argv)
    try:
        if args.command == "batch":
            root = Path(args.directory)
            if not root.is_dir():
                raise ValueError(f"Batch input is not a directory: {root}")
            paths = sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in {".wav", ".flac"})
            data = []
            for path in paths:
                try:
                    data.append({"path": str(path), "report": analyze(path).as_dict()})
                except (OSError, ValueError, RuntimeError) as ex:
                    data.append({"path": str(path), "error": str(ex)})
            output = json.dumps({"results": data}, indent=2, default=_json_default, allow_nan=False)
            if args.json_output:
                Path(args.json_output).write_text(output, encoding="utf-8")
            else:
                print(output)
            return 1 if any("error" in item for item in data) else 0
        else:
            modules = (["high_frequency"] if args.command == "spectrum" else
                       ["synthetic_patterns"] if args.command == "fingerprint" else
                       ["high_frequency", "spectral_comb", "synthetic_patterns",
                        "temporal", "confounders"])
            report = analyze(args.file, modules=modules)
        if args.json_output:
            report.to_json(args.json_output)
        if getattr(args, "html", None):
            report.to_html(args.html)
        if not args.json_output:
            print(json.dumps(report.as_dict() if hasattr(report, "as_dict") else vars(report),
                             indent=2, default=_json_default, allow_nan=False))
        return 0
    except (OSError, ValueError, RuntimeError) as exc:
        print(f"spectralaudit: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
