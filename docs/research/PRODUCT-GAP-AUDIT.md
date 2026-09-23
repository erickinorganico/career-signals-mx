# Auditoría de brechas: del MVP sintético a un informe editorial final

Fecha: 2026-09-22  
Estado: propuesta de contrato; no autoriza activar fuentes ni publicar cifras reales.

## Dictamen

El repositorio ya demuestra un **motor de evidencia** sólido para un MVP
sintético: contratos, estados de evidencia, comparabilidad, receipts, hashes,
exportaciones locales y un reporte HTML/Markdown offline. El ejemplo publicado
es útil para auditar el flujo, pero todavía no es una pieza de investigación que
un estudiante, periodista o analista pueda leer como producto terminado.

La brecha principal no es una aplicación. Es convertir un volcado técnico de
54 filas y cuatro gráficas en un **informe editorial estático, verificable y
legible**, con una narrativa que empiece por la pregunta del lector y termine
en la evidencia que permite auditarla. Ninguna mejora visual compensa la falta
de datos reales, precisión muestral o comparabilidad; esas condiciones deben
seguir bloqueando la publicación numérica real.

## Evidencia revisada

| Activo | Qué ya aporta | Límite para el lector final |
|---|---|---|
| `README.md`, `docs/SCOPE.md`, `docs/PRD.md` | Propósito, límites semánticos y perfiles de lector explícitos. | La ruta de lectura está orientada al repositorio y al CLI, no a una pregunta de investigación. |
| `docs/METHODOLOGY.md`, `docs/SOURCES.md` | Define conceptos, universo, comparabilidad y la ruta condicionada para ENOE. | El método está separado del informe; un lector de una figura no llega a la definición, versión y evidencia de esa cifra en un paso. |
| `brujula/report.py` y `examples/synthetic/report.html` | HTML sin red/scripts, Markdown, SVG/PNG deterministas, tablas alternativas, avisos sintéticos y gaps. | La página es una secuencia larga de tablas con escasa jerarquía editorial; cada gráfico tiene metadatos densos dentro de la imagen y no hay resumen de hallazgos ni perfiles por campo. |
| `examples/synthetic/charts/*` | Barras de último periodo, tendencia de ingreso, etiquetas de ausencia y metadatos exportados. | Las figuras no conforman una historia de comparación: no hay tarjetas de contexto, panel por campo, selección explícita de comparaciones ni incertidumbre estadística. |
| `docs/CONTRACT.md`, receipts, manifest y bundle | Provenance reproducible y fail-closed cuando un run falla. | La evidencia está disponible para un revisor técnico, pero no se presenta como una ficha de trazabilidad legible por sección/figura. |

## Brechas priorizadas

