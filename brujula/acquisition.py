"""Safe, receipt-producing acquisition of catalogued snapshot ZIPs.

This module deliberately stops at an immutable raw ZIP.  Extraction and any
statistical interpretation belong to later, separately reviewed stages.
"""

from __future__ import annotations

import hashlib
import json
import os
import re
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener

from .resources import _resource
from .runlock import BuildLock


_SCHEMA_VERSION = "1.0"
_USER_AGENT = "brujula-laboral-mx/acquisition-1.0"


class AcquisitionError(RuntimeError):
    """A snapshot could not be acquired or validated."""


class _CheckedRedirects(HTTPRedirectHandler):
    def __init__(self, allowed_host: str):
        super().__init__()
        self.allowed_host = allowed_host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        host = (parsed.hostname or "").lower()
        if parsed.scheme != "https" or host != self.allowed_host or parsed.username or parsed.password or parsed.port:
            raise AcquisitionError("redirect URL is not HTTPS on the allowed host")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _read_registry(path: Path) -> dict:
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionError("cannot read registry") from exc
    _validate_registry(result)
    return result


def _validate_registry(registry: dict) -> None:
    if not isinstance(registry, dict):
        raise AcquisitionError("registry root is invalid")
    allowed = str(registry.get("allowed_host", "")).lower()
    max_download = registry.get("max_download_bytes")
    max_uncompressed = registry.get("max_uncompressed_bytes")
    if (not re.fullmatch(r"[a-z0-9.-]+", allowed)
            or type(max_download) is not int or max_download <= 0
            or type(max_uncompressed) is not int or max_uncompressed <= 0):
        raise AcquisitionError("registry limits or allowed_host are invalid")
    snapshots = registry.get("snapshots")
    if not isinstance(snapshots, list):
        raise AcquisitionError("registry snapshots are invalid")
    seen: set[str] = set()
    for item in snapshots:
        sid = item.get("id") if isinstance(item, dict) else None
        if not isinstance(sid, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", sid) or sid in seen:
            raise AcquisitionError("registry snapshot IDs are invalid or duplicated")
        seen.add(sid)
        if item.get("acquisition_approved") is not True:
            raise AcquisitionError(f"snapshot {sid} is not approved for acquisition")
        expected = item.get("expected_sha256")
        if expected is not None and (not isinstance(expected, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", expected)):
            raise AcquisitionError(f"snapshot {sid} expected_sha256 is invalid")


def _snapshot(registry: dict, snapshot_id: str) -> dict:
    for item in registry.get("snapshots", []):
        if item.get("id") == snapshot_id:
            return item
    raise AcquisitionError(f"unknown snapshot_id: {snapshot_id}")


def _default_registry() -> Path:
    return _resource("catalog", "data/catalog", "enoe-snapshots.json")


def _atomic_create(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    fd = os.open(path, flags, 0o600)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(payload)
    except Exception:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        raise


def _write_json_once(path: Path, payload: dict) -> None:
    _atomic_create(path, json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8"))


def _write_current(path: Path, payload: dict) -> None:
    """Replace the mutable pointer atomically; attempt receipts stay immutable."""
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.{uuid.uuid4().hex}.tmp")
    temporary.write_text(json.dumps(payload, ensure_ascii=False, sort_keys=True, indent=2), encoding="utf-8")
    os.replace(temporary, path)


def _zip_safety(data: bytes, max_uncompressed: int) -> None:
    if type(max_uncompressed) is not int or max_uncompressed <= 0:
        raise AcquisitionError("registry limits or allowed_host are invalid")
    try:
        with zipfile.ZipFile(__import__("io").BytesIO(data)) as archive:
            names: set[str] = set()
            expanded = 0
            for info in archive.infolist():
                name = info.filename
                normalized = name.replace("\\", "/")
                if name in names:
                    raise AcquisitionError(f"ZIP duplicate member: {name}")
                names.add(name)
                if normalized.startswith("/") or ":/" in normalized or any(part == ".." for part in normalized.split("/")):
                    raise AcquisitionError(f"ZIP unsafe member path: {name}")
                if info.external_attr >> 16 & 0o170000 == 0o120000:
                    raise AcquisitionError(f"ZIP symlink member: {name}")
                expanded += max(0, info.file_size)
                if expanded > max_uncompressed:
                    raise AcquisitionError("ZIP expanded size exceeds configured limit")
    except zipfile.BadZipFile as exc:
        raise AcquisitionError("download is not a valid ZIP") from exc


def _download(url: str, allowed_host: str, max_bytes: int, timeout: float) -> bytes:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or (parsed.hostname or "").lower() != allowed_host or parsed.username or parsed.password or parsed.port:
        raise AcquisitionError("catalog URL must be HTTPS and use the allowed host")
    # INEGI serves application/x-zip-compressed and rejects application/zip
    # with HTTP 406. Validate the actual ZIP bytes instead of MIME spelling.
    request = Request(url, headers={"User-Agent": _USER_AGENT, "Accept": "*/*"})
    opener = build_opener(_CheckedRedirects(allowed_host))
    try:
        with opener.open(request, timeout=timeout) as response:
            final_host = (urlsplit(response.geturl()).hostname or "").lower()
            final_url = urlsplit(response.geturl())
            if final_url.scheme != "https" or final_host != allowed_host or final_url.username or final_url.password or final_url.port:
                raise AcquisitionError("response URL is not HTTPS on the allowed host")
            content_type = (response.headers.get("Content-Type") or "").lower()
            length = response.headers.get("Content-Length")
            if length and int(length) > max_bytes:
                raise AcquisitionError("download exceeds configured size limit")
            chunks: list[bytes] = []
            total = 0
            while True:
                chunk = response.read(min(1024 * 1024, max_bytes + 1 - total))
                if not chunk:
                    break
                total += len(chunk)
                if total > max_bytes:
                    raise AcquisitionError("download exceeds configured size limit")
                chunks.append(chunk)
            data = b"".join(chunks)
            if "text/html" in content_type or data.lstrip().lower().startswith((b"<!doctype html", b"<html")):
                raise AcquisitionError("download returned HTML instead of ZIP")
            return data
    except (HTTPError, URLError, TimeoutError, ValueError) as exc:
        raise AcquisitionError(f"download failed: {exc}") from exc


def _receipt(snapshot_id: str, run_id: str, started: str, status: str, **extra: object) -> dict:
    result = {
        "schema_version": _SCHEMA_VERSION,
        "run_id": run_id,
        "snapshot_id": snapshot_id,
        "status": status,
        "started_at": started,
        "completed_at": _now(),
    }
    result.update(extra)
    return result


def _clean_error(exc: Exception, output_root: Path) -> dict:
    message = str(exc).replace(str(output_root), "<output>")
    return {"type": type(exc).__name__, "message": message}


def acquire_snapshot(snapshot_id: str, output_root: Path, *, offline: bool = False, registry_path: Path | None = None) -> dict:
    """Acquire one exact catalog URL and return its immutable attempt receipt."""
    if not isinstance(snapshot_id, str) or not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9._-]*", snapshot_id):
        raise AcquisitionError("snapshot_id is invalid")
    output_root = Path(output_root)
    started = _now()
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ") + "-" + uuid.uuid4().hex[:12]
    attempt_dir = output_root / "acquisitions" / snapshot_id / "attempts"
    lock_root = output_root / "acquisitions" / snapshot_id
    current_path = lock_root / "current.json"
    lock_root.mkdir(parents=True, exist_ok=True)

    def failed(exc: Exception, item: dict | None = None) -> dict:
        return _receipt(snapshot_id, run_id, started, "FAILED", mode="offline" if offline else "download",
                        url=item.get("url") if item else None, sha256=None,
                        error=_clean_error(exc, output_root))

    try:
        with BuildLock(lock_root):
            prior = None
            if current_path.exists():
                try:
                    prior = json.loads(current_path.read_text(encoding="utf-8"))
                except (OSError, json.JSONDecodeError):
                    prior = None
            _write_current(current_path, {"schema_version": _SCHEMA_VERSION, "snapshot_id": snapshot_id, "status": "RUNNING", "run_id": run_id, "started_at": started})
            item = None
            try:
                registry = _read_registry(Path(registry_path) if registry_path else _default_registry())
                item = _snapshot(registry, snapshot_id)
                allowed_host = str(registry["allowed_host"]).lower()
                max_bytes = registry["max_download_bytes"]
                max_uncompressed = registry["max_uncompressed_bytes"]
                expected = item.get("expected_sha256")
                parsed_url = urlsplit(str(item.get("url", "")))
                if parsed_url.scheme != "https" or (parsed_url.hostname or "").lower() != allowed_host or parsed_url.username or parsed_url.password or parsed_url.port:
                    raise AcquisitionError("catalog URL must be HTTPS and use the allowed host")
                if offline:
                    candidates = []
                    if prior and prior.get("status") == "SUCCEEDED" and prior.get("sha256"):
                        candidates.append(str(prior["sha256"]))
                    if expected:
                        candidates = [str(expected)]
                    data = None
                    digest = None
                    for candidate in candidates:
                        if not re.fullmatch(r"[0-9a-fA-F]{64}", candidate):
                            continue
                        raw = output_root / "raw" / f"{candidate}.zip"
                        if raw.exists():
                            candidate_data = raw.read_bytes()
                            if len(candidate_data) <= max_bytes and hashlib.sha256(candidate_data).hexdigest() == candidate.lower():
                                data, digest = candidate_data, candidate.lower()
                                break
                    if data is None:
                        raise AcquisitionError("offline cache miss")
                    _zip_safety(data, max_uncompressed)
                    receipt = _receipt(snapshot_id, run_id, started, "SUCCEEDED", mode="cache_offline", url=item["url"], sha256=digest, bytes=len(data))
                else:
                    data = _download(str(item["url"]), allowed_host, max_bytes, 60.0)
                    _zip_safety(data, max_uncompressed)
                    digest = hashlib.sha256(data).hexdigest()
                    if expected and digest.lower() != str(expected).lower():
                        raise AcquisitionError("SHA-256 does not match catalog expected_sha256")
                    raw = output_root / "raw" / f"{digest}.zip"
                    if raw.exists():
                        if hashlib.sha256(raw.read_bytes()).hexdigest() != digest:
                            raise AcquisitionError("existing raw cache failed SHA-256 verification")
                    else:
                        _atomic_create(raw, data)
                    receipt = _receipt(snapshot_id, run_id, started, "SUCCEEDED", mode="download", url=item["url"], sha256=digest, bytes=len(data))
                _write_json_once(attempt_dir / f"{run_id}.json", receipt)
                _write_current(current_path, receipt)
                return receipt
            except Exception as exc:
                receipt = failed(exc, item)
                _write_json_once(attempt_dir / f"{run_id}.json", receipt)
                _write_current(current_path, receipt)
                return receipt
    except RuntimeError as exc:
        # Another owner holds the lock. An immutable attempt receipt is safe;
        # current.json belongs exclusively to the owner and must not be touched.
        receipt = failed(exc)
        try:
            _write_json_once(attempt_dir / f"{run_id}.json", receipt)
        except FileExistsError:
            pass
        return receipt


def resolve_snapshot(snapshot_id: str, output_root: Path, registry_path: Path | None = None) -> tuple[Path, dict]:
    """Resolve a verified cached raw ZIP; never performs a network request."""
    output_root = Path(output_root)
    registry = _read_registry(Path(registry_path) if registry_path else _default_registry())
    item = _snapshot(registry, snapshot_id)
    current_path = output_root / "acquisitions" / snapshot_id / "current.json"
    try:
        receipt = json.loads(current_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionError("snapshot has no readable current receipt") from exc
    if receipt.get("status") != "SUCCEEDED" or receipt.get("snapshot_id") != snapshot_id:
        raise AcquisitionError("snapshot current receipt is not a successful acquisition")
    if receipt.get("url") != item.get("url"):
        raise AcquisitionError("snapshot current receipt does not match registry URL")
    digest = receipt.get("sha256")
    expected = item.get("expected_sha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[0-9a-fA-F]{64}", digest) or (expected and digest.lower() != str(expected).lower()):
        raise AcquisitionError("snapshot current receipt hash does not match registry")
    attempt_path = current_path.parent / "attempts" / f"{receipt.get('run_id')}.json"
    try:
        attempt = json.loads(attempt_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionError("snapshot successful attempt receipt is missing") from exc
    if attempt != receipt:
        raise AcquisitionError("snapshot current receipt does not match immutable attempt receipt")
    path = output_root / "raw" / f"{digest}.zip"
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise AcquisitionError("snapshot raw cache is missing") from exc
    if hashlib.sha256(data).hexdigest() != digest:
        raise AcquisitionError("snapshot raw cache failed SHA-256 verification")
    _zip_safety(data, int(registry["max_uncompressed_bytes"]))
    return path, receipt
