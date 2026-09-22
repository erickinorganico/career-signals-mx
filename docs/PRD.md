# PRD — Brújula Laboral MX

Estado: **baseline de planeación aceptado en M0; release analítico
incompleto**. No se realizaron entrevistas de usuarios para este baseline; los
perfiles, preguntas e hipótesis son supuestos de producto que deberán validarse
con uso real.

## Problema

Las fuentes laborales mexicanas difieren en población, conceptos, periodo,
metodología, unidad y condiciones de reutilización. Un lector puede confundir
personas ocupadas con vacantes, campo de estudio con ocupación, o ausencia con
cero. Brújula Laboral MX debe hacer visibles esas diferencias y permitir una
reproducción local antes de redactar una conclusión.

## Usuarios previstos y decisiones

| Perfil supuesto | Necesidad | Decisión que el producto apoya | Límite explícito |
|---|---|---|---|
| Estudiante explorando un campo | Entender qué mide una señal y cómo cambia | Formular mejores preguntas para investigar opciones | No recomienda una carrera ni predice un resultado individual |
| Persona considerando un cambio | Comparar métricas compatibles y límites | Identificar señales que merecen investigación adicional | No equipara salario observado con oferta futura |
| Analista o periodista | Reproducir cifras, método y evidencia | Auditar una gráfica o brief antes de citarlo | No permite claims sin receipt y evidence refs |
| Contribuyente técnico/metodológico | Extender fuentes y periodos con control | Evaluar si una fuente puede activarse | Acceso público no equivale a permiso o comparabilidad |

## Preguntas de investigación del primer release

1. ¿Puede el repositorio representar tres campos sin confundirlos con
   ocupaciones o vacantes?
2. ¿Puede mostrar ingreso mensual medio, personas ocupadas y participación de
   mujeres con unidad, población, base de precios, periodo y precisión visibles?
3. ¿Bloquea una comparación cuando cambia cualquiera de sus dimensiones de
   comparabilidad?
4. ¿Conserva `null`, `UNKNOWN` y `BLOCKED` sin convertirlos en cero?
5. ¿Puede un lector reconstruir una salida desde el hash de entrada, el contrato
   y el recibo de ejecución?
6. ¿Distingue el reporte entre observación, interpretación, recomendación y
   unknowns?

## Hipótesis a validar

- HYP-001: mostrar universo, unidad, condición sintética y precisión junto a la
  cifra reduce interpretaciones incorrectas durante una revisión cualitativa.
- HYP-002: un gate automático de comparabilidad evita deltas que un análisis
  manual podría aceptar por compartir etiqueta.
- HYP-003: un brief con evidence refs y unknowns permite auditar cada claim sin
  leer primero todo el pipeline.
- HYP-004: un flujo local de un comando para verificar y otro para generar el
  bundle reduce fricción de reproducción para contribuyentes.

Estas hipótesis no se consideran confirmadas por tener una demo. Su validación
de adopción requiere sesiones o feedback reales que todavía no existen.

## Objetivos

### Objetivos técnicos medibles del release inicial

- 100% de las observaciones cumple el schema y resuelve IDs de fuente,
  dimensión, métrica y evidencia.
- 100% de los valores sintéticos no nulos usa `REVIEW`, y 100% de las salidas
  muestra una advertencia sintética persistente.
- Los casos incompatibles definidos en tests producen `comparable: false` y no
  emiten delta numérico.
- Todo `UNKNOWN` tiene `value: null`; ningún `BLOCKED` se renderiza como dato
  válido.
- Un entorno limpio reproduce bundle, DuckDB, exportaciones y reportes sin red
  ni credenciales una vez instaladas las dependencias.
- Cada publicación actual corresponde a un receipt exitoso; un refresh fallido
  reemplaza el estado actual por `BLOCKED` sin reutilizar un éxito histórico.

### Resultados de adopción e impacto por validar

- Al menos un lector de cada perfil objetivo puede explicar correctamente la
  diferencia entre campo, ocupación y vacante usando el reporte.
- Un revisor puede localizar fuente, periodo, población, unidad y limitación de
  una afirmación sin asistencia del autor.
- Un contribuyente externo puede reproducir el artefacto siguiendo solo el
  README y reportar cualquier divergencia.

Estos resultados son criterios de investigación futura, no condiciones que se
puedan declarar cumplidas sin evidencia de usuarios.

## Requisitos funcionales

