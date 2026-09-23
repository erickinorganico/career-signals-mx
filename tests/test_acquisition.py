import hashlib
import io
import json
import zipfile
from urllib.request import Request

import pytest

from brujula import acquisition


def _registry(tmp_path, url="https://www.inegi.org.mx/file.zip", expected=None, **limits):
    path = tmp_path / "registry.json"
    path.write_text(json.dumps({"allowed_host": "www.inegi.org.mx", "max_download_bytes": 1000,
                                "max_uncompressed_bytes": 1000, "snapshots": [{"id": "s1", "url": url,
                                "expected_sha256": expected, "acquisition_approved": True}], **limits}), encoding="utf-8")
    return path


def _zip(name="ok.csv", body=b"id,value\n1,2\n"):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr(name, body)
    return buffer.getvalue()


def test_downloads_verified_zip_to_content_addressed_raw_and_receipt(monkeypatch, tmp_path):
    payload = _zip()
    monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    digest = hashlib.sha256(payload).hexdigest()
    assert receipt["status"] == "SUCCEEDED"
    assert (tmp_path / "raw" / f"{digest}.zip").read_bytes() == payload
    assert (tmp_path / "acquisitions/s1/current.json").exists()
    assert len(list((tmp_path / "acquisitions/s1/attempts").glob("*.json"))) == 1


def test_failure_after_previous_success_replaces_current_without_fallback(monkeypatch, tmp_path):
    payload = _zip()
    monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
    assert acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))["status"] == "SUCCEEDED"
    monkeypatch.setattr(acquisition, "_download", lambda *args: (_ for _ in ()).throw(RuntimeError("network")))
    failed = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    assert failed["status"] == "FAILED"
    assert json.loads((tmp_path / "acquisitions/s1/current.json").read_text())["status"] == "FAILED"


def test_offline_replay_verifies_cache_and_resolve(monkeypatch, tmp_path):
    payload = _zip()
    monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
    acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    path, receipt = acquisition.resolve_snapshot("s1", tmp_path, _registry(tmp_path))
    assert path.exists() and receipt["mode"] == "download"
    assert len(list((tmp_path / "acquisitions/s1/attempts").glob("*.json"))) == 1


@pytest.mark.parametrize("member", ["../escape.csv", "/absolute.csv", "C:/drive.csv"])
def test_rejects_unsafe_zip_members(monkeypatch, tmp_path, member):
    payload = _zip(member)
    monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    assert receipt["status"] == "FAILED"
    assert "unsafe member" in receipt["error"]["message"]


def test_rejects_duplicate_members_and_expansion(monkeypatch, tmp_path):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("x.csv", b"1")
        archive.writestr("x.csv", b"2")
    monkeypatch.setattr(acquisition, "_download", lambda *args: buffer.getvalue())
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    assert receipt["status"] == "FAILED" and "duplicate" in receipt["error"]["message"]
    monkeypatch.setattr(acquisition, "_download", lambda *args: _zip(body=b"x" * 2001))
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    assert receipt["status"] == "FAILED" and "expanded size" in receipt["error"]["message"]


def test_rejects_hash_corruption_unknown_id_and_bad_host(monkeypatch, tmp_path):
    payload = _zip()
    monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
    expected = "0" * 64
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path, expected=expected))
    assert receipt["status"] == "FAILED" and "SHA-256" in receipt["error"]["message"]
    missing = acquisition.acquire_snapshot("missing", tmp_path, registry_path=_registry(tmp_path))
    assert missing["status"] == "FAILED"
    assert json.loads((tmp_path / "acquisitions/missing/current.json").read_text())["status"] == "FAILED"
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path, url="https://evil.example/file.zip"))
    assert receipt["status"] == "FAILED" and "allowed host" in receipt["error"]["message"]


def test_redirect_and_html_are_rejected(monkeypatch, tmp_path):
    monkeypatch.setattr(acquisition, "_download", lambda *args: (_ for _ in ()).throw(acquisition.AcquisitionError("redirect host not allowed")))
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    assert receipt["status"] == "FAILED" and "redirect" in receipt["error"]["message"]
    monkeypatch.setattr(acquisition, "_download", lambda *args: (_ for _ in ()).throw(acquisition.AcquisitionError("download returned HTML")))
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    assert receipt["status"] == "FAILED" and "HTML" in receipt["error"]["message"]


def test_registry_requires_approved_unique_safe_ids_and_pinned_hash(tmp_path):
    path = _registry(tmp_path)
    config = json.loads(path.read_text())
    config["snapshots"][0]["acquisition_approved"] = False
    path.write_text(json.dumps(config))
    revoked = acquisition.acquire_snapshot("s1", tmp_path, registry_path=path)
    assert revoked["status"] == "FAILED"
    assert json.loads((tmp_path / "acquisitions/s1/current.json").read_text())["status"] == "FAILED"
    config["snapshots"][0]["acquisition_approved"] = True
    config["snapshots"].append(config["snapshots"][0].copy())
    path.write_text(json.dumps(config))
    duplicated = acquisition.acquire_snapshot("s1", tmp_path, registry_path=path)
    assert duplicated["status"] == "FAILED"


