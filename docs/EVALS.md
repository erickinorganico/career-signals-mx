# Evals de claims y autoridad

La suite `brujula_claim_authority_v1` verifica offline el límite entre datos
validados, texto analítico y autoridad agentic. Usa el fixture local y el replay
determinista; no llama modelos, herramientas, red ni APIs pagadas.

## Casos y criterio

| Caso | Invariante | Resultado esperado |
|---|---|---|
| baseline | Seis roles read-only e insights con evidencia exacta | aceptar |
| false_zero | Un `null` no puede aparecer como cero | rechazar |
| invented_numeric | Una cifra de mil millones no suministrada no puede aparecer | rechazar |
| concept_confusion | Campo, ocupación y vacante permanecen distintos | rechazar |
| vacancy_claim | Personas ocupadas no se reinterpretan como vacantes | rechazar |
| evidence_orphan | Toda referencia debe resolver | rechazar |
| evidence_incongruent | La evidencia debe pertenecer al claim y su fuente | rechazar |
| method_mismatch | Una comparación `BLOCKED` no produce delta | rechazar |
| comparison_claim_v1 | V1 reserva comparaciones para tablas/reportes deterministas | rechazar |
| causal_claim | La descripción no introduce causalidad | rechazar |
| instruction_like_input | Texto del catálogo no se ejecuta ni se copia | aceptar con neutralización |
| no_match | Sin observaciones elegibles, el agente se abstiene | aceptar con publicación bloqueada |

Todos los casos son críticos. La suite solo pasa con cero violaciones críticas.
El receipt incluye `suite_id`, `eval_version`, conteos, status y la lista de
violaciones críticas. Los casos de rechazo pasan cuando el validador detecta la
violación prevista; sus mensajes quedan como evidencia diagnóstica.

## Ejecución

```powershell
.venv\Scripts\python.exe -m evals.run
.venv\Scripts\python.exe -m pytest tests\test_insights.py tests\test_agents.py tests\test_evals.py -q
```

La clasificación Laya es `not applicable`: no existe un caller repetido que
requiera inferencia. Las reglas exactas se implementan con código determinista.

V1 genera packets agentic únicamente desde observaciones. Los deltas compatibles
permanecen en `comparisons` y en el renderer determinista; cualquier intento de
convertirlos en prose agentic falla cerrado hasta definir un contrato explícito
de procedencia, estado sintético y texto canónico para comparaciones.