| Prioridad | Brecha | Consecuencia | Condición de cierre |
|---:|---|---|---|
| P0 | No existe un dataset real activado con licencia, snapshot, población cerrada, ponderación y varianza. | El informe actual solo puede ser una demostración sintética, nunca una lectura del mercado laboral mexicano. | Un paquete de fuente concreto pasa los gates M6: URL/términos, hash, diccionario/códigos, universo, pesos, estrato/UPM, estimador, precisión y revisión metodológica. |
| P0 | Las cifras y evidencia no se organizan en una unidad editorial de lectura: pregunta → resultado → límite → fuente. | El lector debe descifrar una tabla de observaciones antes de entender por qué importa. | Cada hallazgo tiene un identificador, filas/evidence refs, universo, periodo, método, estado y limitación visibles junto a él. |
| P0 | La incertidumbre no puede mostrarse: el fixture solo tiene notas sintéticas y CV nulo. | Un gráfico limpio podría sugerir una precisión que no existe. | Para datos reales, publicar intervalo/error estándar o CV y su método; si falta, mostrar `REVIEW`/sin estimación gráfica según la política. |
| P1 | Las comparaciones no se exponen como decisiones editoriales. | El lector no sabe qué cambios son comparables, cuáles son brechas y por qué. | Un registro de comparación alimenta el texto y las figuras; solo pares `comparable=true` generan deltas descriptivos. |
| P1 | El HTML no ofrece una jerarquía visual de informe: portada, resumen, perfiles y apéndice. | La información es correcta pero difícil de escanear, imprimir o citar. | Un único HTML estático con navegación interna, diseño tipográfico, figuras con caption y apéndices trazables, sin servidor ni JavaScript. |
| P1 | La accesibilidad es funcional pero mínima. | Las tablas carecen de `caption`, `scope`, resumen de figura y una estructura de lectura deliberada. | HTML semántico, tabla alternativa por figura, caption/long description, contraste probado y orden de encabezados. |
| P2 | No hay formato de impresión/PDF definido. | Un archivo HTML offline no garantiza una entrega cómoda en una reunión o archivo institucional. | Hoja de impresión y PDF opcional generado desde el mismo HTML; el HTML sigue siendo la autoridad y el PDF debe llevar hash/versión. |
| P2 | No hay contrato para perfiles por campo ni para una lectura de desigualdad. | La investigación no responde aún a la pregunta natural: “¿qué se observa para este campo, en este lugar y periodo?” | Perfiles reproducibles por campo y módulos de distribución/desigualdad solo cuando el universo y el estimador los sostengan. |

## Contrato propuesto: publicación estática final

### Artefactos y autoridad

Una publicación es un directorio inmutable bajo un `run_id` validado:

```text
publication/
  index.html                 # autoridad de lectura, autosuficiente y offline
  report.md                  # equivalente semántico y citable
  print.pdf                  # opcional, derivado de index.html
  figures/*.svg
  figures/*.png
  tables/*.csv               # solo si licencia y gate lo permiten
  publication.json           # manifiesto editorial, hashes y rutas
```

`index.html` integra CSS local embebido o content-addressed, no CDN, fuentes
remotas, scripts, tracking ni llamadas de red. “Autosuficiente” significa que
se puede abrir desde disco con sus figuras locales; no significa duplicar en el
HTML datos que el contrato debe mantener como tablas/figuras auditables. El
Markdown conserva el mismo orden de secciones, identificadores de hallazgo,
figuras y tablas. Si se distribuye PDF, su hash y el del HTML fuente se
registran en `publication.json`; PDF no sustituye a HTML/Markdown como versión
auditable.

La publicación solo se materializa cuando `current.json`, manifest y receipt
son coherentes y el bundle es publicable. `BLOCKED` produce un diagnóstico
editorial sin cifras, perfiles, tablas numéricas ni figuras heredadas.

### Estructura de lectura

1. **Portada y estado.** Título, periodo cubierto, geografía, versión, fecha de
   ejecución separada de la fecha de datos, estado (`MEASURED`, `REVIEW`, etc.)
   y banner persistente de sintético cuando aplique.
2. **Qué puede y no puede responder.** Tres o cuatro frases: población,
   concepto, unidad, exclusiones y prohibición de causalidad, ranking o consejo
   individual.
3. **Resumen de señales.** Máximo tres hallazgos descriptivos con links a sus
   fichas. Una señal no aparece si carece de evidencia, precisión o comparación
   permitida.
4. **Cómo leer la evidencia.** Leyenda de estados, brechas, comparabilidad y
   definición corta de campo de estudio frente a ocupación e industria.
5. **Perfiles por campo de estudio.** Una sección repetible por campo: qué mide,
   última observación permitida, tendencia compatible, cobertura geográfica,
   ausencia/precisión y enlaces a fuente/método. No mezcla un campo con una
   ocupación mediante un bridge editorial.
6. **Comparaciones y desigualdad, cuando proceda.** Comparaciones de serie solo
   para pares declarados compatibles. Distribución, brecha o desigualdad solo
   se habilitan si se publica la definición, el denominador, el estimador y la
   precisión; de otro modo se muestra “no evaluado”, no un proxy inventado.
