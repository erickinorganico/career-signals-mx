"""Offline source inventory controls.  Synthetic ZIPs contain no person data."""

import hashlib
import io
import json
import zipfile

import pytest

from brujula import acquisition
from brujula.source_inventory import inventory_all, inventory_snapshot


PERIODS = [f"{year}-Q{quarter}" for year, quarters in ((2024, (3, 4)), (2025, (1, 2, 3, 4)), (2026, (1, 2))) for quarter in quarters]


def _member_paths(period):
    year, quarter = period.split("-Q")
    stem = f"{year}_{quarter}t"
    root = f"conjunto_de_datos_sdem_enoe_{stem}"
    return (
        f"{root}/conjunto_de_datos/conjunto_de_datos_sdem_enoe_{stem}.csv",
        f"{root}/diccionario_de_datos/diccionario_datos_sdem_enoe_{stem}.csv",
        f"{root}/catalogos/cs_p14_c.csv",
    )


def _zip(period, extra=None, omit=()):
    person, dictionary, catalog = _member_paths(period)
    members = {
        person: b"ENT,CS_P14_C\n01,31300\n",
        dictionary: "NOMBRE_CAMPO,LONGITUD,TIPO,NEMÓNICO,CATÁLOGO,RANGO_CLAVES\nCampo,6,C,cs_p14_c,cs_p14_c,\n".encode(),
        catalog: "CVE,DESCRIP\n31300,Ciencias políticas\n32100,Comunicación y periodismo\n33100,Derecho\n".encode(),
    }
    for name in omit:
        members.pop(name)
    members.update(extra or {})
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, payload in members.items():
            archive.writestr(name, payload)
    return buffer.getvalue()


def _cache(tmp_path, overrides=None):
    root = tmp_path / "cache"
    registry = {"allowed_host": "www.inegi.org.mx", "max_download_bytes": 100000,
                "max_uncompressed_bytes": 100000, "source_id": "inegi_enoe",
                "authority": "INEGI", "terms_url": "https://www.inegi.org.mx/inegi/terminos.html",
                "license": "Libre uso", "checked_at": "2026-09-22", "publication_approved": False,
                "snapshots": []}
    for period in PERIODS:
        sid = "enoe_" + period.lower().replace("-", "_")
        payload = _zip(period, (overrides or {}).get(period))
        digest = hashlib.sha256(payload).hexdigest()
        registry["snapshots"].append({"id": sid, "period": period,
            "url": f"https://www.inegi.org.mx/{sid}.zip", "expected_sha256": digest,
            "acquisition_approved": True, "catalog_id": sid, "catalog_title": period,
            "metadata_url": f"https://www.inegi.org.mx/{sid}"})
        raw = root / "raw" / f"{digest}.zip"
        raw.parent.mkdir(parents=True, exist_ok=True)
        raw.write_bytes(payload)
        receipt = {"schema_version": "1.0", "run_id": f"run_{sid}", "snapshot_id": sid,
                   "status": "SUCCEEDED", "started_at": "2026-09-22T00:00:00Z",
                   "completed_at": "2026-09-22T00:01:00Z", "url": f"https://www.inegi.org.mx/{sid}.zip",
                   "sha256": digest, "bytes": len(payload), "mode": "cache_offline"}
        folder = root / "acquisitions" / sid
        (folder / "attempts").mkdir(parents=True)
        (folder / "current.json").write_text(json.dumps(receipt))
        (folder / "attempts" / f"run_{sid}.json").write_text(json.dumps(receipt))
    path = tmp_path / "registry.json"
    path.write_text(json.dumps(registry), encoding="utf-8")
    return root, path


def test_inventory_is_ordered_read_only_and_exact_member(tmp_path):
    root, registry = _cache(tmp_path, {"2024-Q3": {"other/sdem_enoe_2024_3t_bitacora_de_cambios.csv": b"junk"}})
    before = sorted(str(p) for p in root.rglob("*"))
    first = inventory_all(root, registry)
    second = inventory_all(root, registry)
    assert first == second
    assert [item["period"] for item in first] == PERIODS
    assert first[0]["sdem_member"]["path"] == _member_paths("2024-Q3")[0]
    assert first[0]["sdem_member"]["sha256"] == hashlib.sha256(b"ENT,CS_P14_C\n01,31300\n").hexdigest()
    assert sorted(str(p) for p in root.rglob("*")) == before
    assert "01,31300" not in json.dumps(first)


def test_failed_or_running_current_and_missing_attempt_block(tmp_path):
    root, registry = _cache(tmp_path)
    sid = "enoe_2024_q3"
    current = root / "acquisitions" / sid / "current.json"
    original = current.read_text()
    for status in ("FAILED", "RUNNING"):
        receipt = json.loads(original)
        receipt["status"] = status
        current.write_text(json.dumps(receipt))
        with pytest.raises(acquisition.AcquisitionError):
            inventory_snapshot(sid, root, registry)
    current.write_text(original)
    (current.parent / "attempts" / f"run_{sid}.json").unlink()
    with pytest.raises(acquisition.AcquisitionError):
        inventory_snapshot(sid, root, registry)


def test_empty_registry_unknown_id_and_raw_tamper_block(tmp_path):
    root, registry = _cache(tmp_path)
    with pytest.raises(acquisition.AcquisitionError):
        inventory_snapshot("missing", root, registry)
    config = json.loads(registry.read_text())
    config["snapshots"] = []
    registry.write_text(json.dumps(config))
    with pytest.raises(acquisition.AcquisitionError):
        inventory_all(root, registry)
    with pytest.raises(acquisition.AcquisitionError):
        inventory_snapshot("", root, registry)


def test_missing_exact_member_fails_even_with_similar_csv(tmp_path):
    period = "2024-Q3"
    root, registry = _cache(tmp_path)
    sid = "enoe_2024_q3"
    payload = _zip(period, extra={"other/sdem_enoe_2024_3t.csv": b"ENT\n"}, omit=(_member_paths(period)[0],))
    digest = hashlib.sha256(payload).hexdigest()
    (root / "raw" / f"{digest}.zip").write_bytes(payload)
    config = json.loads(registry.read_text())
    config["snapshots"][0]["expected_sha256"] = digest
    registry.write_text(json.dumps(config))
    receipt_path = root / "acquisitions" / sid / "current.json"
    receipt = json.loads(receipt_path.read_text())
    receipt["sha256"] = digest
    receipt_path.write_text(json.dumps(receipt))
    (receipt_path.parent / "attempts" / f"run_{sid}.json").write_text(json.dumps(receipt))
    with pytest.raises(acquisition.AcquisitionError):
        inventory_snapshot(sid, root, registry)
