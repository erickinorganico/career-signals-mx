# GSD final gate map — Brújula Laboral MX v1.0.0

Fecha de auditoría: 2026-09-23. Alcance: mapa de procedimiento y estado; esta auditoría no ejecuta workflows, no cambia estado GSD, no publica y no crea una release.

## Estado verificado

El objetivo vigente es una publicación ENOE real de ocho trimestres. Actualización de estado del 2026-09-23: las fases 1–3 tienen verificación independiente y cierre canónico aceptados; Phase 3 valida su paquete persistido con 6,739 registros, 4,209 comparaciones, 38 afirmaciones y tres aperturas. Phase 4 tiene seis planes revisados, sin bloqueos de planificación y con una advertencia no bloqueante por el número de archivos de 04-06 después de incorporar CI. 04-01 está completado y 04-03 está en corrección de su revisión independiente. Sus controles de informe, exportaciones, aceptación numérica instalada y operación todavía no están cerrados. Phase 5 conserva contexto e investigación y requiere las interfaces aceptadas de Phase 4 antes de planear. La secuencia siguiente conserva todos los gates; el paso 1 ya está cumplido. No corresponde todavía auditar como completo ni publicar v1.0.0.

La receipt existente en docs/evidence/release-receipt.json documenta el release sintético v0.1.0; es regresión/historial y no satisface el alcance real de esta milestone. La investigación de Phase 5 confirma que los comandos, nombres de assets y digest final deben derivarse de la interfaz aceptada de Phase 4.

## Secuencia requerida

1. **Cerrar Phase 3 (hallazgos soportados).** Ejecutar los tres planes en orden, conservar summaries/receipts y hacer verificación de fase; ejecutar revisión de código y security gate cuando sus hooks estén activos.

   $gsd-execute-phase 3
   $gsd-verify-work 3
   $gsd-code-review 3
   $gsd-secure-phase 3

   Gate: los seis ANA deben tener evidencia de cobertura, comparabilidad, supresión y trazabilidad; la verificación canónica debe ser passed; cualquier gaps_found, human_needed, UAT pendiente o threats_open != 0 bloquea el avance. 03-SECURITY.md preparado no equivale a ese resultado.

2. **Planear y ejecutar Phase 4 (publicación offline).** Sólo después de aceptar Phase 3, derivar los comandos reales y el layout de bundle desde sus interfaces.

   $gsd-plan-phase 4
   $gsd-execute-phase 4
   $gsd-verify-work 4
   $gsd-code-review 4
   $gsd-secure-phase 4

   Gates obligatorios: HTML/Markdown/PDF offline en español, figuras y tablas semánticas, CSV/Parquet/DuckDB unidos por claves públicas, ausencia de celdas suprimidas en todos los formatos, replay real de los ocho snapshots con digest numérico canónico, manifest sellado antes de current, fallos que dejen receipt inmutable y current bloqueado, y resolución que vuelva a validar cada snapshot. El smoke PDF previo sólo es evidencia de factibilidad, no aceptación final.

3. **Planear y ejecutar Phase 5 (auditoría independiente y prueba de release).** Después de que Phase 4 tenga interfaces y artefactos aceptados, Phase 5 debe preparar primero la matriz de aceptación local, el target commit y el allowlist exacto. La prueba de release (draft/candidate, assets, readback remoto, publicación autorizada y readback público) ocurre dentro de la ejecución de Phase 5, antes de emitir su verificación final, porque REL-04 exige que el lector pueda recuperar la release. Un draft accesible sólo al propietario no satisface ese criterio.

   $gsd-plan-phase 5
   $gsd-execute-phase 5
   $gsd-verify-work 5
   $gsd-code-review 5
   $gsd-secure-phase 5
   $gsd-docs-update --verify-only

   --verify-only es apropiado para comprobar la cola documental; la generación o modificación de documentación sólo procede con los artefactos finales leídos de Phase 4. REL-01 exige documentación bilingüe de capacidad y límites; no se puede cerrar con narrativas sintéticas antiguas presentadas como capacidad real.

   El workflow gsd-ship tiene un orden diferente: bloquea si la verificación de la fase no es passed. Por eso no debe usarse como prerrequisito del primer readback de Phase 5. El plan de Phase 5 debe ejecutar el procedimiento gh release documentado abajo para el candidato y capturar el readback, cerrar los controles locales de publicación, publicar y comprobar acceso público; después se ejecuta el verificador canónico de Phase 5 y, sólo si hace falta enviar su rama/PR, gsd-ship 5. Esto es una adaptación mínima del orden, no un gate nuevo ni un override.