| ID | Requisito | Aceptación verificable | Hito |
|---|---|---|---|
| REQ-001 | Mantener un catálogo de fuentes separado del dataset | Cada candidato registra autoridad, URL, términos, acceso, población, cobertura, periodicidad, método, fecha y decisión | M0 |
| REQ-002 | Versionar contratos de dataset e insights | JSON Schema rechaza campos inesperados, enums inválidos y estructura incompleta; el quality gate rechaza referencias semánticas rotas entre IDs | M1 |
| REQ-003 | Proveer el slice sintético acordado | Los 3 campos, 3 periodos, 2 geografías y 3 métricas aparecen o tienen estado/nulo explícito | M1 |
| REQ-004 | Mantener conceptos separados | Campos, ocupaciones, industrias y bridges viven en dimensiones distintas; todo bridge queda en `REVIEW` | M1 |
| REQ-005 | Preservar nulos y estados | Ausencia produce `value: null` con `UNKNOWN` o `BLOCKED`; nunca cero implícito | M1 |
| REQ-006 | Validar integridad y rangos | El quality gate detecta duplicados, refs inválidas, unidades/bases incompatibles y porcentajes fuera de rango | M2 |
| REQ-007 | Evaluar freshness por periodo de negocio | El resultado reporta latest period end, age, threshold y estado; el fixture se etiqueta ilustrativo | M2 |
| REQ-008 | Bloquear comparaciones incompatibles | Fuente, universo, geografía, métrica, unidad, método, base, concepto, synthetic flag y orden temporal participan en el gate | M2 |
| REQ-009 | Conservar raw y receipts trazables | Cada intento registra SHA-256, parámetros, timestamps, versión, status y error; fallos invalidan current | M2 |
| REQ-010 | Materializar un warehouse local | DuckDB separa dimensiones, observaciones y bridges sin agregar numéricamente a través de bridges | M2 |
| REQ-011 | Exportar solo datasets permitidos | CSV/Parquet preservan source, period, unit, status y synthetic; exportación se bloquea si el bundle no es publicable | M2 |
| REQ-012 | Generar reportes estáticos accesibles | Markdown/HTML y SVG/PNG muestran fuente, periodo, geografía, unidad, población, precisión y advertencia sintética, con tabla alternativa | M3 |
| REQ-013 | Representar nulos e incompatibilidad visualmente | Nulos son gaps; no se unen series incompatibles ni se grafica `BLOCKED` como valor | M3 |
| REQ-014 | Emitir insight packets auditables | Cada packet separa observación, interpretación, recomendación, unknowns y evidence refs; no permite claims huérfanos | M3 |
| REQ-015 | Ejecutar agentes de solo lectura | Los roles producen propuestas estructuradas; no activan fuentes/bridges, no escriben datos canónicos ni publican | M4 |
| REQ-016 | Evaluar agentes y casos rojos | Evals cubren falsa ausencia cero, confusión conceptual, evidencia faltante, causalidad y serie incompatible | M4 |
| REQ-017 | Reproducir y verificar localmente | Comandos documentados instalan/verifican y ejecutan el flujo offline; tests unitarios, integración y E2E pasan | M5 |
| REQ-018 | Liberar con evidencia de revisión | Secret/license scan, revisión metodológica adversarial, matriz de requisitos y receipt final quedan registrados antes de etiquetar o liberar el release analítico | M5 |

## Requisitos no funcionales

- Python 3.12+, DuckDB, jsonschema y Matplotlib con versiones fijadas; no APIs
  pagadas ni inferencia requerida.
- Salidas deterministas para entradas y versión iguales; timestamps y run IDs se
  aíslan de la geometría y los cálculos.
- Operación local-first y offline después de instalar dependencias; sin CDN,
  fuentes remotas ni telemetría.
- Datos raw content-addressed; runs históricos inmutables y estado `current`
  explícito.
- Español en el reporte analítico; documentación de repositorio utilizable en
  español e inglés.
- Solo datos sintéticos o datos públicos redistribuibles tras revisión de
  términos; ningún secreto, credencial o material de otros workspaces.

## Criterios de aceptación del release

El release inicial solo puede etiquetarse como reproducible cuando REQ-001 a
REQ-018 tienen evidencia verificable. Los archivos parciales actuales no
constituyen una ruta verde. Una extensión ENOE o LATAM no es necesaria para
cerrar este release y no puede usarse para compensar fallos del slice sintético.

## Decisiones abiertas

- La forma final de validar HYP-001 a HYP-004 con usuarios reales.
- Si dbt Core aporta suficiente lineage para justificar su costo operativo
  después del MVP.
- Umbrales de precisión y dominios subnacionales para ENOE, sujetos a revisión
  estadística.
- Cualquier caller de Laya; se evalúa solo si aparece una decisión repetida,
  cerrada y observable con baseline y fallback.
