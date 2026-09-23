from __future__ import annotations

import json
import math
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

from .resources import contract_path

SCHEMA_PATH = contract_path("dataset.schema.json")


def load_dataset(path: Path) -> dict[str, Any]:
    """Load one local dataset and fail closed on malformed JSON/schema."""
    dataset_path = Path(path)
    def reject_non_finite(value: str) -> None:
        raise ValueError(f"Non-finite JSON number: {value}")

    def parse_float(value: str) -> float:
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError(f"Non-finite JSON number: {value}")
        return parsed

    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"Duplicate JSON key: {key}")
            result[key] = value
        return result

    with dataset_path.open("r", encoding="utf-8") as handle:
        dataset = json.load(handle, parse_constant=reject_non_finite, parse_float=parse_float, object_pairs_hook=reject_duplicate_keys)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(dataset)
    if not isinstance(dataset, dict):
        raise TypeError("Dataset root must be an object")
    for row in dataset["observations"]:
        if row["value"] is not None and not math.isfinite(row["value"]):
            raise ValueError(f"Non-finite observation value: {row['id']}")
    return dataset
