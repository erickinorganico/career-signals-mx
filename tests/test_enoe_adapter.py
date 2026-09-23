"""Synthetic ENOE frame controls; no official person rows are stored here."""

import hashlib
import io
import json
import zipfile

import numpy as np
import pytest
from brujula.populations import normalize_cmpe_key

from brujula.acquisition import AcquisitionError
from brujula.enoe_adapter import load_snapshot_frame
from test_source_inventory import _cache, _member_paths


HEADER = "r_def,c_res,eda,cs_p13_1,cs_p16,cs_p14_c,est_d_tri,upm,fac_tri,sex,clase1,clase2,ing7c,ingocup,emp_ppal,pos_ocu,sub_o,dur9c,hrsocup,ent,ageb,loc,mun"
ROWS = [
    "0,1,15,7,1, 33100,1,11,2,2,1,1,1,100,1,1,1,2,40,02",
    "00,3,98,7,1,999999,1,11,3,1,1,2,7,999999,0,5,0,9,0,02",
    "0,1,97,7,1,31300,1,12,4,2,1,1,6,0,2,2,0,1,0,03",
    "15,1,30,7,1,33100,2,20,5,1,1,1,1,500,1,1,0,2,40,03",
]


def fixture(tmp_path, rows=ROWS, header=HEADER, snapshot_id="enoe_2025_q2"):
    root, registry = _cache(tmp_path)
    sid = snapshot_id
    period = next(x["period"] for x in json.loads(registry.read_text())["snapshots"] if x["id"] == sid)
    if header == HEADER and period >= "2025-Q3":
        header = HEADER.replace(",ent,ageb,loc,mun", ",cve_ent,cve_ageb,cve_loc,cve_mun")
    member = _member_paths(period)[0]
    item = next(x for x in json.loads(registry.read_text())["snapshots"] if x["id"] == sid)
    old = root / "raw" / f"{item['expected_sha256']}.zip"
    with zipfile.ZipFile(old) as archive:
        content = {x.filename: archive.read(x) for x in archive.infolist()}
    content[member] = (header + "\n" + "\n".join(row + ",1,1,1" if row else row for row in rows) + "\n").encode("latin1")
    dictionary = _member_paths(period)[1]
    content[dictionary] = ("NOMBRE_CAMPO,LONGITUD,TIPO,NEMÓNICO,CATÁLOGO,RANGO_CLAVES\n" +
        "".join(f"Campo,{6 if field == 'cs_p14_c' else 2},C,{field},{'cs_p14_c' if field == 'cs_p14_c' else ''},\n"
                for field in set(header.split(',')))).encode("utf-8")
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        for name, data in content.items():
            archive.writestr(name, data)
    data = buffer.getvalue()
    digest = hashlib.sha256(data).hexdigest()
    (root / "raw" / f"{digest}.zip").write_bytes(data)
    config = json.loads(registry.read_text())
    config["synthetic_fixture"] = True
    next(x for x in config["snapshots"] if x["id"] == sid)["expected_sha256"] = digest
    registry.write_text(json.dumps(config))
    folder = root / "acquisitions" / sid
    receipt = json.loads((folder / "current.json").read_text())
    receipt.update(sha256=digest, bytes=len(data))
    (folder / "current.json").write_text(json.dumps(receipt))
    (folder / "attempts" / f"{receipt['run_id']}.json").write_text(json.dumps(receipt))
    return sid, root, registry


def test_complete_frame_design_and_order(tmp_path):
    sid, root, registry = fixture(tmp_path)
    frame, audit = load_snapshot_frame(sid, root, registry)
    assert len(frame.weight) == 3
    assert audit["raw_rows"] == 4 and audit["frame_rows"] == 3
    assert frame.synthetic is True and audit["synthetic"] is True
    assert audit["provenance"] == "declared_synthetic_fixture"
    assert audit["design"]["psus"] == 2 and audit["design"]["strata"] == 1
    assert frame.age.tolist() == [15, 98, 97]
    assert frame.cmpe.tolist() == ["033100", None, "031300"]
    assert frame.cmpe_catalog_labels["033100"] == "Derecho"
    assert frame.cmpe_catalog_labels["031300"] == "Ciencias políticas"
    assert "999999" not in frame.cmpe_catalog_labels
    with pytest.raises(TypeError):
        frame.cmpe_catalog_labels["033100"] = "changed"
    assert audit["lexemes"]["cs_p14_c"]["space_padded"] == 1
    assert not any(isinstance(value, list) for value in audit.values())
    sid2, root2, registry2 = fixture(tmp_path / "other", rows=list(reversed(ROWS)))
    _, reverse_audit = load_snapshot_frame(sid2, root2, registry2)
    assert audit["design"] == reverse_audit["design"]
    assert audit["frame_rows"] == reverse_audit["frame_rows"]


