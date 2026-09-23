"""Installed v2 CLI paths keep real research distinct from synthetic demo."""

from brujula import cli


def test_research_open_uses_verified_current(monkeypatch, capsys, tmp_path):
    called = []

    def verified(output_root, source_root):
        called.append((output_root, source_root))
        return {"html": tmp_path / "sealed" / "report.html"}

    monkeypatch.setattr("brujula.pipeline_v2.resolve_publication_current", verified)
    assert cli.main(["research-open", "--source-root", str(tmp_path / "sources"),
                     "--output-root", str(tmp_path / "publication"),
                     "--format", "html"]) == 0
    assert called == [(tmp_path / "publication", tmp_path / "sources")]
    assert "report.html" in capsys.readouterr().out


def test_real_cli_help_declares_separate_paths(capsys):
    try:
        cli.main(["research-analyze", "--help"])
    except SystemExit as exc:
        assert exc.code == 0
    output = capsys.readouterr().out
    for flag in ("--source-root", "--acceptance-receipt", "--analysis-output", "--audit-dir"):
        assert flag in output
