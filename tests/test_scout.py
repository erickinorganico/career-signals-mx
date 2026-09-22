"""Network-free source-monitor controls; actual HTTP is opt-in."""
import json
from pathlib import Path

from brujula.scout import OfficialRedirects, fetch_public_page, scout_source
from urllib.request import Request

import pytest


def fake_page(body):
    return lambda url: (body, {"url": url, "http_status": 200, "content_type": "text/html", "etag": None, "last_modified": None})


def test_source_discovery_is_review_then_unchanged_and_never_activates(tmp_path):
    first = scout_source("inegi_enoe_2025_q2", tmp_path, fake_page(b"version one"))
    second = scout_source("inegi_enoe_2025_q2", tmp_path, fake_page(b"version one"))
    third = scout_source("inegi_enoe_2025_q2", tmp_path, fake_page(b"methodology changed"))
    assert [r["status"] for r in (first, second, third)] == ["REVIEW", "MEASURED", "REVIEW"]
    assert all(not r["activation_allowed"] and not r["numeric_publication_allowed"] for r in (first, second, third))
    assert third["previous_sha256"] == first["sha256"]
    assert len(list((tmp_path / "raw").glob("*.bin"))) == 2
    assert len(list((tmp_path / "runs").glob("*.json"))) == 3


def test_failure_overwrites_current_not_fresh_success(tmp_path):
    success = scout_source("inegi_enoe_2025_q2", tmp_path, fake_page(b"body"))
    def offline(url):
        raise OSError("network unavailable")
    failed = scout_source("inegi_enoe_2025_q2", tmp_path, offline)
    assert failed["status"] == "BLOCKED" and failed["sha256"] is None
    current = json.loads(next((tmp_path / "current").glob("*.json")).read_text(encoding="utf-8"))
    assert current["run_id"] == failed["run_id"] != success["run_id"]


@pytest.mark.parametrize("source", ["ola_stps", "imco_compara_carreras_2026", "https://evil.example", "../escape"])
def test_unapproved_source_never_fetches(source, tmp_path):
    def fail_if_called(url):
        pytest.fail("Unapproved network request")
    result = scout_source(source, tmp_path, fail_if_called)
    assert result["status"] == "BLOCKED"


@pytest.mark.parametrize("url", ["http://www.inegi.org.mx/", "https://evil.example/", "https://www.inegi.org.mx:8443/", "https://user@www.inegi.org.mx/"])
def test_fetch_rejects_unapproved_origins_before_network(url):
    with pytest.raises(ValueError):
        fetch_public_page(url)


def test_redirect_does_not_escape_official_origin():
    with pytest.raises(ValueError):
        OfficialRedirects().redirect_request(Request("https://www.inegi.org.mx/"), None, 302, "Found", {}, "https://evil.example/")
