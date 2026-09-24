# Portable paths in historical execution records

Machine-specific prefixes in planning records are represented by these explicit placeholders. They preserve the referenced file, temporary environment identity and verification result; they are not literal shell commands or evidence of an installation on another computer.

| Placeholder | Resolve on the local machine |
|---|---|
| `${GSD_CORE}` | Root of the installed GSD runtime containing `bin/gsd-tools.cjs`, `workflows/` and `templates/`. |
| `${CODEX_SKILLS}` | Skills directory containing the named `gsd-*` skill. |
| `${UV_EXECUTABLE}` | Full path to the available `uv` executable. |
| `${TEMP}` | Operating-system temporary directory used for the recorded isolated environment. |

Repository file references are relative to the repository root. Expand these placeholders using the actual local installation before invoking a workflow. Historical temporary paths document import isolation; they are not required to exist on a reader's machine. Source, wheel, manifest and receipt hashes remain unchanged.
