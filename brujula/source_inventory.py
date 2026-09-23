"""Read-only, metadata-only inventory of the eight pinned ENOE packages."""

from __future__ import annotations

import csv
import hashlib
import io
import json
import re
import zipfile
from collections import Counter
from pathlib import Path

from .acquisition import AcquisitionError, _default_registry, _read_registry, resolve_snapshot


PERIODS = ("2024-Q3", "2024-Q4", "2025-Q1", "2025-Q2", "2025-Q3", "2025-Q4", "2026-Q1", "2026-Q2")
FOCUS_CODES = {"31300": "Ciencias políticas", "32100": "Comunicación y periodismo", "33100": "Derecho"}
GEO_OLD = ("AGEB", "ENT", "LOC", "MUN")
GEO_NEW = ("CVE_AGEB", "CVE_ENT", "CVE_LOC", "CVE_MUN")
MAX_METADATA_BYTES = 1024 * 1024


def _registry(path: Path | None) -> tuple[dict, dict[str, dict]]:
    registry = _read_registry(Path(path) if path is not None else _default_registry())
    items = registry["snapshots"]
    if len(items) != len(PERIODS) or [x.get("period") for x in items] != list(PERIODS):
        raise AcquisitionError("inventory registry must contain the eight approved periods in order")
    expected_ids = ["enoe_" + period.lower().replace("-", "_") for period in PERIODS]
    if [x.get("id") for x in items] != expected_ids:
        raise AcquisitionError("inventory registry IDs are not the approved eight")
    for key in ("source_id", "authority", "terms_url", "license", "checked_at"):
        if not isinstance(registry.get(key), str) or not registry[key].strip():
            raise AcquisitionError(f"registry {key} is required")
    if registry.get("publication_approved") is not False:
        raise AcquisitionError("inventory requires unapproved microdata publication state")
    for item in items:
        for key in ("url", "catalog_id", "catalog_title", "metadata_url", "expected_sha256"):
            if not isinstance(item.get(key), str) or not item[key].strip():
                raise AcquisitionError(f"snapshot {item['id']} lacks {key}")
    return registry, {x["id"]: x for x in items}


def _paths(period: str) -> tuple[str, str, str, str]:
    year, quarter = period.split("-Q")
    stem = f"{year}_{quarter}t"
    base = f"conjunto_de_datos_sdem_enoe_{stem}"
    return (
        f"{base}/conjunto_de_datos/conjunto_de_datos_sdem_enoe_{stem}.csv",
        f"{base}/diccionario_de_datos/diccionario_datos_sdem_enoe_{stem}.csv",
        f"{base}/catalogos/cs_p14_c.csv",
        f"{base}/conjunto_de_datos/sdem_enoe_{stem}_bitacora_de_cambios.csv",
    )


def _member(archive: zipfile.ZipFile, name: str, *, metadata: bool) -> tuple[dict, bytes | None]:
    info = archive.getinfo(name)
    if info.is_dir() or info.file_size == 0:
        raise AcquisitionError(f"required ZIP member is empty: {name}")
    if metadata and info.file_size > MAX_METADATA_BYTES:
        raise AcquisitionError(f"metadata member exceeds bound: {name}")
    digest = hashlib.sha256()
    size = 0
    chunks: list[bytes] = []
    with archive.open(info) as stream:
        while chunk := stream.read(1024 * 1024):
            digest.update(chunk)
            size += len(chunk)
            if metadata:
                chunks.append(chunk)
    if size != info.file_size:
        raise AcquisitionError(f"ZIP member size mismatch: {name}")
    return {"path": name, "sha256": digest.hexdigest(), "bytes": size}, b"".join(chunks) if metadata else None


def _metadata_rows(data: bytes, name: str) -> list[dict[str, str]]:
    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise AcquisitionError(f"metadata is not UTF-8: {name}") from exc
    try:
        reader = csv.DictReader(io.StringIO(text, newline=""))
        if not reader.fieldnames or len(reader.fieldnames) != len(set(reader.fieldnames)):
            raise AcquisitionError(f"metadata header is empty or duplicated: {name}")
        rows = list(reader)
        if not rows or any(None in row for row in rows):
            raise AcquisitionError(f"metadata rows are empty or malformed: {name}")
        return rows
    except csv.Error as exc:
        raise AcquisitionError(f"invalid metadata CSV: {name}") from exc


