"""Verified ENOE SDEM to one in-memory complete responding/resident frame.

Only aggregate custody and lexical diagnostics leave this module. Person columns
remain in memory and are never included in the audit mapping.
"""

from __future__ import annotations

import csv
import io
import math
import re
import zipfile
from collections import Counter, defaultdict
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from .acquisition import AcquisitionError, resolve_snapshot
from .populations import normalize_cmpe_key
from .source_inventory import inventory_snapshot


COLUMNS = (
    "r_def", "c_res", "eda", "cs_p13_1", "cs_p16", "cs_p14_c",
    "est_d_tri", "upm", "fac_tri", "sex", "clase1", "clase2",
    "ing7c", "ingocup", "emp_ppal", "pos_ocu", "sub_o", "dur9c",
    "hrsocup",
)
NUMERIC = set(COLUMNS) - {"est_d_tri", "upm", "fac_tri", "cs_p14_c"}
ASCII = re.compile(r"[0-9]+\Z", re.ASCII)


@dataclass(frozen=True, slots=True)
class Frame:
    """Column arrays aligned to the entire valid response/resident design."""

    snapshot_id: str
    period: str
    source_id: str
    inventory: dict
    cmpe_catalog_keys: frozenset[str]
    columns: dict[str, np.ndarray]

    def __len__(self) -> int:
        return len(self.columns["fac_tri"])

    def __getattr__(self, name: str) -> np.ndarray:
        try:
            return self.columns[name]
        except KeyError as exc:
            raise AttributeError(name) from exc

    @property
    def weight(self) -> np.ndarray:
        return self.columns["fac_tri"]

    @property
    def age(self) -> np.ndarray:
        return self.columns["eda"]

    @property
    def cmpe(self) -> np.ndarray:
        return self.columns["cs_p14_c"]


def _lex(raw: str | None, field: str, counts: Counter) -> str | None:
    if not isinstance(raw, str):
        raise AcquisitionError(f"missing SDEM {field} cell")
    counts["raw_cells"] += 1
    if raw == "":
        counts["empty"] += 1
        return None
    value = raw.strip(" ")
    if value == "":
        counts["space_blank"] += 1
        return None
    if value != raw:
        counts["space_padded"] += 1
    if ASCII.fullmatch(value) is None:
        raise AcquisitionError(f"unsupported SDEM numeric token in {field}")
    counts["digits"] += 1
    return value


def _catalog(archive: zipfile.ZipFile, member: str) -> frozenset[str]:
    with archive.open(member) as stream:
        reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
        keys = [row.get("CVE") for row in reader]
    if not keys or any(not isinstance(key, str) for key in keys):
        raise AcquisitionError("CMPE catalog lacks keys")
    # This validates the entire period catalog, including normalized collisions.
    # The official catalog carries 999999 as its unknown sentinel; it is not
    # an eligible field key for the population normalizer.
    valid_keys = [key for key in keys if key != "999999"]
    normalize_cmpe_key("", valid_keys)
    return frozenset(valid_keys)


def _dictionary(archive: zipfile.ZipFile, member: str, required: set[str]) -> None:
    with archive.open(member) as stream:
        reader = csv.DictReader(io.TextIOWrapper(stream, encoding="utf-8-sig", newline=""))
        if not reader.fieldnames or "NEMÓNICO" not in reader.fieldnames:
            raise AcquisitionError("SDEM dictionary is malformed")
        names = Counter((row.get("NEMÓNICO") or "").lower() for row in reader)
    if any(names[name] != 1 for name in required):
        raise AcquisitionError("SDEM dictionary lacks a unique required field")


