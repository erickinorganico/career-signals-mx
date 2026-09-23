# Contribuir

Empieza por [el mandato](docs/PROJECT-CHARTER.md), [scope](docs/SCOPE.md),
[plan](docs/PLAN.md) y [estado actual](docs/STATUS.md). Escoge una tarea con
dependencias resueltas; lee sus criterios de aceptación antes de cambiar código.

## Proceso

1. Trabaja en una rama `codex/<tema>` o una rama descriptiva acordada.
2. Mantén un cambio acotado y preserva el trabajo concurrente. Si cambia una
   interfaz, actualiza contrato y consumidores juntos; no renombres conceptos
   estadísticos por conveniencia técnica.
3. Ejecuta los checks afectados y `python scripts/check_docs.py`. La demo y el
   replay son offline; separa la evidencia de tests locales de la instalación
   limpia, el E2E y la publicación, que requieren revisión del integrador.
4. Actualiza STATUS con evidencia y el plan con el estado de la tarea. Los
   cambios de decisión merecen un ADR nuevo o una referencia que sustituya el
   anterior.
5. Revisa el diff, secretos, atribución y licencias. Conserva commits pequeños
   que expliquen el cambio y su validación.

Los nombres de archivos y rutas en ejemplos son relativos al repositorio.
No incluyas directorios personales, tokens, dumps privados, cuentas de prueba
reales ni datos de otras organizaciones. `.venv`, `.cache` y `artifacts` no se
publican; los ejemplos compartidos deberán ser sintéticos o redistribuibles y
revisarse explícitamente.

## Pruebas

Las pruebas de esta etapa usan fixtures desechables y no tienen acceso a
producción. Ejecútalas y corrige regresiones del cambio sin pedir aprobación
por cada iteración. Separa tests offline de lecturas optativas de fuentes.
Las verificaciones necesarias se definen en [VALIDATION-PLAN](docs/VALIDATION-PLAN.md).

Una propuesta de agente no activa fuentes ni bridges. `official_snapshot`
permanece bloqueado hasta M6. No incorporamos APIs de
inferencia pagadas o servicios obligatorios. Laya necesita un caso real y una
evaluación previa de la política completa; véase [PROJECT-EFFICIENCY](PROJECT-EFFICIENCY.md).

## Reportar un problema

Incluye requisito/tarea relacionada, comando, versión, resultado esperado,
resultado observado y un fixture mínimo sin datos personales. No publiques
secretos ni microdatos restringidos en un issue. Para problemas estadísticos,
explicita universo, grain, periodo, fuente y método; una discrepancia de cifras
por sí sola no demuestra cuál definición es correcta.
