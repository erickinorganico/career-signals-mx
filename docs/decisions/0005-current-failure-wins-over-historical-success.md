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
El lock persistente del sistema operativo se libera tras un cierre normal y el
arranque siguiente recupera un `RUNNING` dejado por crash. Si la generación ya
selló `SUCCEEDED` y falla la publicación, se conserva el receipt y se escribe un
`publication-failure.json` separado; `current` queda `BLOCKED`.
`report.md` es un índice humano derivado: si quedó atrasado por una interrupción,
su enlace se rechaza y se regenera desde el puntero validado. No se requiere
una transacción entre ambos archivos. El éxito anterior sigue auditable dentro
de `runs/`, nunca como fallback current.

## Alternatives considered

- Last-known-good: rechazado por riesgo de falsa frescura.
- Borrar runs fallidos: rechazado porque elimina evidencia diagnóstica.

## Consequences

Los consumidores deben leer `current.json`. El pipeline usa reemplazo atómico,
manifiesto con hash de todos los artefactos y receipts finales inmutables. El
CLI rechaza un puntero RUNNING/BLOCKED o un manifest inconsistente; un fallo del
índice humano después del commit no revoca el éxito canónico. Un receipt de
ejecución no equivale a publicación remota.
