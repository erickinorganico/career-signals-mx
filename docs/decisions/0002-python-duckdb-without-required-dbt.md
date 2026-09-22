# ADR-0002: Python y DuckDB; dbt no obligatorio

## Status

Accepted

## Date

2026-09-22

## Context

El piloto es pequeño, local-first y debe funcionar sin servicios ni
credenciales. Requiere schemas, transformaciones deterministas y SQL auditable.

## Decision

Usar Python 3.12, JSON Schema y DuckDB con dependencias fijadas. DuckDB es una
materialización local por run. dbt Core/dbt-duckdb no es requisito del v1.

## Alternatives considered

- SQLite: menos conveniente para Parquet y análisis columnar.
- PostgreSQL: requiere servicio y operación innecesarios.
- dbt desde M1: aporta lineage, pero añade estructura antes de demostrar que el
  número de modelos la justifica.

## Consequences

Las relaciones y tests deben ser explícitos en Python/SQL. dbt puede proponerse
después si reduce trabajo total y mejora lineage. La decisión no afirma que el
warehouse actual tenga todas las FK o checks objetivo.
