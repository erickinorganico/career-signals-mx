"""Offline source inventory controls.  Synthetic ZIPs contain no person data."""

import hashlib
import io
import json
import zipfile

import pytest

from brujula import acquisition
from brujula.source_inventory import inventory_all, inventory_snapshot, normalize_cmpe_code


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
    geo = "CVE_AGEB,CVE_ENT,CVE_LOC,CVE_MUN,CVEGEO" if period >= "2025-Q3" else "AGEB,ENT,LOC,MUN"
    members = {
        person: f"{geo},CS_P14_C\n".encode(),
        dictionary: "NOMBRE_CAMPO,LONGITUD,TIPO,NEMÓNICO,CATÁLOGO,RANGO_CLAVES\nCampo,6,C,cs_p14_c,cs_p14_c,\n".encode(),
        catalog: "CVE,DESCRIP\n31300,Ciencias políticas\n32100,Comunicación y periodismo\n33100,Derecho\n".encode(),
    }
    if period in ("2024-Q3", "2024-Q4"):
        year, quarter = period.split("-Q")
        root = f"conjunto_de_datos_sdem_enoe_{year}_{quarter}t/conjunto_de_datos"
        fields = ["cs_p14_c"] * 4 if quarter == "3" else ["cs_p14_c"] * 5 + ["par_c", "cs_p20a_c"] + ["cs_p20b_c"] * 2
        members[f"{root}/sdem_enoe_{year}_{quarter}t_bitacora_de_cambios.csv"] = ("Nombre de campo,Fecha de modificación\n" + "".join(f"{field},27/05/2025\n" for field in fields)).encode()
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
    assert first[0]["sdem_member"]["sha256"] == hashlib.sha256(b"AGEB,ENT,LOC,MUN,CS_P14_C\n").hexdigest()
    assert sorted(str(p) for p in root.rglob("*")) == before
    assert "person record" not in json.dumps(first)


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


def test_revision_log_is_required_and_exact_for_2024(tmp_path):
    root, registry = _cache(tmp_path)
    sid = "enoe_2024_q3"
    assert inventory_snapshot(sid, root, registry)["revisions"]["fields"] == {"cs_p14_c": 4}
    _replace_zip(tmp_path, root, registry, "2024-Q3", _zip("2024-Q3", omit=(
        "conjunto_de_datos_sdem_enoe_2024_3t/conjunto_de_datos/sdem_enoe_2024_3t_bitacora_de_cambios.csv",)))
    with pytest.raises(acquisition.AcquisitionError, match="bitácora"):
        inventory_snapshot(sid, root, registry)


def _replace_zip(tmp_path, root, registry, period, payload):
    sid = "enoe_" + period.lower().replace("-", "_")
    digest = hashlib.sha256(payload).hexdigest()
    (root / "raw" / f"{digest}.zip").write_bytes(payload)
    config = json.loads(registry.read_text(encoding="utf-8"))
    item = next(x for x in config["snapshots"] if x["id"] == sid)
    item["expected_sha256"] = digest
    registry.write_text(json.dumps(config), encoding="utf-8")
    current = root / "acquisitions" / sid / "current.json"
    receipt = json.loads(current.read_text())
    receipt["sha256"] = digest
    current.write_text(json.dumps(receipt))
    (current.parent / "attempts" / f"run_{sid}.json").write_text(json.dumps(receipt))


def test_catalog_encoding_alias_and_provenance_fail_closed(tmp_path):
    root, registry = _cache(tmp_path)
    period = "2025-Q3"
    sid = "enoe_2025_q3"
    catalog = _member_paths(period)[2]
    _replace_zip(tmp_path, root, registry, period, _zip(period, extra={catalog: b"CVE,DESCRIP\n31300,\xff\n"}))
    with pytest.raises(acquisition.AcquisitionError, match="UTF-8"):
        inventory_snapshot(sid, root, registry)
    person = _member_paths(period)[0]
    _replace_zip(tmp_path, root, registry, period, _zip(period, extra={person: b"ENT,CVE_ENT,CS_P14_C\n"}))
    with pytest.raises(acquisition.AcquisitionError, match="geography"):
        inventory_snapshot(sid, root, registry)
    config = json.loads(registry.read_text())
    config["terms_url"] = ""
    registry.write_text(json.dumps(config))
    with pytest.raises(acquisition.AcquisitionError, match="terms_url"):
        inventory_snapshot(sid, root, registry)
    config["terms_url"] = "https://www.inegi.org.mx/inegi/terminos.html"
    registry.write_text(json.dumps(config))
    current = root / "acquisitions" / sid / "current.json"
    receipt = json.loads(current.read_text())
    receipt["completed_at"] = None
    current.write_text(json.dumps(receipt))
    (current.parent / "attempts" / f"run_{sid}.json").write_text(json.dumps(receipt))
    with pytest.raises(acquisition.AcquisitionError, match="completed_at"):
        inventory_snapshot(sid, root, registry)


