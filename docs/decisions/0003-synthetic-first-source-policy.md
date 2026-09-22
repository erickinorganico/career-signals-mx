# ADR-0003: Piloto sintético y activación explícita de fuentes reales

## Status

Accepted

## Date

2026-09-22

## Context

Las fuentes candidatas difieren en términos, población y método. Calcular ENOE
por campo exige clasificación, ponderadores y varianza de diseño verificados.

## Decision

El release inicial usa un fixture sintético 3×3×2×3, siempre `REVIEW`. El
catálogo de fuentes permanece separado. ENOE es candidata priorizada para M6,
con `numeric_ingestion_allowed=false` hasta aprobar un snapshot concreto. No se
redistribuyen cifras de OLA, Data México o IMCO sin licencia clara.

## Alternatives considered

- Copiar cifras de portales: rechazado por términos, reproducibilidad y
  ambigüedad metodológica.
- Calcular ENOE inmediatamente: diferido hasta implementar el diseño complejo.

## Consequences

El fixture prueba flujo, no resultados del mercado. El reporte debe advertirlo.
La activación real requiere licencia, hash, diccionario, CMPE, población,
ponderación, varianza, quality y revisión adversarial.
