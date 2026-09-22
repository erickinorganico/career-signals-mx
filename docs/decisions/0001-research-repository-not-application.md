# ADR-0001: Repositorio de investigación, no aplicación

## Status

Accepted

## Date

2026-09-22

## Context

El objetivo es producir evidencia reproducible, tablas, gráficas y briefs. Una
aplicación introduciría servidor, estado de UI, empaquetado y pruebas que no
mejoran la validez metodológica del primer release.

## Decision

La interfaz es CLI/archivos. Las salidas son DuckDB, CSV/Parquet autorizados,
Markdown/HTML y PNG/SVG. No se construye frontend, backend, API HTTP, dashboard
interactivo ni servicio.

## Alternatives considered

- Dashboard estático: rechazado en v1 porque desplaza esfuerzo desde contratos y
  comparabilidad.
- Aplicación local: diferida a una fase independiente tras validar utilidad.

## Consequences

El E2E termina en un research bundle y reporte estático. “Publisher” significa
gate de artefacto; publicar a GitHub es un proceso de release separado. Esta
decisión está aceptada, aunque el renderer aún no está implementado.
