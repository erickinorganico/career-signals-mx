# Roadmap — Brújula Laboral MX

> **Roadmap histórico M0–M6 del piloto 0.1.0.** Fue sustituido para la entrega activa por el [roadmap GSD 1.0.0](../.planning/ROADMAP.md). ENOE real forma parte de la entrega comprometida; los estados históricos siguientes no acreditan su terminación.

El roadmap está ordenado por dependencias y gates, no por fechas prometidas.
México se valida antes de cualquier expansión LATAM. El estado de un hito solo
cambia con evidencia revisada; archivos presentes o trabajo parcial no bastan.

| Hito | Resultado | Requisitos | Entrada | Gate de salida | Estado |
|---|---|---|---|---|---|
| M0 — Planeación y publicación inicial | Repositorio público, mandato, fuentes, scope, PRD, contrato, plan, riesgos y trazabilidad coherentes | REQ-001 | Handoff corregido y auditoría de fuentes | Revisión principal confirma links, precedencia, ausencia de secretos/datos restringidos y consistencia de IDs | `PLANNING COMPLETE` |
| M1 — Contrato y slice sintético | Fixture ilustrativo conforme al contrato, con conceptos separados y nulos deliberados | REQ-002–REQ-005 | M0 aceptado | Schema y quality gate pasan casos verdes/rojos; 54 grains y 7 nulos explícitos | `VERIFIED` |
| M2 — Integridad, comparabilidad y trazabilidad | Quality gate, freshness, comparisons, receipts, DuckDB y exports locales | REQ-006–REQ-011 | M1 aceptado | Casos verdes y rojos pasan; fallo invalida current; warehouse y exports preservan semántica | `VERIFIED` |
| M3 — Reportes y briefs estáticos | Markdown/HTML, gráficas, tablas alternativas e insights auditables | REQ-012–REQ-014 | M2 aceptado | Render determinista; nulos son gaps; cada claim resuelve evidencia y muestra límites | `VERIFIED` |
| M4 — Agentes read-only y evals | Roles estructurados para fuentes, calidad, insights y visualización sin autoridad de mutación | REQ-015–REQ-016 | M2 aceptado; M3 disponible para eval E2E | 12/12 evals; propuestas sin autoridad de mutación | `VERIFIED` |
| M5 — Release reproducible | Instalación limpia, replay offline, tests/E2E, revisión adversarial y publicación verificada | REQ-017–REQ-018 | M1–M4 aceptados | Suite local, replay limpio, revisión, CI y publicación PASS | `RELEASED` |
| M6 — ENOE real para México | Primer snapshot real nacional con ponderación, diseño muestral y precisión validados | Requisitos nuevos después de M5 | M5 aceptado y source activation aprobada | Términos, CMPE, factor/estrato/UPM, varianza, atribución, hash y comparabilidad revisados | `CONDITIONAL` |

## M0 — Planeación y publicación inicial

Este hito fija autoridad, alcance, requisitos y trabajo ejecutable. Incluye la
creación del repositorio autorizado y la auditoría primaria de fuentes. El
integrador principal revisó el paquete documental y sus IDs canónicos, por lo
que M0 queda `PLANNING COMPLETE`. Esa marca no implica runtime, demo, release
analítico ni definición de terminado; M1–M4 están verificados localmente y M5
está publicado como v0.1.0, con verificación local y CI PASS.

## M1 — Contrato y slice sintético

El primer slice prueba semántica y control de calidad sin atribuir cifras a
México. Debe incluir tres campos, tres periodos, dos geografías y tres métricas,
con al menos un caso nulo útil para probar el falso cero. Los IDs editoriales
usan prefijo `demo_`; ninguna etiqueta humana se presenta como código CMPE.

## M2 — Integridad, comparabilidad y trazabilidad

El pipeline crea artefactos solo después de validar el dataset. Freshness usa el
periodo de negocio, no el timestamp de ejecución. Toda comparación declara sus
razones de compatibilidad o bloqueo. Cada intento conserva receipt; un fallo
deja `current` en `BLOCKED` y nunca revive un run histórico como actual.

## M3 — Reportes y briefs estáticos

El producto de lectura es un artefacto estático en español, acompañado por
documentación bilingüe del repositorio. Las gráficas incluyen tabla alternativa
y muestran fuente, periodo, geografía, población, unidad, base nominal,
precisión y condición sintética. Los briefs separan observación,
interpretación, recomendación y unknowns.

## M4 — Agentes read-only y evals

Los agentes reciben catálogos y bundles validados y devuelven propuestas
estructuradas. No descargan por defecto, no modifican datos canónicos, no
activan fuentes o bridges y no publican. El cálculo, los joins y el render
siguen siendo deterministas. Laya solo se estudia si existe un caller repetido
con baseline etiquetado, impacto de error, umbrales y fallback; `not applicable`
es un resultado aceptable con evidencia.

## M5 — Release reproducible

El release se verifica desde un entorno limpio y sin red después de instalar
dependencias. La revisión final cubre metodología, claims, secretos, licencias,
atribución y matriz REQ→evidencia. La publicación autorizada es únicamente en
`erickinorganico/career-signals-mx`.

## M6 — México con ENOE real

La extensión real comienza a nivel nacional para reducir riesgo estadístico.
No se fija una fecha ni se declara aprobada por el solo hecho de que ENOE sea
pública. Requiere activar un paquete concreto y demostrar clasificación CMPE,
universos, factor de expansión, estrato, UPM, varianza, precisión y provenance.
Informalidad, geografía subnacional y salarios reales son extensiones separadas.

## Expansiones posteriores

1. Más periodos mexicanos que pasen el gate de comparabilidad.
2. Dominios subnacionales representativos y documentados.
3. Informalidad y transformación a precios reales con contratos propios.
4. Bridges editoriales campo↔ocupación evaluados y siempre en `REVIEW`.
5. Evaluación de una interfaz local como proyecto independiente, fuera del
   alcance de este roadmap inicial.
6. LATAM país por país, después de M6, con auditoría local de fuente, población,
   clasificación, moneda, precios, precisión, términos y comparabilidad. No se
   forma una serie regional por compartir etiquetas.

## Reglas de cambio

Un cambio de alcance crea o actualiza requisitos antes de iniciar trabajo. Una
fuente nueva no pasa de candidata a activa por propuesta de agente. Un hito
condicional no se promueve hasta resolver su gate; el resto del trabajo
autorizado continúa si no depende de esa decisión.

El cierre de M5 corresponde a [v0.1.0](RELEASE.md): 89 tests y 12 evals PASS,
CI Windows/Linux, revisión independiente, wheel aislado y assets publicados con
hashes remotos verificados. M6 permanece condicional y fuera de este release.
