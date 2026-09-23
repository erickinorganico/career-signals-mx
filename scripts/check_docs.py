"""Offline documentation checks. This does not certify the analytical release."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
LINK = re.compile(r"(?<!!)\[[^\]\n]+\]\((<[^>]+>|[^)\s]+)(?:\s+\"[^\"]*\")?\)")
IMAGE = re.compile(r"!\[[^\]\n]*\]\(([^)\s]+)\)")
SECRET_PATTERNS = [
    re.compile(r"gh[opusr]_[A-Za-z0-9]{30,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{30,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}"),
]


def repository_files() -> list[Path]:
    result = list(ROOT.glob("*.md"))
    for directory in ("docs", "brujula", "contracts", "data", "tests", "scripts", "evals", ".github"):
        root = ROOT / directory
        if root.exists():
            result.extend(p for p in root.rglob("*") if p.is_file() and "__pycache__" not in p.parts
                          and p.suffix in {".md", ".json", ".py", ".toml", ".ps1", ".sh", ".yml"})
    result += [ROOT / p for p in ("pyproject.toml", "requirements.txt", "LICENSE", ".gitignore")]
    return sorted(set(p for p in result if p.exists()))


def main() -> int:
    errors = []
    links = 0
    documents = 0
    json_files = 0
    files = repository_files()
    for path in files:
        text = path.read_text(encoding="utf-8-sig")
        relative = path.relative_to(ROOT).as_posix()
        if any(pattern.search(text) for pattern in SECRET_PATTERNS):
            errors.append(f"{relative}: potential credential; inspect privately (value suppressed)")
        if re.search(r"[A-Z]:[\\/]Users[\\/]", text, flags=re.I):
            errors.append(f"{relative}: machine-specific personal path")
        if path.suffix == ".json":
            json_files += 1
            try:
                json.loads(text, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(f"Nonfinite JSON: {value}")))
            except (ValueError, json.JSONDecodeError) as exc:
                errors.append(f"{relative}: invalid JSON: {type(exc).__name__}")
        if path.suffix != ".md":
            continue
        documents += 1
        outside_fences = re.sub(r"```[^\n]*\n.*?```", "", text, flags=re.S)
        targets = [match.group(1).strip("<>") for match in LINK.finditer(outside_fences)]
        targets += [match.group(1) for match in IMAGE.finditer(outside_fences)]
        for target in targets:
            parsed = urlsplit(target)
            if parsed.scheme in {"http", "https", "mailto"} or target.startswith("#"):
                continue
            if parsed.scheme:
                errors.append(f"{relative}: unsupported link scheme")
                continue
            links += 1
            location = (path.parent / unquote(parsed.path)).resolve()
            if not location.is_relative_to(ROOT) or not location.exists():
                errors.append(f"{relative}: broken local link {target}")
    mandatory = ["README.md", "README.en.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "PROJECT-EFFICIENCY.md", "CONTRIBUTING.md",
                 *[f"docs/{name}.md" for name in ("README", "PROJECT-CHARTER", "SCOPE", "PRD", "PLAN", "ROADMAP", "RISKS", "ARCHITECTURE", "SPEC", "CONTRACT", "METHODOLOGY", "GLOSSARY", "SOURCES", "STATUS", "VALIDATION-PLAN", "ORCHESTRATION", "VISUALIZATION", "PLANNING-REVIEW")],
                 "docs/decisions/README.md"]
    for required in mandatory:
        if not (ROOT / required).is_file():
            errors.append(f"missing planning deliverable: {required}")
    print(json.dumps({"status": "PASS" if not errors else "FAIL", "scope": "local documentation links, required planning files, JSON syntax and heuristic credential/path scan; no network or runtime certification",
                      "files_scanned": len(files), "markdown_files": documents, "local_links_checked": links,
                      "json_files": json_files, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
