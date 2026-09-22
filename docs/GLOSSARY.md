# Glosario canónico

Los términos de este archivo son contratos semánticos. Una etiqueta parecida no
autoriza joins ni comparaciones.

| Término | Definición en Brújula Laboral MX | No significa |
|---|---|---|
| Campo de estudio (`field_of_study`) | Clasificación del programa/formación estudiada | ocupación ejercida, industria o vacante |
| Ocupación (`occupation`) | Tipo de trabajo o tareas desempeñadas según una clasificación declarada | carrera cursada o puesto disponible |
| Industria (`industry`) | Actividad económica de la unidad/establecimiento donde se trabaja | ocupación individual |
| Vacante | Oportunidad laboral publicada o registrada | persona ocupada; no existe como dimensión numérica del v1 |
| Geografía | Dominio territorial de una observación y de su representatividad | lugar universalmente comparable |
| Periodo de negocio | Intervalo al que se refiere la medición | fecha de descarga o ejecución |
| Fuente | Productor/dataset que origina una observación | página que republica o visualiza el dato |
| Catálogo de fuentes | Registro de candidatos y su decisión de uso | lista de fuentes activas ni permiso numérico |
| Fuente candidata | Fuente investigada pero no activada | fuente aprobada para ingesta |
| Fuente activa | Fuente con términos, método, contrato y gate aprobados para un snapshot concreto | permiso permanente para versiones futuras |
| Bridge | Relación explícita entre conceptos distintos, con método, evidencia y confianza | equivalencia oficial o permiso de agregación |
| Grain | Conjunto mínimo de claves que identifica una observación | número de filas del archivo |
| Población/universo | Personas o unidades elegibles según filtros y definiciones | toda la población mexicana por defecto |
| Factor de expansión | Peso muestral que representa cuántas unidades poblacionales corresponde a un registro | multiplicador arbitrario |
| UPM | Unidad primaria de muestreo usada en el diseño complejo | ID de persona |
| Estrato | Grupo del diseño muestral usado para selección/varianza | agrupación analítica opcional |
| Coeficiente de variación (CV) | Error estándar relativo a la estimación | porcentaje de cambio temporal |
| Precisión | Incertidumbre estadística documentada para una estimación | exactitud absoluta garantizada |
| Nominal | Expresado en pesos del periodo observado | poder adquisitivo constante |
| Real/deflactado | Ajustado con deflactor y periodo base explícitos | sinónimo de dato verdadero |
| Evidence ref | ID interno que resuelve a evidencia registrada | URL libre o cita no comprobable |
| Receipt | Registro de un intento con hash, tiempos, versión, estado y error | prueba de que el dato es correcto por sí solo |
| Raw inmutable | Bytes de entrada preservados por hash | dataset limpio/canónico |
| Bundle | Paquete estructurado de dataset, quality, comparaciones, insights, receipt y catálogo | aplicación o endpoint |
| Current | Puntero al intento vigente, exitoso o fallido | último éxito disponible |
| Run histórico | Artefactos inmutables de un intento anterior | fallback vigente |
| Sintético | Valor inventado deliberadamente para probar el sistema | estimación, simulación predictiva o dato anonimizado |
| `MEASURED` | Observación real con evidencia y gates de método/precisión satisfechos | cualquier número presente |
| `REVIEW` | Dato/propuesta visible que requiere interpretación o revisión; estado obligatorio de valores sintéticos | error ni aprobación final |
| `UNKNOWN` | El valor no está disponible o no puede determinarse; `value` es `null` | cero |
| `BLOCKED` | El gate impide publicar o comparar | dato negativo |
| Freshness | Edad respecto al final del periodo de negocio | tiempo desde que corrió el script |
| Comparabilidad | Compatibilidad de concepto, población, fuente, método, unidad, precio, geo y tiempo | etiquetas iguales |
| Insight packet | Observación, interpretación, recomendación, unknowns y evidencia separadas | texto libre o claim causal |
| Agente read-only | Función que produce una propuesta/diagnóstico estructurado sin modificar datos canónicos | actor autónomo con autoridad de publicación |
| Publisher | Gate lógico que autoriza generar el artefacto analítico | cuenta que hace push o publica en GitHub |
| Source Scout | Monitor opt-in de metadata de orígenes permitidos | scraper general ni activador de datasets |
| Laya | Candidato local para clasificación/ranking repetido sujeto a evaluación | router de modelos, autoridad o motor estadístico |

## Convenciones de IDs

- IDs editoriales/sintéticos comienzan con `demo_`.
- IDs de periodos y geografías son estables dentro de la versión del contrato.
- Un label puede cambiar para legibilidad; el ID no cambia silenciosamente.
- Una clave oficial solo se usa cuando la clasificación y versión están citadas.
- `source_id` del dataset activo y `source_id` del catálogo candidato no implican
  la misma autorización.