4. **Auditar UAT y la milestone completa.** Cuando las fases tengan sus reports y el readback remoto de Phase 5 esté registrado, ejecutar ambos análisis; el segundo requiere leer VERIFICATION.md de todas las fases, cruzar REQUIREMENTS/SUMMARY/VERIFICATION y revisar integración entre fases.

   $gsd-audit-uat
   $gsd-audit-milestone v1.0.0

   Gate: ningún requisito unsatisfied, fase sin verificación, UAT pending|blocked|human_needed, integración rota o Nyquist incompleto puede presentarse como milestone aprobada. Resolver y re-verificar evidencia afectada; no convertir un override en completion silenciosa.

5. **Cerrar y etiquetar la milestone (estado administrativo posterior al proof).** Sólo con el audit aprobado y todas las fases phase_complete=true y verification_status=passed:

   node "${GSD_CORE}/bin/gsd-tools.cjs" query audit-open --json
   $gsd-complete-milestone v1.0.0

   complete-milestone archiva ROADMAP/REQUIREMENTS/fases, actualiza MILESTONES.md/STATE.md y crea el tag si aún no existe; el workflow explícitamente salta la creación cuando el tag ya existe. Así, si el candidato de Phase 5 ya creó el tag v1.0.0 para que GitHub pueda servir el release y su readback, el cierre administrativo no duplica ni cambia ese target. Su pre-close audit-open debe quedar sin material abierto. Un cierre con overrides requiere una decisión explícita y un registro de gaps; no cumple el objetivo solicitado de release completo.

6. **Preparar y publicar el release autorizado dentro de Phase 5.** El workflow $gsd-ship es el gate de envío de una fase/PR, no sustituye el asset audit de GitHub. Antes de subir, congelar el target SHA y el allowlist derivado del manifest de Phase 4; inspeccionar wheel/archive, licenses, attribution, secrets, microdata y redistribución. Crear el candidato y hacer readback remoto antes de la verificación final de Phase 5; ejecutar $gsd-ship 5 después sólo cuando haya una fase shippeable. gsd-ship exige verification passed, árbol limpio, remoto/auth y security threats_open == 0.

   Procedimiento de release, con placeholders intencionales hasta aceptar Phase 4:

   gh release create v1.0.0 --repo erickinorganico/career-signals-mx --target <TARGET_SHA> --draft --title "Brújula Laboral MX v1.0.0" <ALLOWLISTED_ASSETS>
   gh release view v1.0.0 --repo erickinorganico/career-signals-mx --json tagName,targetCommitish,isDraft,assets,url
   gh release download v1.0.0 --repo erickinorganico/career-signals-mx --dir <ISOLATED_READBACK_DIR>

   Compare downloaded names, sizes and SHA-256 (incluido el digest remoto cuando esté disponible) con el inventario local; registrar target SHA, URLs, hashes, checks y limitaciones en una receipt final. La igualdad del readback acredita los assets candidatos, pero todavía no satisface el acceso público de REL-04. Una vez cerrados los controles independientes locales de instalación, contenido, seguridad, licencias, secreto/microdatos y paridad, publicar el draft autorizado y repetir la lectura pública de tag/URL/assets. Esa evidencia permite la verificación final de Phase 5; la auditoría global y el archivo administrativo del milestone se ejecutan después. No usar el cierre administrativo como prerrequisito de su propia prueba de acceso público. Cualquier mismatch, asset fuera del allowlist, licencia no resuelta, secreto/microdato o gate material abierto bloquea publicación.

