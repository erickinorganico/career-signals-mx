# Tener ocupación y trabajar en lo que se estudió

Revisión de fuentes: 28 de septiembre de 2026. Alcance: consulta documental;
no activa una fuente ni una estimación nueva en el conjunto de datos.

## Qué mide el informe

La proporción publicada divide las personas ocupadas entre las personas del
grupo con situación laboral conocida, incluidos quienes están fuera de la
fuerza laboral. No mide afinidad con la carrera, formalidad ni calidad laboral.
El complemento tampoco es una tasa de desempleo.

La revisión independiente del CSV local ENOE 2026-T2, aplicando el universo
documentado en `brujula/populations.py` y sumando `FAC_TRI`, reprodujo:

| Estudios | Ocupados ponderados | Total ponderado con CLASE2 1–4 | Proporción |
|---|---:|---:|---:|
| Derecho | 983,740 | 1,296,754 | 75.8617% |
| Comunicación y periodismo | 160,373 | 214,211 | 74.8668% |
| Ciencias políticas | 95,799 | 125,932 | 76.0720% |

Numerador: `CLASE2=1`. Universo: residentes elegibles, estudios profesionales
terminados y edad conocida de 15+; excluye estudios técnicos, posgrado e
incompletos. Son estimaciones del proyecto con precisión no oficial.

## Sí existe información sobre afinidad

El [Observatorio Laboral de la STPS, Tendencias del empleo profesional](https://observatoriolaboral.gob.mx/static/estudios-publicaciones/Tendencias_empleo.html)
publica un indicador de relación entre ocupación y estudios. La página
consultada identifica 2026-T2 y reporta **82.3%** como promedio de afinidad
de los profesionistas ocupados. Es una referencia externa nacional: no es el
resultado de Derecho, Comunicación o Ciencias políticas por separado.

La [tabla de Ciencias Sociales](https://observatoriolaboral.gob.mx/static/estudios-publicaciones/Sociales.html)
incluye las tres carreras, pero sus columnas son ocupados, distribución por
sexo e ingreso; no incluye una columna de afinidad. No deben interpretarse
los porcentajes de hombres o mujeres como afinidad.

La [tabla histórica de carreras con más ocupados](https://www.observatoriolaboral.gob.mx/static/que-quieres-ser/Mayor_ocupados.html)
sí muestra afinidad de Derecho, pero corresponde a **2017-T1**, no a 2026.
No se usa como resultado actual. En las páginas consultadas no se verificó
una cifra actual de afinidad para cada una de las tres carreras.

## Qué falta para incorporarlo como resultado comparable

Necesitamos una definición reproducible de afinidad, sus correspondencias
entre códigos de estudio y ocupación, filtros, periodo y precisión. El
[glosario de OLA](https://observatoriolaboral.gob.mx/static/herramientas-sitio/Glosario_terminos.html)
describe conceptos y cifras anualizadas, pero no establece por sí solo el
algoritmo de afinidad del indicador consultado. No se asume que OLA y este
proyecto utilicen el mismo universo o ventana temporal.

Contar únicamente a quienes tienen el título ocupacional «abogado», por
ejemplo, no sería automáticamente una medida válida de afinidad: excluiría
otras actividades relacionadas sin una regla documentada. Tampoco se puede
multiplicar nuestro porcentaje de ocupación por el promedio nacional de OLA.

Estado por carrera: **no disponible como estimación validada del proyecto**.
OLA permanece como referencia documental del catálogo; no se ingieren sus
tablas ni se incorporan sus cifras a las gráficas ENOE del release.