def load_snapshot_frame(snapshot_id: str, output_root: Path, registry_path: Path | None = None) -> tuple[Frame, dict]:
    """Load a pinned current ZIP once into columns, retaining all design PSUs."""
    inventory = inventory_snapshot(snapshot_id, Path(output_root), registry_path)
    if inventory["source_id"] != "inegi_enoe" or inventory["microdata_publication_approved"] is not False:
        raise AcquisitionError("unapproved source identity or publication state")
    path, receipt = resolve_snapshot(snapshot_id, Path(output_root), registry_path)
    if receipt["sha256"] != inventory["raw_sha256"] or receipt["run_id"] != inventory["receipt_run_id"]:
        raise AcquisitionError("snapshot changed after inventory")
    member = inventory["sdem_member"]["path"]
    required = set(COLUMNS) | {inventory["geography_header"].lower()}
    lexical = defaultdict(Counter)
    buffers: dict[str, list] = {field: [] for field in required}
    raw_rows = 0
    excluded = Counter()
    with zipfile.ZipFile(path) as archive:
        catalog = _catalog(archive, inventory["catalog_member"]["path"])
        _dictionary(archive, inventory["dictionary_member"]["path"], required)
        with archive.open(member) as binary:
            reader = csv.DictReader(io.TextIOWrapper(binary, encoding="latin1", newline=""), strict=True)
            header = reader.fieldnames
            if not header or len(header) != len(set(header)) or set(header) != set(inventory["sdem_header"]):
                raise AcquisitionError("SDEM header changed or duplicated")
            if not required.issubset(header):
                raise AcquisitionError("SDEM header lacks required fields")
            try:
                for row in reader:
                    raw_rows += 1
                    if None in row or any(row.get(field) is None for field in required):
                        raise AcquisitionError("malformed SDEM row width")
                    response = _lex(row["r_def"], "r_def", lexical["r_def"])
                    residence = _lex(row["c_res"], "c_res", lexical["c_res"])
                    if response not in {"0", "00"}:
                        excluded["response"] += 1
                        continue
                    if residence not in {"1", "3"}:
                        excluded["residence"] += 1
                        continue
                    for field in required:
                        if field in ("r_def", "c_res"):
                            value = response if field == "r_def" else residence
                        else:
                            value = _lex(row[field], field, lexical[field])
                        if field in {"fac_tri", "est_d_tri", "upm"} and value is None:
                            raise AcquisitionError(f"missing design field {field}")
                        if field == "fac_tri":
                            weight = float(value)
                            if not math.isfinite(weight) or weight <= 0:
                                raise AcquisitionError("FAC_TRI must be positive and finite")
                            value = weight
                        elif field == "cs_p14_c":
                            value = normalize_cmpe_key(value, catalog)
                        elif field in NUMERIC:
                            value = int(value) if value is not None else -1
                        buffers[field].append(value)
            except (csv.Error, UnicodeDecodeError, OverflowError) as exc:
                raise AcquisitionError("SDEM CSV cannot be decoded safely") from exc
    count = len(buffers["fac_tri"])
    if count < 2:
        raise AcquisitionError("complete response/resident frame has fewer than two rows")
    arrays = {
        field: np.asarray(values, dtype=np.float64 if field == "fac_tri" else np.int64 if field in NUMERIC else object)
        for field, values in buffers.items()
    }
    if not np.isfinite(np.sum(arrays["fac_tri"], dtype=np.float64)):
        raise AcquisitionError("FAC_TRI aggregate overflow")
    pairs = set(zip(arrays["est_d_tri"], arrays["upm"]))
    strata = set(arrays["est_d_tri"])
    psus_by_stratum: dict[str, set[str]] = defaultdict(set)
    for stratum, psu in pairs:
        psus_by_stratum[stratum].add(psu)
    if len(pairs) < 2:
        raise AcquisitionError("complete frame has fewer than two design PSUs")
    after_path, after_receipt = resolve_snapshot(snapshot_id, Path(output_root), registry_path)
    if after_path != path or after_receipt != receipt:
        raise AcquisitionError("snapshot changed during frame load")
    frame = Frame(snapshot_id, inventory["period"], inventory["source_id"], inventory, catalog, arrays)
    audit = {
        "snapshot_id": snapshot_id, "period": inventory["period"], "source_id": inventory["source_id"],
        "raw_sha256": inventory["raw_sha256"], "sdem_sha256": inventory["sdem_member"]["sha256"],
        "dictionary_sha256": inventory["dictionary_member"]["sha256"], "catalog_sha256": inventory["catalog_member"]["sha256"],
        "raw_rows": raw_rows, "frame_rows": count, "excluded": dict(sorted(excluded.items())),
        "design": {"strata": len(strata), "psus": len(pairs), "singleton_strata": sum(len(psus) == 1 for psus in psus_by_stratum.values())},
        "lexemes": {field: dict(sorted(counts.items())) for field, counts in sorted(lexical.items())},
    }
    return frame, audit
