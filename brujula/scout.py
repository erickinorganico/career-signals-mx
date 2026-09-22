"""Opt-in official-page monitor. Discovery is a proposal, never source activation."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib import robotparser
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, Request, build_opener
from uuid import uuid4

from .pipeline import atomic_json, immutable_bytes, json_bytes, now, read_catalog

USER_AGENT = "BrujulaLaboralMX/0.1 (local public-source metadata monitor)"
MAX_BYTES = 3_000_000


class OfficialRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        parsed = urlsplit(newurl)
        if parsed.scheme != "https" or parsed.hostname != "www.inegi.org.mx" or parsed.port not in {None, 443}:
            raise ValueError("Redirect leaves the approved INEGI origin")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def fetch_public_page(url: str) -> tuple[bytes, dict]:
    parsed = urlsplit(url)
    if parsed.scheme != "https" or parsed.hostname != "www.inegi.org.mx" or parsed.username or parsed.port not in {None, 443}:
        raise ValueError("Only the approved HTTPS INEGI origin is permitted")
    opener = build_opener(OfficialRedirects())
    robots_url = "https://www.inegi.org.mx/robots.txt"
    with opener.open(Request(robots_url, headers={"User-Agent": USER_AGENT}), timeout=20) as response:
        content = response.read(MAX_BYTES + 1)
        if len(content) > MAX_BYTES:
            raise ValueError("Robots response exceeds limit")
        robots = robotparser.RobotFileParser()
        robots.parse(content.decode("utf-8", errors="replace").splitlines())
    if not robots.can_fetch(USER_AGENT, url):
        raise ValueError("Source robots policy does not permit this fetch")
    with opener.open(Request(url, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/json"}), timeout=20) as response:
        body = response.read(MAX_BYTES + 1)
        if len(body) > MAX_BYTES:
            raise ValueError("Source response exceeds 3 MB limit")
        content_type = response.headers.get_content_type()
        if content_type not in {"text/html", "application/json", "text/plain"}:
            raise ValueError("Unsupported source content type")
        return body, {"http_status": response.status, "content_type": content_type, "url": response.url,
                      "etag": response.headers.get("ETag"), "last_modified": response.headers.get("Last-Modified")}


def scout_source(source_id: str, output: Path, fetcher=fetch_public_page) -> dict:
    catalog = read_catalog()
    source = next((item for item in catalog if item["id"] == source_id), None)
    run_id = uuid4().hex
    receipt = {"schema_version": "1.0", "run_id": run_id, "source_id": source_id, "started_at": now(),
               "completed_at": None, "status": "BLOCKED", "activation_allowed": False,
               "numeric_publication_allowed": False, "mode": "read_only_metadata", "sha256": None, "error": None}
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    # IDs never become file paths: the identifier itself is hashed.
    current = output / "current" / (hashlib.sha256(source_id.encode()).hexdigest() + ".json")
    previous = json.loads(current.read_text(encoding="utf-8")) if current.exists() else None
    try:
        if not source or not source.get("monitor_allowed"):
            raise ValueError("Source is not approved for metadata monitoring")
        raw, response = fetcher(source["url"])
        digest = hashlib.sha256(raw).hexdigest()
        immutable_bytes(output / "raw" / f"{digest}.bin", raw)
        changed = previous is None or previous.get("sha256") != digest or previous.get("status") == "BLOCKED"
        receipt.update(status="REVIEW" if changed else "MEASURED", sha256=digest, response=response,
                       changed=changed, previous_sha256=previous.get("sha256") if previous else None,
                       recommendation="Revisar contenido, publicación y metodología antes de integrar." if changed else "Contenido sin cambio desde la última captura verificada.",
                       limitation="Un hash distinto puede ser navegación o formato; no prueba un cambio estadístico.")
    except Exception as exc:
        receipt["error"] = {"type": type(exc).__name__, "message": str(exc)}
    receipt["completed_at"] = now()
    immutable_bytes(output / "runs" / f"{run_id}.json", json_bytes(receipt))
    atomic_json(current, receipt)
    return receipt