def test_pinned_offline_cache_never_falls_back_to_prior_hash(monkeypatch, tmp_path):
    payload = _zip()
    monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
    base = _registry(tmp_path)
    acquisition.acquire_snapshot("s1", tmp_path, registry_path=base)
    config = json.loads(base.read_text())
    config["snapshots"][0]["expected_sha256"] = "0" * 64
    pinned = tmp_path / "pinned.json"
    pinned.write_text(json.dumps(config))
    receipt = acquisition.acquire_snapshot("s1", tmp_path, offline=True, registry_path=pinned)
    assert receipt["status"] == "FAILED" and receipt["error"]["message"] == "offline cache miss"


def test_resolve_is_read_only_and_rejects_failed_or_corrupt_current(tmp_path):
    registry = _registry(tmp_path)
    current = tmp_path / "acquisitions/s1/current.json"
    current.parent.mkdir(parents=True)
    current.write_text(json.dumps({"status": "FAILED", "snapshot_id": "s1"}))
    with pytest.raises(acquisition.AcquisitionError, match="successful"):
        acquisition.resolve_snapshot("s1", tmp_path, registry)
    assert not list((tmp_path / "acquisitions/s1").glob("attempts/*.json"))


@pytest.mark.parametrize("url", ["http://www.inegi.org.mx/file.zip", "https://www.inegi.org.mx:443/file.zip", "https://user:pass@www.inegi.org.mx/file.zip"])
def test_rejects_noncanonical_catalog_url_before_transport(monkeypatch, tmp_path, url):
    called = []
    monkeypatch.setattr(acquisition, "_download", lambda *args: called.append(True) or _zip())
    receipt = acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path, url=url))
    assert receipt["status"] == "FAILED" and not called


def test_invalid_snapshot_id_never_creates_path(tmp_path):
    with pytest.raises(acquisition.AcquisitionError, match="snapshot_id is invalid"):
        acquisition.acquire_snapshot("../escape", tmp_path, registry_path=_registry(tmp_path))
    assert not (tmp_path / "acquisitions").exists()


def test_offline_cache_enforces_download_limit(monkeypatch, tmp_path):
    payload = _zip()
    monkeypatch.setattr(acquisition, "_download", lambda *args: payload)
    acquisition.acquire_snapshot("s1", tmp_path, registry_path=_registry(tmp_path))
    registry = _registry(tmp_path, max_download_bytes=len(payload) - 1)
    receipt = acquisition.acquire_snapshot("s1", tmp_path, offline=True, registry_path=registry)
    assert receipt["status"] == "FAILED" and receipt["error"]["message"] == "offline cache miss"


def test_download_sends_wildcard_accept_and_redirect_policy(monkeypatch):
    seen = {}

    class Response:
        headers = {"Content-Type": "application/x-zip-compressed"}

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return None

        def geturl(self):
            return "https://www.inegi.org.mx/file.zip"

        def read(self, size=-1):
            value = _zip()
            if not seen.get("read"):
                seen["read"] = True
                return value
            return b""

    class Opener:
        def open(self, request, timeout):
            seen["request"] = request
            return Response()

    monkeypatch.setattr(acquisition, "build_opener", lambda handler: Opener())
    assert acquisition._download("https://www.inegi.org.mx/file.zip", "www.inegi.org.mx", 1000, 1)
    assert seen["request"].get_header("Accept") == "*/*"
    redirects = acquisition._CheckedRedirects("www.inegi.org.mx")
    for target in ("http://www.inegi.org.mx/file.zip", "https://evil.example/file.zip", "https://user:pass@www.inegi.org.mx/file.zip", "https://www.inegi.org.mx:444/file.zip"):
        with pytest.raises(acquisition.AcquisitionError):
            redirects.redirect_request(Request("https://www.inegi.org.mx/file.zip"), None, 302, "", {}, target)


def test_resolve_rejects_non_hex_digest_and_mismatched_attempt(tmp_path):
    registry = _registry(tmp_path)
    current = tmp_path / "acquisitions/s1/current.json"
    attempts = current.parent / "attempts"
    attempts.mkdir(parents=True)
    receipt = {"status": "SUCCEEDED", "snapshot_id": "s1", "url": "https://www.inegi.org.mx/file.zip", "sha256": "z" * 64, "run_id": "run"}
    current.write_text(json.dumps(receipt))
    (attempts / "run.json").write_text(json.dumps(receipt))
    with pytest.raises(acquisition.AcquisitionError, match="hash"):
        acquisition.resolve_snapshot("s1", tmp_path, registry)
