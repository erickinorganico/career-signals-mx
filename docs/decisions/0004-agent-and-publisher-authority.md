# ADR-0004: Agentes read-only y autoridad limitada del Publisher

## Status

Accepted

## Date

2026-09-22

## Context

Los agentes pueden acelerar investigación y redacción, pero no deben transformar
una sugerencia en fuente activa, dato canónico o claim publicado.

## Decision

Todos los roles agentic son deterministas y read-only en v1. Producen propuestas
estructuradas con evidencia. Source Scout no activa fuentes; Schema Mapper no
aprueba bridges; Insight Analyst no calcula; Visualization Planner no cambia
datos; Publisher solo permite o bloquea el artefacto analítico.

## Alternatives considered

- Agentes con escritura directa: rechazado por pérdida de trazabilidad.
- Inferencia pagada obligatoria: rechazada por reproducibilidad/costo.
- Sin agentes: rechazado porque impediría probar el contrato de propuestas y
  gates, aunque el cálculo permanezca determinista.

## Consequences

La publicación GitHub autorizada la ejecuta el flujo de desarrollo después de
secret/license/method review; no el rol Publisher. Laya solo puede entrar a un
caller repetido tras baseline, evals, fallback y shadow mode.
