import json

from brujula.cli import main


def test_report_cli_rejects_blocked_pointer(tmp_path, capsys):
    (tmp_path / "current.json").write_text(json.dumps({"status": "BLOCKED", "publishable": False}))
    assert main(["report", "--output", str(tmp_path)]) == 1
    assert "BLOCKED" in capsys.readouterr().err


def test_report_cli_checks_missing_manifest(tmp_path, capsys):
    (tmp_path / "current.json").write_text(json.dumps({"status": "REVIEW", "build_status": "SUCCEEDED", "publishable": True, "run_id": "20260922T000000-abcdef123456"}))
    assert main(["report", "--output", str(tmp_path)]) == 1
    assert "ERROR" in capsys.readouterr().err