7. **Método y límites.** Universo, filtros, periodos, unidad/base de precios,
   diseño, estimador, tratamiento de nulos, comparabilidad y precisión. Incluir
   un enlace interno desde cada figura a esta definición.
8. **Fuentes y trazabilidad.** Por fuente: autoridad, URL, licencia/términos,
   fecha de consulta, snapshot/hash y versión metodológica. Por publicación:
   run ID, receipt, manifest, hash del input y commit.
9. **Apéndice de datos.** Tablas completas por figura, registro de
   comparaciones bloqueadas y diccionario de indicadores. Es la evidencia de
   lectura, no una descarga implícita de microdatos.

### Sistema de visualización

| Pregunta del lector | Figura estática | Reglas de publicación |
|---|---|---|
| ¿Cuál es la última observación disponible por campo? | Dot plot o barras horizontales por métrica, con una marca `Sin dato` sin barra. | Una figura por métrica/unidad; nunca eje que mezcle personas, pesos y porcentajes. |
| ¿Cómo cambia una señal en el tiempo? | Línea o puntos por campo y geografía. | Punto para cada valor permitido; segmento solo para una pareja `comparable=true`; `null`, `UNKNOWN`, `BLOCKED` e incompatibilidad rompen la serie. |
| ¿Es diferente por geografía? | Pequeños múltiplos por geografía, con el mismo indicador y periodo. | No convertir una geografía no representativa en ranking; declarar dominio y precisión. |
| ¿Qué tan incierta es la estimación? | Punto con IC 95% o barras de error; tabla con SE/CV/n efectivo. | Obligatorio para datos reales cuando aplique; si no existe, no se presenta una comparación numérica como precisa. |
| ¿Hay una brecha descriptiva? | Diferencia absoluta o relativa con intervalo, solo cuando el contrato de comparación lo permite. | Etiqueta “descriptiva”; no atribuir causa y no calcular porcentaje si la base es cero. |
| ¿Cómo se distribuye o concentra una medida? | Percentiles, mediana o curva de distribución ponderada. | Fuera de alcance hasta que existan microdatos permitidos, definición y varianza; no derivar desigualdad de tres medias. |

Cada figura tiene: título que responde una pregunta, subtítulo de universo y
periodo, leyenda que no depende solo de color, marca sintética/estado, caption
con interpretación estrictamente descriptiva, link a método y tabla equivalente
con fuente, periodo, geografía, unidad, población, base de precios, precisión,
estado y evidence refs.

### Accesibilidad y presentación

