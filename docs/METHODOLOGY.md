# Metodología analítica y estadística

Fecha: 2026-09-22. Aplica al piloto sintético y define las condiciones para una
extensión ENOE real. No convierte el fixture en una estimación de México.

## Unidad conceptual

Un **campo de estudio** clasifica formación; una **ocupación** clasifica trabajo
desempeñado; una **industria** clasifica la actividad de la unidad económica; una
**vacante** es una oportunidad publicada. Son entidades distintas. Un bridge
puede proponer relación entre ellas, pero no crea identidad ni equivalencia.

## Piloto v1

- Campos: Derecho, Comunicación y periodismo, Ciencias políticas.
- Periodos ilustrativos: 2025-Q2, 2025-Q3 y 2025-Q4.
- Geografías: México nacional y Jalisco ilustrativo.
- Métricas: `employed_people`, `mean_monthly_income`, `female_share`.
- Fuente: fixture local sintético, con IDs `demo_*`.
- Estado: valor sintético presente = `REVIEW`; ausencia = `UNKNOWN` y `null`.

Los números del fixture prueban contratos, visualizaciones y comportamiento de
fallo. No estiman población, empleo o ingreso reales.

## Definiciones de métricas

### Personas ocupadas

Para una fuente real:

\[
\widehat{N}_{ocupadas,c}=\sum_{i\in U_c} w_i I(ocupada_i=1)
\]

`U_c` es la población elegible del campo `c`, `w_i` el factor de expansión y
`I` el indicador de condición ocupada reconstruido según documentación oficial.
Unidad: personas estimadas. No representa vacantes, empleos disponibles ni
egresados recientes.

### Ingreso laboral mensual medio

\[
\bar y_c=\frac{\sum_{i\in U_c^+} w_i y_i}{\sum_{i\in U_c^+}w_i}
\]

`U_c^+` incluye únicamente personas ocupadas elegibles con ingreso monetario
mensual válido y positivo. Faltantes, no respuesta e ingresos no monetarios no
se convierten en cero. Unidad: MXN corrientes por mes; base `nominal`.

Los pesos nominales no miden poder adquisitivo. Comparar periodos nominales solo
describe pesos de cada fecha. Un análisis real requiere deflactor, periodo base,
fuente, fórmula y nueva `methodology_id`.

### Participación de mujeres

Sea `O_c` el conjunto de personas ocupadas elegibles del campo `c` que tienen
un valor válido en la variable de sexo de la fuente:

\[
100\times\frac{\sum_{i\in O_c}w_iI(sexo_i=mujer)}
{\sum_{i\in O_c}w_i}
\]

Numerador y denominador se restringen a personas ocupadas con sexo registrado
válido. “Mujer” conserva la codificación de la variable fuente y no debe
reinterpretarse como identidad de género. La métrica no demuestra igualdad,
discriminación, preferencia ni causalidad.

## Comparabilidad

Dos observaciones son comparables solo si coinciden todos estos campos:

1. tipo e ID de concepto;
2. población/universo y filtros;
3. geografía y dominio representativo;
4. métrica, unidad y fórmula;
5. base de precios;
6. fuente y versión metodológica;
7. clasificación y bridge aplicables;
8. condición sintética/real;
9. tratamiento de faltantes y precisión.

Además, los periodos deben ser distintos y estar ordenados. En v1, cualquier
diferencia produce `BLOCKED` para el delta. Un bridge o una etiqueta editorial
no restaura comparabilidad. Una armonización futura requiere metodología
validada, revisión adversarial y una serie nueva, separada y versionada; nunca
reescribe la serie original. `null` nunca se sustituye por cero. Un cambio
porcentual con base cero es `null`, aunque pueda informarse el cambio absoluto.

MOPRADEF ilustra una ruptura: el cambio de operativo/muestra desde 2024 y de
población objetivo/metodología desde 2025 impide concatenar ingenuamente la
serie. No es una fuente laboral del producto.

