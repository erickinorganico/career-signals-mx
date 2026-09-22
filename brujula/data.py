from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from jsonschema import Draft202012Validator, FormatChecker

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "contracts" / "dataset.schema.json"


def load_dataset(path: Path) -> dict[str, Any]:
    """Load one local dataset and fail closed on malformed JSON/schema."""
    dataset_path = Path(path)
    with dataset_path.open("r", encoding="utf-8") as handle:
        dataset = json.load(handle)
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator(schema, format_checker=FormatChecker()).validate(dataset)
    return dataset