- Usar `header`, `main`, `nav`, `section`, `figure`, `figcaption`, encabezados
  ordenados y enlaces internos visibles. Los cuadros de datos usan `caption`,
  `thead`, `th scope` y `td`; para tablas complejas, asociaciones explícitas.
  W3C recomienda tablas de datos como alternativa a visualizaciones y una
  equivalencia textual completa para gráficos complejos.
  ([W3C Tables Tutorial](https://www.w3.org/WAI/tutorials/tables/),
  [W3C Images Tutorial](https://www.w3.org/WAI/tutorials/images/)).
- Garantizar contraste, tamaño de tipografía imprimible, no codificar estado
  solo por color, y escribir alt breve más una tabla/long description. SVG es
  preferible para inspección; PNG permite inserción en documentos.
- El diseño debe funcionar a 200% de zoom y en impresión. La portada y cada
  sección deben conservar número de página/título en PDF, pero la versión PDF
  no añade interactividad ni datos distintos.
- Separar el detalle técnico en `details` HTML sin ocultar las limitaciones
  críticas; Markdown deja el detalle expandido para lectores sin navegador.

### Datos reales y método: gates no negociables

La primera publicación real nacional basada en ENOE necesita el paquete exacto
de datos y su documentación, no solo una URL de programa. El diseño muestral
oficial de ENOE documenta factores de expansión, estratos y UPM; por ello el
contrato de análisis debe preservar esas variables y usar un estimador de
varianza compatible, no tratarlas como una muestra simple.
([INEGI, diseño muestral ENOE](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf)).

Antes de mostrar una cifra real, la publicación debe comprobar:

- licencia/términos y atribución verificadas para el artefacto concreto;
- snapshot raw, SHA-256, versión de cuestionario/diccionario y parámetros de
  transformación;
- población, elegibilidad, clasificación de campo y denominador de cada métrica;
- pesos, estrato, UPM, método de estimación, SE/IC o CV y regla explícita de
  supresión;
- periodo, geografía/dominio de inferencia, unidad y base de precios;
- evidence refs que resuelven a la fuente y a las filas/transformaciones;
- comparación bloqueada ante cambios de definición, fuente, cobertura, método,
  precios o clasificación.

## Qué se recicla y qué se reemplaza

| Se conserva | Se reemplaza o amplía |
|---|---|
| Dataset schema, estados, quality gate, comparability, raw hashes, receipt, manifest y current fail-closed. | El layout de “todas las observaciones primero” por una narrativa de secciones y perfiles; la tabla completa queda en apéndice. |
| HTML/Markdown offline, escape de payload, ausencia de scripts/red, SVG/PNG deterministas y tablas alternativas. | HTML de una sola línea y sin estilos por una plantilla editorial semántica, imprimible y con navegación interna. |
| Barras de último periodo, puntos de tendencia, huecos y etiquetas `Sin dato`. | Una familia de figuras orientada a preguntas, con pequeños múltiplos, incertidumbre y comparaciones solo declaradas. |
| Warning sintético y separación campo/ocupación. | Un banner contextual por sección/figura y un glosario breve que explique el alcance sin repetir una advertencia técnica en cada celda. |
| Insight packets separados en observación, interpretación, recomendación y unknowns. | Una capa editorial que cite cada packet/claim y evite recomendaciones si la evidencia solo permite describir. |

## Criterios de aceptación del informe final

1. Un lector identifica en menos de una pantalla qué población, periodo,
   geografía, estado de evidencia y límites tiene el informe.
2. Cada número o afirmación descriptiva tiene ID de hallazgo, filas/evidence
   refs y enlace a método/fuente; ninguna afirmación introduce causalidad,
   pronóstico, vacantes o recomendación individual.
3. Cada figura responde una sola pregunta, separa métrica/unidad/concepto y
   tiene tabla equivalente completa. Ausencia e incompatibilidad son visibles y
   nunca se convierten en cero.
4. Cada delta procede únicamente de un registro de comparación permitido. Las
   comparaciones bloqueadas se explican en un apéndice legible.
5. Una cifra real incluye método de precisión publicado y pasa el gate de
   fuente, población, diseño muestral y licencia. Sin ello, la salida es
   `REVIEW`, `UNKNOWN` o `BLOCKED`, según corresponda.
6. Abrir `index.html` desde disco no solicita recursos externos ni ejecuta
   código. HTML, Markdown, SVG/PNG y PDF opcional comparten manifest, run ID y
   hashes verificables.
7. Pruebas automatizadas cubren equivalencia HTML/Markdown, recursos externos
   prohibidos, navegación de encabezados, tablas/captions, contraste, impresión
   y que PDF —si existe— proviene del mismo HTML validado.

## Secuencia recomendada

1. Aprobar este contrato editorial y definir una plantilla estática con datos
   sintéticos para validar estructura, no para simular evidencia real.
2. Diseñar el modelo de `publication.json`, las fichas de hallazgo y las tablas
   por figura; añadir tests de correspondencia de claims, tablas y hashes.
3. Implementar la plantilla HTML/Markdown y su salida de impresión; evaluar PDF
   solo si el HTML impreso cubre una necesidad real de distribución.
4. Ejecutar revisión de accesibilidad y lectura con los cuatro perfiles del PRD.
5. Abrir M6 de ENOE como proyecto metodológico separado. La publicación final
   de cifras reales depende de sus gates, no de terminar el diseño editorial.