## Recomendado por configuración GSD

.planning/config.json activa research, plan_check, verifier, nyquist_validation, auto_advance, code_review, security_enforcement (ASVS 1, bloquea en high), pattern_mapper, post_planning_gaps, human_verify_mode=end-of-phase y context_guard_mode=warn. Deben conservarse esas comprobaciones en cada fase:

- leer investigación/contexto antes de planear y pasar plan-check antes de ejecutar;
- ejecutar gsd-code-review después de cambios de fase y reparar/revisar hallazgos;
- ejecutar gsd-secure-phase antes de avanzar o shippear;
- conservar la verificación canónica producida por execute-phase y consultarla con query verification.status; ejecutar gsd-verify-work sólo cuando haya UAT/juicio humano persistente o una verificación stale/human_needed que deba resolverse; no tratarlo como sustituto del verificador independiente;
- ejecutar gsd-audit-uat como barrido transversal antes de la auditoría final;
- conservar *-VALIDATION.md y demostrar Nyquist; un PASS de tests no reemplaza replay real, revisión PDF/visual o readback remoto;
- actualizar documentación sólo desde interfaces aceptadas y volver a verificar enlaces, comandos y claims.

## Condicional, no inventar

- $gsd-ui-review sólo si una fase introduce una superficie UI que el workflow reconoce; para este proyecto no hay frontend/app. Phase 4 sí requiere su propia inspección determinista de HTML, print/mobile/200% y PDF porque PUB-01–05 lo exigen, aunque eso no sea una aplicación navegable.
- $gsd-pr-branch sólo si el flujo de colaboración cambia la estrategia de ramas; config.json dice branching_strategy: none.
- UAT manual sólo para items que la verificación marque human_needed o que sean realmente user-facing; no fabricar pasos humanos para invariantes que tests deterministas pueden probar.
- No instalar plugins, inferencia pagada, fuentes de datos nuevas ni credenciales. No usar los comandos actuales demo/report ni los nombres del release sintético como contrato de Phase 4/5.

## Referencias canónicas

- .planning/config.json, .planning/STATE.md, .planning/ROADMAP.md, .planning/REQUIREMENTS.md.
- .planning/phases/03-supported-labor-findings/03-CONTEXT.md, 03-RESEARCH.md, 03-VALIDATION.md, 03-UPSTREAM-PREFLIGHT.md.
- .planning/phases/04-offline-publication-and-reproducible-operation/04-CONTEXT.md, 04-RESEARCH.md, 04-EDITORIAL-SPEC.md, 04-PACKAGING-READBACK.md.
- .planning/phases/05-independent-audit-and-v1-0-0-release/05-CONTEXT.md, 05-RESEARCH.md.
- GSD skills: ${CODEX_SKILLS}/gsd-audit-milestone/SKILL.md, gsd-audit-uat/SKILL.md, gsd-complete-milestone/SKILL.md, gsd-docs-update/SKILL.md, gsd-secure-phase/SKILL.md, gsd-ship/SKILL.md, gsd-verify-work/SKILL.md.
- GSD workflows: ${GSD_CORE}/workflows/ files audit-milestone.md, audit-uat.md, complete-milestone.md, docs-update.md, secure-phase.md, ship.md, verify-phase.md, verify-work.md.
- Release mechanics: GitHub CLI gh release and official release asset API, as linked in 05-RESEARCH.md; the exact asset set remains a Phase 4 output.
- CLI readback: node ${GSD_CORE}/bin/gsd-tools.cjs query audit-open --json executed on 2026-09-23; result has_open_items=false and total=0. The command form is valid; it is a pre-close scan, not milestone verification.
