# ADR-0005: Un fallo vigente prevalece sobre un éxito histórico

## Status

Accepted

## Date

2026-09-22

## Context

Mantener silenciosamente el último reporte exitoso después de una actualización
fallida haría parecer actuales datos que ya no pudieron regenerarse.

## Decision

Cada intento obtiene un run histórico. Al comenzar se invalida `current`;
`current.json` es la única autoridad y permanece `BLOCKED` durante la ejecución
y ante un fallo. El receipt final y los artefactos sellados son inmutables.
`report.md` es un índice humano derivado: si quedó atrasado por una interrupción,
su enlace se rechaza y se regenera desde el puntero validado. No se requiere
una transacción entre ambos archivos. El éxito anterior sigue auditable dentro
de `runs/`, nunca como fallback current.

## Alternatives considered

- Last-known-good: rechazado por riesgo de falsa frescura.
- Borrar runs fallidos: rechazado porque elimina evidencia diagnóstica.

## Consequences

Los consumidores deben leer `current.json`. El pipeline necesita reemplazo
atómico de ese puntero, receipts finales inmutables y tests de recuperación
antes y después del commit y de la actualización del índice humano.
