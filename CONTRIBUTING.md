# Guía para contribuir / Contribution guide

This guide applies to the current real-data research repository. Phase 4 interfaces and installed checks have recorded evidence; final v1.0.0 release acceptance remains a separate Phase 5 gate.

## Español

### Antes de cambiar el proyecto

Lee el alcance, el método y el contrato v2 vigentes. Los contratos v1 y la demo sintética se conservan como compatibilidad histórica; no describen el informe ENOE actual. Revisa el requisito y los criterios de aceptación de la tarea. Trabaja en una rama `codex/<tema>` y conserva los cambios de otras personas.

La unidad de revisión es un cambio concreto con su evidencia. Si cambia una interfaz, actualiza contrato, productor, consumidores y pruebas afectadas juntos. No cambies las definiciones de población, campo de estudio, ocupación, industria, fuente o periodo para resolver un problema de nombres. Una igualdad de etiquetas no autoriza una unión ni una comparación.

### Desarrollo y pruebas

Usa un entorno aislado con la versión de Python y dependencias fijadas en el proyecto. Las pruebas ordinarias usan fixtures locales desechables y no tienen acceso a producción. Ejecuta las pruebas afectadas después de una corrección; antes de integrar, ejecuta la verificación completa y los controles de documentación y prohibiciones indicados por la CI vigente. Registra el comando, la versión, el resultado y el commit realmente comprobados. No atribuyas a un cambio una ejecución anterior sobre código diferente.

Distingue las pruebas sintéticas de la aceptación real. La instalación limpia comprueba que el paquete contiene sus recursos y funciona fuera del checkout. La aceptación numérica real comprueba los ocho ZIP aprobados, el oráculo R y las referencias oficiales. La reproducción offline vuelve a calcular resultados con insumos fijados. La revisión visual inspecciona los archivos HTML/PDF y figuras realmente generados. Ninguna de estas pruebas sustituye a las demás.

Los fallos de refresco invalidan la publicación vigente; no restaures silenciosamente un éxito histórico. Prueba fallos con copias y fixtures desechables. No alteres los datos de origen aceptados ni los recibos históricos para que una prueba pase. Cambiar la referencia independiente o el golden exige la secuencia explícita de revisión y nueva evidencia; nunca regeneres valores esperados para ocultar una discrepancia.

### Fuentes, atribución y datos

Una propuesta de agente o una entrada en el catálogo candidato no activa una fuente o puente conceptual. Una edición nueva requiere revisar acceso, términos, población, diccionario, método y comparabilidad. Mantén nulos, supresiones y sus motivos en cada formato. No copies microdatos individuales al repositorio, issues, fixtures públicos o archivos de release. Publica únicamente agregados y material redistribuible que haya pasado el inventario y revisión correspondientes.

Conserva atribuciones de INEGI, avisos de transformación y licencias de dependencias y fuentes tipográficas. No incluyas secretos, rutas personales, herramientas locales, cachés o material propietario de otros proyectos. No introduzcas inferencia externa o APIs pagadas como requisito del cálculo.

### Proponer y revisar un cambio

Explica el problema y el comportamiento que cambia, con un ejemplo breve cuando ayude. Incluye las comprobaciones realizadas y sus límites; distingue implementación, revisión, CI, reproducción y publicación. Mantén commits acotados y actualiza la documentación afectada. Una decisión metodológica nueva debe quedar documentada con su justificación y evidencia.

Para reportar un problema, incluye versión/commit, comando, resultado esperado y observado y un fixture mínimo sin datos personales. Si la discrepancia es estadística, identifica universo, campo o concepto, geografía, periodo, fuente, medida y método. Una diferencia de cifras no establece por sí sola cuál definición es correcta.

## English

### Before changing the project

Read the current scope, methodology and v2 contract. The v1 contracts and synthetic demo remain historical compatibility material; they do not describe the current ENOE report. Review the task's requirement and acceptance criteria. Work on a `codex/<topic>` branch and preserve other contributors' changes.

A review concerns a concrete change and its evidence. When an interface changes, update its contract, producer, consumers and affected tests together. Do not change population, field of study, occupation, industry, source or period definitions to solve a naming problem. Matching labels do not authorize a join or comparison.

### Development and checks

Use an isolated environment with the project's declared Python version and pinned dependencies. Ordinary tests use disposable local fixtures and have no production access. Run affected tests after a fix; before integration, run the full verification, documentation and prohibition checks defined by current CI. Record the command, version, result and commit actually checked. A result from different source bytes does not establish that a change passes.

Keep synthetic checks separate from real acceptance. A clean installation checks that the package includes its resources and runs outside the source checkout. Real numerical acceptance checks the eight approved ZIPs, R oracle and official references. Offline reproduction recalculates results from fixed inputs. Visual review inspects actual generated HTML/PDF files and figures. These checks do not substitute for one another.

A failed refresh invalidates current publication; do not silently restore historical success. Test failure paths using disposable copies and fixtures. Never alter accepted source data or historical receipts to make a test pass. An independent reference or golden change requires its explicit review and fresh-evidence sequence; never regenerate expectations merely to hide a discrepancy.

### Sources, attribution and data

An agent proposal or candidate-catalog entry does not activate a source or conceptual bridge. A new edition requires access, terms, population, dictionary, method and comparability review. Preserve nulls, suppression and reasons in every format. Do not place individual microdata in the repository, issues, public fixtures or release assets. Publish only aggregates and redistributable material that passed the relevant inventory and review.

Keep INEGI attribution, transformation notices and dependency/font licenses. Do not include secrets, personal paths, local toolchains, caches or proprietary material from other projects. Do not make external inference or paid APIs a calculation prerequisite.

### Proposing and reviewing a change

Explain the problem and resulting behavior, with a short example where useful. Include actual checks and their limits; distinguish implementation, review, CI, reproduction and publication. Keep commits focused and update affected documentation. Document each new methodological decision with its reasoning and evidence.

For an issue, include version/commit, command, expected and observed results and a minimal fixture without personal data. For a statistical discrepancy, identify universe, field or concept, geography, period, source, measure and method. A numerical difference alone does not establish which definition is correct.

## Integration evidence

Grounded in AGENTS.md, `.planning/REQUIREMENTS.md`, accepted Phase 2/3 receipts and `docs/evidence/phase-04-publication-acceptance.json`. Installed commands are documented in the current CLI and operations guide. Scope of contribution approval is not an authorization for arbitrary GitHub publication by contributors.