## Precisión para ENOE real (M6)

ENOE es una encuesta probabilística compleja, no un censo. Una extensión real
debe usar factor de expansión, estrato y UPM de la versión correspondiente y un
estimador de varianza compatible con el diseño. Debe registrar al menos:

- `sample_size` no ponderado;
- estimación ponderada;
- error estándar o coeficiente de variación;
- intervalo de confianza cuando proceda;
- dominio, cuestionario y periodo;
- exclusiones y no respuesta.

Los umbrales de publicación serán una política del proyecto, versionada y
probada; no se presentarán como umbrales oficiales de INEGI. Como referencia
metodológica, IMCO publica un filtro CV ≤15% para ciertos indicadores de su
edición, pero ese criterio pertenece a su metodología y no se hereda
automáticamente.

Hasta implementar varianza del diseño, una cifra real calculada desde microdatos
permanece `REVIEW` con `precision_note`; es un artefacto interno de investigación
y no es publicable como release numérico. La fuente continúa inactiva para
ingesta pública. `MEASURED` exige licencia, source snapshot, método, población,
precisión y evidencia resueltos.

## Fuentes auditadas

- [INEGI ENOE](https://www.inegi.org.mx/programas/enoe/15ymas/) y
  [metadatos RNM 2025](https://www.inegi.org.mx/rnm/index.php/catalog/1121):
  candidato primario de M6. Acceso público y diseño documentado.
- [Términos de libre uso de INEGI](https://www.inegi.org.mx/inegi/terminos.html):
  permiten copiar, extraer, adaptar y publicar con atribución, preservación de
  metadatos y aviso de transformación.
- [OLA/STPS](https://www.observatoriolaboral.gob.mx/static/estudios-publicaciones/Tendencias_empleo.html)
  y [condiciones](https://www.observatoriolaboral.gob.mx/static/acerca-ola/Condiciones_uso.html):
  referencia editorial; sin licencia de redistribución explícita encontrada y
  con ambigüedad de unidad observada. No se redistribuyen cifras.
- [Data México](https://www.economia.gob.mx/datamexico/es/about/infoapi) y
  [términos](https://www.economia.gob.mx/datamexico/es/about/legal): referencia
  de acceso; la licencia uniforme de datasets derivados no quedó clara.
- [IMCO Compara Carreras](https://comparacarreras.imco.org.mx/metodologia/):
  referencia metodológica, no fuente numérica redistribuida.
- [INEGI MOPRADEF](https://www.inegi.org.mx/programas/mopradef/default.html?init=1):
  control negativo de ruptura metodológica.

## Freshness

La frescura se calcula desde el fin del periodo de negocio, separada de la fecha
de ejecución/descarga. Para fixture, el estado es `REVIEW` ilustrativo. Para una
fuente real, un umbral vencido produce warning/`REVIEW`; un fallo de descarga
produce `BLOCKED`. Un artefacto histórico exitoso no sustituye el estado current.

## Claims e insights

Cada insight separa:

- **observación:** cifra/estado que existe en una fila;
- **interpretación:** lectura descriptiva compatible con población y método;
- **recomendación:** siguiente pregunta o uso prudente;
- **unknowns:** lo que la evidencia no resuelve;
- **evidence_refs:** referencias internas resolubles.

No se generan predicciones causales ni orientación individual como certeza. Un
agente puede proponer texto o gráfica, pero cálculos, comparaciones y render son
deterministas.

## Criterio de promoción de fuente real

La ENOE pasa de candidata a activa únicamente cuando un paquete específico tiene
URL y licencia verificadas, raw con SHA-256, diccionario y clasificación
versionados, población/fórmula cerradas, ponderación y varianza verificadas,
pruebas de precisión/nulos/comparabilidad y revisión adversarial. La aprobación
de metadata no autoriza publicación numérica.
