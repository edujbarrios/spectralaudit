import json

from spectralaudit.cli import main


def test_cli_report(audio_factory, tmp_path):
    path = audio_factory()
    outfile = tmp_path / "r.json"
    assert main(["spectrum", str(path), "--json", str(outfile)]) == 0
    assert "high_frequency" in json.loads(outfile.read_text())["findings"]
    assert main(["analyze", str(path), "--html", str(tmp_path / "r.html")]) == 0
    assert (tmp_path / "r.html").exists()


def test_cli_error(capsys):
    assert main(["analyze", "/does/not/exist.wav"]) == 2
    assert "spectralaudit" in capsys.readouterr().err
