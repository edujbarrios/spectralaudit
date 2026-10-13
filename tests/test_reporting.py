"""Report format guarantees and JSON/Markdown/text round-trip checks."""
import json

import numpy as np
import pytest

from spectralaudit import analyze
from spectralaudit.models import AuditReport, format_payload


def test_json_markdown_text(audio_factory, tmp_path):
    report = analyze(audio_factory(), modules=["synthetic_patterns"])
    original = report.as_dict()
    j = report.to_json(tmp_path / "report.json")
    m = report.to_markdown(tmp_path / "report.md")
    t = report.to_text(tmp_path / "report.txt")
    assert json.loads(j.read_text()) == original
    assert "# SpectralAudit report" in m.read_text()
    assert "**candidate_pattern**" in m.read_text()
    assert "SYNTHETIC_PATTERNS" in t.read_text()
    assert report.as_dict() == original
    assert not hasattr(report, "to_html")


def test_numpy_and_escaped_markdown():
    report = AuditReport({"count": np.int64(2), "name": "test \x60audio\x60"},
                         {"pattern": {"values": np.array([440, 880]), "missing": None}})
    assert "440" in report.as_text()
    assert "test \\\x60audio\\\x60" in report.as_markdown()
    assert "null" in report.as_markdown()


def test_unknown_output_type_is_rejected():
    with pytest.raises(ValueError):
        format_payload({}, format="html")