def _header(archive: zipfile.ZipFile, name: str) -> list[str]:
    with archive.open(name) as stream:
        line = stream.readline(65537)
    if not line or len(line) > 65536 or b"\n" not in line:
        raise AcquisitionError("SDEM header is empty or too long")
    try:
        header = next(csv.reader([line.decode("utf-8-sig")]))
    except (UnicodeDecodeError, csv.Error) as exc:
        raise AcquisitionError("SDEM header is not valid UTF-8 CSV") from exc
    if not header or any(not x for x in header) or len(header) != len(set(header)):
        raise AcquisitionError("SDEM header is empty or duplicated")
    return header


def _coding(dictionary_rows: list[dict[str, str]], catalog_rows: list[dict[str, str]]) -> dict:
    fields = [row for row in dictionary_rows if row.get("NEMÓNICO", "").upper() == "CS_P14_C"]
    if len(fields) != 1 or fields[0].get("LONGITUD") != "6" or fields[0].get("CATÁLOGO", "").lower() != "cs_p14_c":
        raise AcquisitionError("dictionary does not define six-character CS_P14_C")
    labels: dict[str, str] = {}
    for row in catalog_rows:
        key = row.get("CVE")
        label = row.get("DESCRIP")
        if not isinstance(key, str) or not re.fullmatch(r"[0-9]{1,6}", key) or not isinstance(label, str) or not label.strip():
            raise AcquisitionError("invalid CMPE catalog key or label")
        normalized = key.zfill(6)
        if normalized in labels:
            raise AcquisitionError("duplicate normalized CMPE catalog key")
        labels[normalized] = label
    result = {}
    for raw, expected_label in FOCUS_CODES.items():
        normalized = raw.zfill(6)
        label = labels.get(normalized)
        if label != expected_label:
            raise AcquisitionError(f"CMPE focus code {raw} is absent or changed")
        result[raw] = {"code": normalized, "label": label}
    return {"field": "CS_P14_C", "length": 6, "normalization": "ASCII digits, zero-fill to six; absent and 999999 stay unknown", "focus_codes": result, "unknown_code": "999999", "catalog_key_count": len(labels)}


def _revisions(rows: list[dict[str, str]], name: str, member: dict | None) -> dict:
    if member is None:
        return {"status": "no_sdem_bitacora_member_found", "member": None, "count": None, "date": None, "fields": None}
    fields = Counter()
    dates = set()
    for row in rows:
        field = row.get("Nombre de campo")
        date = row.get("Fecha de modificación")
        if not field or not date or not re.fullmatch(r"\d{2}/\d{2}/\d{4}", date):
            raise AcquisitionError(f"malformed SDEM revision metadata: {name}")
        fields[field.lower()] += 1
        dates.add(date)
    if len(dates) != 1:
        raise AcquisitionError(f"conflicting SDEM revision dates: {name}")
    date = next(iter(dates))
    day, month, year = date.split("/")
    return {"status": "sdem_bitacora_present", "member": member, "count": len(rows), "date": f"{year}-{month}-{day}", "fields": dict(sorted(fields.items()))}


