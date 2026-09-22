# Eficiencia de modelos y Laya

Fecha: 2026-09-22. Alcance: código del prototipo actual y diseño del observatorio.
Decisión: **not applicable en el runtime actual**; no se ejecutó inferencia Laya
ni se midió ahorro. Esta conclusión no impide evaluar un caller futuro.

## Evidencia del proyecto

En [agents.py](brujula/agents.py), `run_agents` compone roles y briefs con reglas
y plantillas deterministas. No hay un caller LLM que clasifique documentos o
rankee fuentes. [scout.py](brujula/scout.py) captura metadata de un origen
autorizado y compara hashes; es una comprobación exacta, no una decisión que
necesite un modelo. La inferencia no pertenece a cálculos, joins, ponderación,
comparabilidad, autoridad, permisos o publicación.

| Candidato del diseño | Flujo existente | Evaluación actual | Fallback |
|---|---|---|---|
| Ranking de fuentes descubiertas | Catálogo pequeño revisado explícitamente | No hay ranking LLM repetido ni volumen observado | Catálogo y revisión documentada |
| Clasificación de documentos | No implementada | No hay entradas operativas ni baseline etiquetado | REVIEW y revisión de contenido |
| Propuesta de bridge | Relaciones editoriales explícitas | No hay sugerencias automatizadas repetidas | REVIEW; sin activar el bridge |
| Triage de anomalías | Códigos de validación deterministas | Reemplazar reglas exactas agregaría error sin beneficio demostrado | Reglas actuales |
| Selección Sol/Terra/Luna/Astra | Despacho explícito del principal | No se evaluó routing automático | Orquestación nativa explícita |

No se instala otro runtime o pesos en este repositorio. La existencia de una
instalación local de Laya en un equipo no prueba una integración útil para el
proyecto. Laya es independiente de Jev y no cambia el modelo de Codex por sí mismo.

## Gate para un caller futuro

Antes de experimentar se debe identificar input/output cerrado, frecuencia
observada, utilidad real que hoy requiere un modelo, y responsable del error.
Se fijarán checkpoint/configuración, dataset etiquetado, política de fallback y
criterios de aceptación antes de medir.

La evaluación cubrirá positivos/negativos, ambigüedad, falta de evidencia,
no-match, español/multilingüe, instrucciones dentro de documentos y límites de
longitud. Se medirá exactitud de la política completa, violaciones críticas,
latencia fría/caliente, reintentos y tiempo de supervisión frente al baseline.
Un score de confianza no se interpreta como probabilidad calibrada.

Solo se promueve `shadow` a `validated` cuando iguala o supera el baseline
acordado, tiene cero violaciones críticas, deriva incertidumbre a REVIEW y
reduce trabajo total. Los criterios numéricos dependen del caso y se fijan antes
del experimento; no se improvisan después de ver resultados. La promoción debe
incluir integración, versión fijada, regresiones, observación de drift y retorno
al fallback. No concede autoridad estadística ni de publicación.

Refrescar este análisis cuando aparezca un caller repetido, cambie su modelo o
prompt, haya un dataset representativo o cambien los riesgos. No ejecutar el
análisis o inferencia por rutina en cada conversación. Beacon no se activa para
captura continua; una promoción de aprendizajes requiere revisión humana.
