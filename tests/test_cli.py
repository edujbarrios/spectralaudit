import json

from spectralaudit.cli import main


def test_cli_report(audio_factory, tmp_path):
    path = audio_factory()
    outfile = tmp_path / "r.json"
    assert main(["spectrum", str(path), "--json", str(outfile)]) == 0
    assert "high_frequency" in json.loads(outfile.read_text())["findings"]
    assert main(["analyze", str(path), "--markdown", str(tmp_path / "r.md")]) == 0
    assert "## Findings" in (tmp_path / "r.md").read_text()
    assert main(["fingerprint", str(path), "--text", str(tmp_path / "r.txt")]) == 0
    assert "SYNTHETIC_PATTERNS" in (tmp_path / "r.txt").read_text()


def test_cli_error(capsys):
    assert main(["analyze", "/does/not/exist.wav"]) == 2
    assert "spectralaudit" in capsys.readouterr().err

def test_batch_missing_directory_fails(capsys, tmp_path):
    assert main(["batch", str(tmp_path / "missing")]) == 2
    assert "not a directory" in capsys.readouterr().err


def test_batch_empty_directory_is_valid(tmp_path, capsys):
    assert main(["batch", str(tmp_path)]) == 0
    assert "RESULTS" in capsys.readouterr().out
    output = tmp_path / "results.json"
    assert main(["batch", str(tmp_path), "--json", str(output)]) == 0
    assert json.loads(output.read_text()) == {"results": []}


def test_cli_does_not_accept_html(audio_factory):
    import pytest
    from spectralaudit.cli import make_parser
    with pytest.raises(SystemExit):
        make_parser().parse_args(["analyze", str(audio_factory()), "--html", "out.html"])
    with pytest.raises(SystemExit):
        make_parser().parse_args(["analyze", str(audio_factory()), "--json", "a.json", "--markdown", "b.md"])