def _inventory(snapshot_id: str, output_root: Path, registry_path: Path | None, registry: dict, item: dict) -> dict:
    path, receipt = resolve_snapshot(snapshot_id, output_root, registry_path)
    if not isinstance(receipt.get("completed_at"), str) or not receipt["completed_at"]:
        raise AcquisitionError("acquisition completed_at is required")
    person, dictionary, catalog, bitacora = _paths(item["period"])
    try:
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            if len(names) != len(set(names)):
                raise AcquisitionError("ZIP contains duplicate member names")
            for required in (person, dictionary, catalog):
                if names.count(required) != 1:
                    raise AcquisitionError(f"exact ZIP member missing: {required}")
            if names.count(bitacora) > 1:
                raise AcquisitionError("ambiguous SDEM bitácora member")
            header = _header(archive, person)
            person_member, _ = _member(archive, person, metadata=False)
            dictionary_member, dictionary_data = _member(archive, dictionary, metadata=True)
            catalog_member, catalog_data = _member(archive, catalog, metadata=True)
            assert dictionary_data is not None and catalog_data is not None
            dictionary_rows = _metadata_rows(dictionary_data, dictionary)
            catalog_rows = _metadata_rows(catalog_data, catalog)
            coding = _coding(dictionary_rows, catalog_rows)
            if bitacora in names:
                revision_member, revision_data = _member(archive, bitacora, metadata=True)
                assert revision_data is not None
                revisions = _revisions(_metadata_rows(revision_data, bitacora), bitacora, revision_member)
            else:
                revisions = _revisions([], bitacora, None)
    except (zipfile.BadZipFile, KeyError, OSError) as exc:
        raise AcquisitionError("cannot inspect exact ZIP members") from exc
    normalized_header = [x.upper() for x in header]
    if len(normalized_header) != len(set(normalized_header)):
        raise AcquisitionError("SDEM header has duplicate case-insensitive names")
    old_present = [x in normalized_header for x in GEO_OLD]
    new_present = [x in normalized_header for x in GEO_NEW]
    expected_new = item["period"] >= "2025-Q3"
    if (any(old_present) and any(new_present)) or (not all(new_present) if expected_new else not all(old_present)):
        raise AcquisitionError("SDEM geography aliases conflict or are absent")
    if (any(old_present) if expected_new else any(new_present)):
        raise AcquisitionError("unexpected geography alias in SDEM header")
    if "CS_P14_C" not in normalized_header:
        raise AcquisitionError("SDEM header lacks CS_P14_C")
    current = Path(output_root) / "acquisitions" / snapshot_id / "current.json"
    try:
        if json.loads(current.read_text(encoding="utf-8")) != receipt:
            raise AcquisitionError("snapshot current changed during inventory")
    except (OSError, json.JSONDecodeError) as exc:
        raise AcquisitionError("snapshot current changed during inventory") from exc
    return {
        "snapshot_id": snapshot_id, "period": item["period"], "source_id": registry["source_id"],
        "source_url": item["url"], "catalog_id": item["catalog_id"], "catalog_title": item["catalog_title"],
        "metadata_url": item["metadata_url"], "authority": registry["authority"], "license": registry["license"],
        "terms_url": registry["terms_url"], "registry_checked_at": registry["checked_at"],
        "acquired_at": receipt["completed_at"], "receipt_run_id": receipt["run_id"],
        "receipt_sha256": hashlib.sha256(json.dumps(receipt, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8")).hexdigest(),
        "receipt_started_at": receipt.get("started_at"), "receipt_completed_at": receipt["completed_at"],
        "raw_sha256": receipt["sha256"], "sdem_member": person_member, "dictionary_member": dictionary_member,
        "catalog_member": catalog_member, "sdem_header": header, "sdem_column_count": len(header),
        "geography_header": "CVE_ENT" if expected_new else "ENT", "geography_aliases": dict(zip(GEO_OLD, GEO_NEW)),
        "concept_equivalence_review": "REVIEW", "coding": coding, "cmpe_catalog_version": "CMPE 2016 (bundled cs_p14_c)",
        "revisions": revisions, "person_row_encoding": "UNRESOLVED",
        "transformation_note": "Metadata and full member hashes only; no person rows or ZIP bytes exported. CMPE keys are validated and zero-filled; unknown stays unknown.",
        "microdata_publication_approved": False,
    }


def inventory_snapshot(snapshot_id: str, output_root: Path, registry_path: Path | None = None) -> dict:
    """Inventory one approved current package, without network or writes."""
    registry, items = _registry(registry_path)
    if not isinstance(snapshot_id, str) or snapshot_id not in items:
        raise AcquisitionError("unknown or empty snapshot_id")
    return _inventory(snapshot_id, Path(output_root), registry_path, registry, items[snapshot_id])


def inventory_all(output_root: Path, registry_path: Path | None = None) -> list[dict]:
    """Return all eight current packages in approved chronological order."""
    registry, items = _registry(registry_path)
    return [_inventory(sid, Path(output_root), registry_path, registry, items[sid]) for sid in items]
