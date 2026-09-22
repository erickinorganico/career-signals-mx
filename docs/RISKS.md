# Registro de riesgos — Brújula Laboral MX

Escala: probabilidad e impacto se califican como baja, media o alta para ordenar
el trabajo; no son estimaciones estadísticas. El owner es responsable de vigilar
el trigger y mantener evidencia de la respuesta.

| ID | Riesgo | Prob. | Impacto | Owner funcional | Trigger observable | Mitigación y respuesta | Evidencia de cierre |
|---|---|---:|---:|---|---|---|---|
| RSK-001 | Términos permiten acceso pero no redistribución | Alta | Alta | Source owner | No existe licencia clara, los términos se contradicen o cambian | Mantener la fuente como referencia; no descargar/empaquetar; registrar URL y fecha; activar solo tras revisión explícita | Source record aprobado con términos y atribución |
| RSK-002 | ENOE se calcula sin diseño muestral completo | Media | Alta | Methodology owner | Falta factor, estrato, UPM, varianza o regla de precisión | Mantener observaciones reales fuera del release; implementar y revisar diseño antes de `MEASURED` | Nota metodológica, tests y revisión estadística |
| RSK-003 | Campo de estudio se presenta como ocupación o vacante | Media | Alta | Ontology owner | Join o narrativa cruza tipos sin bridge explícito | Dimensiones separadas, bridge con provenance y `REVIEW`, casos rojos de schema/eval | Tests conceptuales y reporte revisado |
| RSK-004 | Ausencia o bloqueo se convierte en cero | Media | Alta | Data-quality owner | `null`, `UNKNOWN` o `BLOCKED` aparece como 0 en tabla, delta o gráfica | Invariantes de schema/calidad; gaps visuales; test E2E de falso cero | Casos rojos pasan en datos, export y render |
| RSK-005 | Datos sintéticos se interpretan como medición de México | Alta | Alta | Publication owner | Falta warning en dataset, gráfica, reporte o brief | Prefijo `demo_`, `synthetic: true`, estado `REVIEW` y warning persistente en toda salida | Inspección de bundle, reportes y exports |
| RSK-006 | Se comparan series incompatibles | Media | Alta | Comparability owner | Cambia fuente, universo, geografía, métrica, unidad, base, método, concepto, synthetic flag o periodo | Comparación fail-closed con razones; sin delta automático | Matriz de casos incompatibles verde |
| RSK-007 | Un run histórico se muestra como actual tras un fallo | Media | Alta | Pipeline owner | Refresh falla y `current` aún apunta al éxito previo | Receipt por intento; reemplazar current/report por `BLOCKED`; conservar histórico separado | Test de refresh fallido y recibos |
| RSK-008 | Claim o recomendación carece de evidencia | Media | Alta | Insight owner | Evidence ref no resuelve o la interpretación excede observación | Schema, validador y evals; separar observación/interpretación/recomendación/unknowns | Paquetes válidos y revisión adversarial |
| RSK-009 | La precisión disponible se omite o exagera | Media | Alta | Methodology owner | CV/sample faltante se presenta como exactitud o significancia | Nota visible, estado `REVIEW`, sin lenguaje causal/significancia no calculada | Reporte y packet revisados |
| RSK-010 | El pipeline deja de ser reproducible/offline | Media | Media | Release owner | El replay usa red, CDN, fuente remota, estado local oculto o versión flotante | Dependencias fijadas, fuentes/fonts locales, build determinista y prueba limpia sin red | Receipt de clean-room replay |
| RSK-011 | Se publica secreto, path privado o material ajeno | Baja | Alta | Publication owner | Secret scan, diff o docs detectan credencial, ruta de usuario o contenido de otro workspace | Revisión de secretos/licencias y diff antes de push; solo artefactos autorizados | Checklist y scan guardados |
| RSK-012 | Un agente muta o publica fuera de su autoridad | Media | Alta | Agent owner | Output intenta activar fuente/bridge, editar canónico o publicar | Roles read-only, schemas de salida, tools acotadas y gate determinista humano/principal | Evals de autoridad y agent receipt |
| RSK-013 | Scope creep hacia app, UI o servicio | Alta | Media | Product owner | Aparecen servidor, endpoint, frontend o hosting como criterio del release | Aplicar SCOPE/PRD; registrar propuesta en backlog futuro independiente | Review de archivos y roadmap coherente |
| RSK-014 | Cobertura pequeña se vende como producto nacional completo | Media | Alta | Research owner | Narrativa omite los 3 campos/periodos o generaliza a todas las carreras | Etiquetar cobertura en cada salida y limitar claims al fixture/metodología | Revisión editorial con coverage visible |
| RSK-015 | Cambio de fuente o método produce drift silencioso | Media | Alta | Source + methodology owners | Hash, diccionario, versión o definición difiere del baseline | Raw content-addressed, versionado de adaptador y comparabilidad bloqueada hasta revisión | Diff metodológico y nuevo receipt |
| RSK-016 | Dependencia vulnerable o licencia incompatible | Baja | Alta | Release owner | Audit reporta CVE crítica o licencia incompatible | Versiones fijadas, dependencias mínimas, revisión antes de release y reemplazo/bloqueo | Reporte de dependencias y licencias |
| RSK-017 | El producto no ayuda a los perfiles supuestos | Media | Media | Product/research owner | Lectores no entienden conceptos o no pueden auditar una cifra | Validar HYP-001–004 con tareas observables; registrar feedback y corregir lenguaje/flujo | Evidencia de sesiones, no inferida de tests |
| RSK-018 | LATAM se agrega con equivalencias falsas | Media | Alta | Future country owner | Se combina un país sin auditoría de población, clasificación, moneda, precio, precisión y términos | México primero; contrato y gate por país; no agregación regional automática | Review por país y matriz de compatibilidad |

## Priorización inmediata

Antes del primer release se cierran o controlan RSK-003 a RSK-013 y RSK-016.
RSK-001 y RSK-002 permanecen como condiciones de M6 y no bloquean la demo
sintética. RSK-017 requiere evidencia de uso posterior: no puede cerrarse con
tests técnicos. RSK-018 permanece inactivo hasta proponer un país concreto.

## Protocolo de escalamiento

Ante un trigger, el owner registra el artefacto afectado, el requisito y el
estado `REVIEW` o `BLOCKED`. Solo se detiene el trabajo que depende del riesgo.
Los términos ambiguos, el acceso a un dataset y la activación de una fuente o
bridge requieren resolución explícita. Un fallo técnico dentro del entorno
local autorizado se corrige y vuelve a verificar sin crear un nuevo gate de
permiso.