def test_unknown_cmpe_code_is_null(tmp_path):
    root, registry = _cache(tmp_path)
    item = inventory_snapshot("enoe_2025_q2", root, registry)
    assert normalize_cmpe_code("31300", item["coding"]) == "031300"
    assert normalize_cmpe_code("999999", item["coding"]) is None
    assert normalize_cmpe_code(None, item["coding"]) is None
    assert normalize_cmpe_code("99999", item["coding"]) is None


def test_newer_failed_attempt_cannot_hide_behind_successful_current(tmp_path):
    root, registry = _cache(tmp_path)
    sid = "enoe_2024_q3"
    folder = root / "acquisitions" / sid / "attempts"
    (folder / "zz_later.json").write_text(json.dumps({"status": "FAILED", "run_id": "zz_later"}))
    with pytest.raises(acquisition.AcquisitionError, match="newer attempt"):
        inventory_snapshot(sid, root, registry)


def test_all_eight_cached_offline_when_present(monkeypatch):
    from pathlib import Path
    root = Path("artifacts/enoe")
    if not root.exists():
        pytest.skip("local eight-package cache absent; offline acceptance remains incomplete")
    monkeypatch.setattr(acquisition, "_download", lambda *args, **kwargs: pytest.fail("inventory used network downloader"))
    items = inventory_all(root)
    expected_member_hashes = (
        "a2b8ea7a64ae2c6b428526da24c6c62894decd7d1b0520853472966e69522135",
        "b5d39d8b6afa2c554f3f68a225293d4ab6531706823d2c9084b7c002ae769f86",
        "bcb310cbd5b695db264da0f0dcaef266d047a037486853012e5cbc096d7abbf5",
        "c9f1a2adf14b388be7d1a68ef57d30fd92356d36f522cc7e3ac32de6ab5a48d8",
        "04bd5d5f9668848ac6c435f29abe3b20e6693f02f2ee880a1e9dc0aab1c94c9d",
        "088a2affeaef800bd9941656869392290905a9cf597af42a15d748b13b43de7e",
        "8bf2b74f4222b72c5d717509a7527213346564f17acd1affdce7f50bd21daeca",
        "6256468cd6cf5ed08b8538f8094eb3cf20793cb669ba0084c18f571fc8f78407",
    )
    assert [x["period"] for x in items] == PERIODS
    assert tuple(x["sdem_member"]["sha256"] for x in items) == expected_member_hashes
    assert [x["sdem_column_count"] for x in items] == [114] * 4 + [115] * 4
    assert [x["geography_header"] for x in items] == ["ENT"] * 4 + ["CVE_ENT"] * 4
    assert [x["revisions"]["count"] for x in items[:2]] == [4, 9]
    assert [x["revisions"]["date"] for x in items[:2]] == ["2025-05-27"] * 2
    assert all(x["terms_url"] and x["acquired_at"] and x["sdem_member"]["sha256"] for x in items)
    assert len({x["catalog_member"]["sha256"] for x in items}) == 1
    assert items[2]["dictionary_member"]["sha256"] != items[1]["dictionary_member"]["sha256"]
    assert all(x["coding"]["focus_codes"]["31300"]["code"] == "031300" for x in items)
    encoded = json.dumps(items, ensure_ascii=False)
    assert not encoded.startswith("PK") and "27/05/2025" not in encoded
    assert all(x["microdata_publication_approved"] is False for x in items)
