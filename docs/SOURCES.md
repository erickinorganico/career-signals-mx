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

## Inventario local verificado de ocho paquetes ENOE

La autoridad de custodia es `data/catalog/enoe-snapshots.json`: fija las ocho URL
oficiales, el SHA-256 de cada ZIP, sus fichas, términos y aprobación de
**adquisición**. `inventory_all(Path('artifacts/enoe'))` resuelve exclusivamente
el intento `current.json` y su recibo inmutable. Un intento fallido, en curso,
ausente o alterado bloquea el inventario; un éxito histórico no lo sustituye.
El inventario no autoriza por sí solo una cifra ni la publicación de microdatos.

La tabla resume una verificación local del 2026-09-22. Cada miembro SDEM es
`conjunto_de_datos_sdem_enoe_YYYY_Nt/conjunto_de_datos/conjunto_de_datos_sdem_enoe_YYYY_Nt.csv`;
el diccionario es el miembro hermano
`diccionario_de_datos/diccionario_datos_sdem_enoe_YYYY_Nt.csv` y el catálogo
es `catalogos/cs_p14_c.csv`. El JSON local ignorado
`.cache/research/enoe-source-inventory.json` registra las rutas completas,
SHA-256 y bytes de cada miembro, identificador y hash del recibo, fecha de
adquisición, encabezado completo y metadatos de fuente. No contiene filas de
personas ni bytes de ZIP.

| Corte y ficha INEGI | SHA-256 ZIP | SHA-256 SDEM | Columnas / entidad | SHA-256 diccionario | Bitácora SDEM |
|---|---|---|---|---|---|
| 2024-Q3 · [2403872](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=2403872) | `f384a1b8872e051856ed2241289400302b13a8701489b1c596390452c183cd01` | `a2b8ea7a64ae2c6b428526da24c6c62894decd7d1b0520853472966e69522135` | 114 / `ent` | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | 4 cambios `cs_p14_c`, 2025-05-27; SHA `cc3101c01a94cd7e9e810f82bc1cd2d49f3cf867d4ee5fc9e0761f6e283d565e` |
| 2024-Q4 · [2534385](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=2534385) | `bb6d958c9bca11672d367d2c051cd08bf1654c471c2f32c8e21992c126a3b426` | `b5d39d8b6afa2c554f3f68a225293d4ab6531706823d2c9084b7c002ae769f86` | 114 / `ent` | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | 9 cambios: 5 `cs_p14_c`, 1 `par_c`, 1 `cs_p20a_c`, 2 `cs_p20b_c`, 2025-05-27; SHA `4716ded92c64ae5053e1f20c6d5df188eed8bf14e503ae88a86e7321cf4062e5` |
| 2025-Q1 · [2715160](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=2715160) | `3931e7c9242147da6ebf9badb1e2b9a59d43d95a9811e077232be406c4ce6691` | `bcb310cbd5b695db264da0f0dcaef266d047a037486853012e5cbc096d7abbf5` | 114 / `ent` | `410dff0ef72908a275e01be116e1bce949d79a38e17a403427840680c64cd51d` | Sin miembro de bitácora SDEM en este ZIP |
| 2025-Q2 · [2985637](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=2985637) | `9530a017e3defb0658418b73a47a6039eeb54abf11342fa10693374736515127` | `c9f1a2adf14b388be7d1a68ef57d30fd92356d36f522cc7e3ac32de6ab5a48d8` | 114 / `ent` | `ce67f37024a4a60767b0b140ad249e9eca98bf900459117cf82f63c3649d251b` | Sin miembro de bitácora SDEM en este ZIP |
| 2025-Q3 · [3161259](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=3161259) | `7138b2bfabc740a9805b83b3fd0dae28287fc2aab3781a596a741b8fc7861566` | `04bd5d5f9668848ac6c435f29abe3b20e6693f02f2ee880a1e9dc0aab1c94c9d` | 115 / `cve_ent` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | Sin miembro de bitácora SDEM en este ZIP |
| 2025-Q4 · [3233652](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=3233652) | `e4d4284cc9924a40c39544a5530715f320a5627cd81997214c0430827616d9d6` | `088a2affeaef800bd9941656869392290905a9cf597af42a15d748b13b43de7e` | 115 / `cve_ent` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | Sin miembro de bitácora SDEM en este ZIP |
| 2026-Q1 · [3634157](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=3634157) | `429c288af46e408de743e5dfb92750f668df7e42789be5824f7cdf1c5ff56580` | `8bf2b74f4222b72c5d717509a7527213346564f17acd1affdce7f50bd21daeca` | 115 / `cve_ent` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | Sin miembro de bitácora SDEM en este ZIP |
| 2026-Q2 · [3946334](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=3946334) | `9ef8877c363f6097da1a04b2077cbda96300cc474b38f835c4963d1dd8f953df` | `6256468cd6cf5ed08b8538f8094eb3cf20793cb669ba0084c18f571fc8f78407` | 115 / `cve_ent` | `43dd74055f8d4c934c5101b68f70065517f4a4b538d8230592e273b4c0ec6cbe` | Sin miembro de bitácora SDEM en este ZIP |

Los ocho catálogos `cs_p14_c.csv` tienen SHA-256
`b521d2b5a07e3471da1bd6792183bb2c6864a38e022f74a6a919990c49f4a871`.
El diccionario 2025-Q1 tiene hash propio, distinto al de 2024-Q3/Q4 y 2025-Q2.
La longitud declarada de `cs_p14_c` es seis caracteres. Las claves ASCII
`31300`, `32100` y `33100` del catálogo se validan y rellenan a
`031300`, `032100` y `033100` para Ciencias políticas, Comunicación y
periodismo, y Derecho; `999999` y ausencia siguen siendo desconocidos.

El cambio de cabecera `ageb/ent/loc/mun` a
`cve_ageb/cve_ent/cve_loc/cve_mun`, con `cvegeo` añadido, se observa desde
2025-Q3. La equivalencia conceptual entre periodos queda en `REVIEW` y
requiere validación antes de calcular diferencias temporales. La ausencia de
bitácora en los otros seis ZIP no afirma que jamás hayan tenido revisiones.
Los bytes de metadatos se decodifican como UTF-8; la codificación de las filas
de personas aún no está establecida y debe auditarse en la fase de ingesta.

Fuente: INEGI, Encuesta Nacional de Ocupación y Empleo, ocho paquetes
trimestrales 2024-Q3–2026-Q2. [Términos de libre uso de INEGI](https://www.inegi.org.mx/inegi/terminos.html).
La selección de miembros, verificación de hashes, normalización de claves y
este inventario son transformaciones de Brújula Laboral MX, no realizadas ni
avaladas por INEGI. Los ZIP y microdatos quedan en almacenamiento local
ignorado; solo los metadatos y futuros agregados validados pueden entrar en
un artefacto público.
