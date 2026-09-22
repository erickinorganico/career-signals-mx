# Índice de decisiones arquitectónicas

Los ADRs registran decisiones aceptadas y su razón. **Accepted no significa
implementado ni verificado.** El estado real se consulta en
[ARCHITECTURE.md](../ARCHITECTURE.md) y [SPEC.md](../SPEC.md).

| ADR | Estado | Decisión |
|---|---|---|
| [ADR-0001](0001-research-repository-not-application.md) | Accepted | repositorio de investigación, no aplicación |
| [ADR-0002](0002-python-duckdb-without-required-dbt.md) | Accepted | Python + DuckDB; dbt no obligatorio |
| [ADR-0003](0003-synthetic-first-source-policy.md) | Accepted | piloto sintético y activación explícita de fuentes |
| [ADR-0004](0004-agent-and-publisher-authority.md) | Accepted | agentes read-only y Publisher limitado al artefacto |
| [ADR-0005](0005-current-failure-wins-over-historical-success.md) | Accepted | fallo current prevalece sobre éxito histórico |

Cuando una decisión cambie, se crea un ADR nuevo que marca el anterior como
Superseded; no se elimina historial.
