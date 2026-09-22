# Registro de fuentes

Auditoría realizada el **2026-09-22** contra páginas primarias. El detalle
estructurado está en [source-research.json](source-research.json).

## Decisión

La ENOE de INEGI es la fuente priorizada para evaluar una extensión real posterior
al MVP. Esta decisión de planeación no activa una carga numérica: el catálogo
conserva `numeric_ingestion_allowed=false` hasta completar el contrato del dataset
y la validación metodológica. El paquete candidato inicial es el segundo trimestre de 2025, cuyo
catálogo RNM identifica el proyecto como `MEX-INEGI.ESD3.03-ENOE-2025-II`,
declara acceso público y enlaza los indicadores de precisión. INEGI permite
copiar, extraer, adaptar y publicar su información si se preservan los
metadatos, se acredita la fuente y se explica que la transformación no fue
realizada ni avalada por INEGI.

La búsqueda no encontró un tabulado pequeño de INEGI que publique por campo las
tres métricas elegidas. InfoLaboral permite tabulados flexibles de indicadores
estratégicos y los tabulados básicos publican agregados laborales, pero el cruce
por carrera/campo sigue requiriendo microdatos y validación del diseño. Por eso
el MVP usa fixtures sintéticos; no contiene observaciones ENOE numéricas.

OLA, Data México e IMCO siguen siendo referencias útiles, pero no son fuentes de
ingesta del MVP. MOPRADEF es un control negativo de comparabilidad.

## Matriz de auditoría

| Fuente | Acceso observado | Población / grain / periodicidad | Términos encontrados | Decisión y límite |
|---|---|---|---|---|
| [ENOE — programa](https://www.inegi.org.mx/programas/enoe/15ymas/), [RNM 2025 Q2-Q4](https://www.inegi.org.mx/rnm/index.php/catalog/1121) e [InfoLaboral](https://www.inegi.org.mx/programas/enoe/15ymas/tabulados/infolaboral.html) | Página, metadatos y descarga de microdatos públicos; el sitio lista resultados trimestrales hasta 2026-Q2 al auditar; InfoLaboral exporta agregados | Personas residentes en viviendas seleccionadas; características económicas captadas desde 12+, indicadores difundidos para 15+; microdato persona/hogar/vivienda; cobertura nacional, entidad y ciudades autorrepresentadas; levantamiento continuo y difusión mensual/trimestral | [Términos INEGI](https://www.inegi.org.mx/inegi/terminos.html): copia, difusión, adaptación, extracción y explotación permitidas; atribución, metadatos y aviso de transformación obligatorios | **Candidata priorizada; ingesta numérica no activada.** No se encontró tabulado pequeño por campo con las tres métricas; aplicar factor, estrato y UPM antes de integrar microdatos |
| [OLA — tendencias](https://www.observatoriolaboral.gob.mx/static/estudios-publicaciones/Tendencias_empleo.html), [tabla de Ciencias Sociales](https://www.observatoriolaboral.gob.mx/static/estudios-publicaciones/Sociales.html) y [condiciones](https://www.observatoriolaboral.gob.mx/static/acerca-ola/Condiciones_uso.html) | El endpoint principal devolvió 502 al fetch directo, pero las páginas estaban indexadas y la tabla de Ciencias Sociales reportaba actualización a 2026-Q2 | Personas ocupadas por carrera/área; tabla nacional; actualización trimestral aparente basada en ENOE STPS-INEGI | Condiciones informativas y limitación de responsabilidad; no se localizó permiso explícito de copia o redistribución | **Benchmark solamente.** No automatizar ni empaquetar. El encabezado “Ocupados (miles de personas)” frente al formato de los valores mostrados deja la unidad ambigua |
| [Data México — acceso](https://www.economia.gob.mx/datamexico/es/about/infoapi) y [términos](https://www.economia.gob.mx/datamexico/es/about/legal) | Viz Builder ofrece CSV y JSON; la página de versiones muestra actualización de empleo ENOE en 5.1.0 (2025-11-25) | Integra cubos de múltiples fuentes con distintos grains y periodicidades; cada cubo requiere su diccionario | Declara plataforma/contenido bajo AGPLv3, pero también restringe copias/descargas a uso personal no comercial y prohíbe alterar información; los términos son insuficientes para redistribuir un snapshot derivado sin aclaración | **Referencia/API manual, no ingesta.** No asumir que AGPL sobre la plataforma concede licencia uniforme sobre todos los datos |
| [IMCO — metodología](https://comparacarreras.imco.org.mx/metodologia/) | Acceso actual; edición 2026 documentada | Personas de 15 a 98 años con carrera profesional/posgrado concluido; campos detallados CMPE 2016; cuatro trimestres ENOE procesados y promediados; filtro CV ≤15% | La página indica “Todos los derechos reservados”; no se encontró licencia de datos reutilizable | **Referencia metodológica.** No copiar cifras. Su salario ajusta subreporte y atípicos, por lo que no es comparable con una media ENOE simple |
| [MOPRADEF](https://www.inegi.org.mx/programas/mopradef/default.html?init=1) | Página, resultados y metodología accesibles | Personas de 18+ en 2013-2024; desde 2025, personas de 12+; viviendas/hogares/personas; anual desde 2015 | Cubierto por los términos de libre uso de INEGI | **Fuera del dominio laboral.** Se usa como caso rojo: nueva muestra independiente desde 2024 y cambio conceptual/metodológico y de población en 2025 bloquean una serie ingenua |

## Referencia de OLA y restricción de redistribución

La tabla oficial de Ciencias Sociales contiene información sobre los tres
campos elegidos. La auditoría conserva la URL, la fecha, la limitación de acceso
y la ambigüedad de unidad; no redistribuye las cifras observadas porque no se
estableció una licencia suficiente para incorporarlas al proyecto.

La selección de campos permite probar conceptos, nulos y comparabilidad. No es
un ranking de carreras ni una recomendación basada en ingresos. Una extensión
real debe reconstruir los indicadores desde una fuente autorizada y documentar
cualquier diferencia de población o metodología.

## Notas metodológicas obligatorias

- ENOE es una encuesta probabilística. Una suma ponderada es una estimación, no
  un conteo administrativo.
- Las características económicas se refieren a la semana anterior a la
  entrevista; los ingresos, al mes anterior. El trimestre es el periodo de
  publicación, no una promesa de que cada variable mida todo el trimestre.
- El cuestionario ampliado se aplica en el primer trimestre y el básico en los
  demás. No se debe asumir que todas las variables existen igual en Q1 y Q2-Q4.
- La población de un indicador debe expresarse en cada observación. “Personas
  que estudiaron el campo”, “personas ocupadas del campo” y “personas que
  ejercen una ocupación relacionada” son universos diferentes.
- IMCO combina cuatro trimestres, filtra por CV y ajusta ingresos por subreporte
  y atípicos. Sus resultados no validan por igualdad una estimación trimestral
  simple.
- Data México integra fuentes y versiones; su etiqueta no reemplaza la
  metodología ni los términos de la fuente originaria.

## Atribución para la extensión ENOE

Usar una forma equivalente a:

> Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo (ENOE), bases de datos
> del segundo trimestre de 2025. Cálculos y transformación de Brújula Laboral
> MX; no realizados ni avalados por INEGI. Consulta: 2026-09-22.

Conservar además URL exacta, SHA-256 del archivo descargado, parámetros,
diccionario usado, hora de fetch y versión del código.