@pytest.mark.parametrize("snapshot_id,geography_field", [
    ("enoe_2025_q2", "ent"), ("enoe_2025_q3", "cve_ent"),
])
def test_geography_aliases_materialize_canonical_integer_codes(tmp_path, snapshot_id, geography_field):
    sid, root, registry = fixture(tmp_path, snapshot_id=snapshot_id)
    frame, audit = load_snapshot_frame(sid, root, registry)
    values = frame.columns[geography_field]
    assert values.dtype == np.int64
    # Source cells are zero-prefixed strings (02/03); selectors consume ints.
    assert values.tolist() == [2, 2, 3]
    assert audit["lexemes"][geography_field]["digits"] == 3


def test_missing_geography_is_unknown_and_cannot_match_valid_entity(tmp_path):
    missing = ROWS[0].removesuffix(",02") + ","
    sid, root, registry = fixture(tmp_path, rows=[missing, ROWS[1], ROWS[2]])
    frame, _ = load_snapshot_frame(sid, root, registry)
    assert frame.columns["ent"].tolist() == [-1, 2, 3]
    assert not np.any(frame.columns["ent"] == 1)


@pytest.mark.parametrize("bad", ["0,1", "0,1,30,7,1,33100,1,11,0,2,1,1,1,100,1,1,1,2,40,02", "0,1,30,7,1,33100,1,11,1e309,2,1,1,1,100,1,1,1,2,40,02", "0,1,30,7,1,33100,1,11,2,2,1,1,1,100,1,1,1,2,40,\u00a002"])
def test_invalid_design_or_code_fails(tmp_path, bad):
    sid, root, registry = fixture(tmp_path, rows=[bad, ROWS[1], ROWS[2]])
    with pytest.raises((AcquisitionError, ValueError)):
        load_snapshot_frame(sid, root, registry)


def test_empty_singleton_duplicate_and_failed_current(tmp_path):
    for index, rows in enumerate(([], ROWS[:1])):
        sid, root, registry = fixture(tmp_path / str(index), rows=rows)
        with pytest.raises(AcquisitionError):
            load_snapshot_frame(sid, root, registry)
    sid, root, registry = fixture(tmp_path / "duplicate", header=HEADER + ",EDA")
    with pytest.raises(AcquisitionError):
        load_snapshot_frame(sid, root, registry)


def test_same_upm_label_in_two_strata_is_two_clusters(tmp_path):
    second = ROWS[2].replace(",1,12,4,", ",2,11,4,")
    sid, root, registry = fixture(tmp_path, rows=[ROWS[0], ROWS[1], second])
    _, audit = load_snapshot_frame(sid, root, registry)
    assert audit["design"] == {"strata": 2, "psus": 2, "singleton_strata": 2}


def test_weight_overflow_fails_before_estimation(tmp_path):
    giant = ROWS[0].replace(",1,11,2,", ",1,11," + "9" * 400 + ",")
    sid, root, registry = fixture(tmp_path, rows=[giant, ROWS[1], ROWS[2]])
    with pytest.raises(AcquisitionError):
        load_snapshot_frame(sid, root, registry)


def test_cmpe_lookup_matches_phase1_normalizer(tmp_path):
    sid, root, registry = fixture(tmp_path)
    frame, _ = load_snapshot_frame(sid, root, registry)
    for raw, actual in ((" 33100", frame.cmpe[0]), ("999999", frame.cmpe[1]), ("31300", frame.cmpe[2])):
        assert actual == normalize_cmpe_key(raw, frame.cmpe_catalog_keys)


def test_custom_unmarked_registry_cannot_impersonate_official(tmp_path):
    sid, root, registry = fixture(tmp_path)
    config = json.loads(registry.read_text())
    config.pop("synthetic_fixture")
    registry.write_text(json.dumps(config))
    with pytest.raises(AcquisitionError, match="provenance"):
        load_snapshot_frame(sid, root, registry)
    sid, root, registry = fixture(tmp_path / "failed")
    current = root / "acquisitions" / sid / "current.json"
    receipt = json.loads(current.read_text()); receipt["status"] = "FAILED"; current.write_text(json.dumps(receipt))
    with pytest.raises(AcquisitionError):
        load_snapshot_frame(sid, root, registry)
