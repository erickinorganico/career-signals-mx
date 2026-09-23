# ENOE: especificación estadística por campo de estudio

Fecha de revisión: 2026-09-22. Estado: **método propuesto; habilitación numérica pendiente de pruebas de aceptación**. Esta revisión no activa fuentes ni publica estimaciones reales. Se revisaron documentos oficiales, metadatos y el encabezado del paquete 2026Q2 obtenido por el integrador; no se ejecutó aquí una descarga masiva ni una reconciliación con microdatos.

## 1. Dictamen y alcance identificable

**Sí existe carrera estudiada en ENOE trimestral.** El cuestionario sociodemográfico pregunta la carrera que la persona estudia o estudió y si terminó sus estudios o materias. Es información educativa, no una inferencia a partir de su ocupación. Las preguntas 13–17 también permiten distinguir nivel, egreso y asistencia escolar. “Terminó materias” no equivale a título profesional. Fuente leída: [cuestionario sociodemográfico, preguntas 13–17, páginas PDF 3–4](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/c_sdem_v5a.pdf).

El archivo pertinente es **SDEMT**, que contiene `CS_P14_C`; los COE aportan preguntas económicas y comprobaciones de codificación. La [estructura de la base 2025, tabla SDEMT, páginas PDF 16–18](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_325_fd_c_bas_amp.pdf) declara `CS_P14_C` de tipo carácter, longitud 6, y CMPE 2016 desde III-2021. La longitud de almacenamiento no demuestra que todos sus valores tengan seis dígitos significativos.

El producto identificable es: **situación laboral de personas cuyo campo educativo declarado cumple un universo explícito**. No mide vacantes, demanda de contratación, retorno causal de estudiar una carrera ni el conjunto de personas con cualquier título previo en ese campo. La carrera reportada puede corresponder a posgrado: no permite reconstruir todas las licenciaturas previas.

Para evitar esa ambigüedad, se propone una primera población principal: personas de edad conocida de 15 años o más, residentes actuales, con nivel declarado `07 Profesional`, materias terminadas y campo identificado. Etiqueta: “Personas ocupadas con estudios profesionales terminados en el campo declarado”. Una extensión a `07/08/09` debe llamarse “campo de los estudios superiores declarados terminados”, conservar nivel y usar otro `population_id`; no presentarla como todos los egresados de licenciatura.

## 2. Archivos y contratos por periodo

| Periodo | Evidencia leída | Selección de tabla |
| --- | --- | --- |
| 2025Q1 | [RNM 1104, cuestionario ampliado](https://www.inegi.org.mx/rnm/index.php/catalog/1104) | Verificar el miembro SDEMT del paquete de Q1; no reutilizar posiciones del COE básico. |
| 2025Q2 | [RNM, diccionario SDEMT225](https://www.inegi.org.mx/rnm/index.php/catalog/1121/data-dictionary/F42?file_name=SDEMT225) | Tabla `SDEMT225`; el diccionario enumera `FAC_TRI`, `EST_D_TRI`, `UPM`, `ENT`. |
| 2025Q3 | [RNM, diccionario SDEMT325](https://www.inegi.org.mx/rnm/index.php/catalog/1121/data-dictionary/F47?file_name=SDEMT325) y estructura 2025 | Tabla `SDEMT325`; aplicar contrato geográfico nuevo. |
| 2025Q4 | [RNM, inventario de archivos](https://www.inegi.org.mx/rnm/index.php/catalog/1121/data-dictionary) | Tabla `SDEMT425`; confirmar encabezado y catálogo incluidos. |
| 2026Q1 | El integrador localizó la ficha del programa; esta revisión no inspeccionó sus miembros. | **Pendiente por paquete**, no copiar nombres físicos de 2025 por suposición. |
| 2026Q2 | Encabezado y diccionario/catálogo incluidos, inspeccionados en copia local del [ZIP oficial](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2026/conjunto_de_datos_enoe_2026_2t_csv.zip). | Miembro `conjunto_de_datos_sdem_enoe_2026_2t/conjunto_de_datos/conjunto_de_datos_sdem_enoe_2026_2t.csv`; 115 columnas en minúsculas, incluidos `fac_tri`, `est_d_tri`, `upm` y `cve_ent`. |
| 2024Q3–Q4, si se extiende a ocho trimestres | Fuera de la verificación documental de paquetes de esta revisión. | Candidatos a la misma familia CMPE; requieren manifiesto y prueba de equivalencia propios. |

El [registro oficial de pestañas del programa](https://www.inegi.org.mx/programas/enoe/15ymas/data/pestana/pestanadata.js), leído en la copia local `.cache/research/tabs.json` obtenida por el integrador, anuncia desde 2025Q3 el cambio `AGEB/ENT/LOC/MUN` → `CVE_AGEB/CVE_ENT/CVE_LOC/CVE_MUN` y la incorporación de `CVEGEO`. Esto es deriva de esquema confirmada, no evidencia de cambio del factor.

Contrato propuesto de ingestión: guardar URL, SHA-256, fecha de revisión, miembros del ZIP, encabezado, diccionario y catálogo por trimestre; resolver miembros por manifiesto validado; leer claves como texto; rechazar encabezados duplicados, dos alias contradictorios o faltantes. `SDEM` es el nombre conceptual usado en documentos; no constituye un nombre de archivo universal. Las uniones COE–SDEMT deben usar la clave de persona documentada en cada paquete, con unicidad, cardinalidad 1:1 y cobertura auditadas; no unir solo por `N_REN` o por fila.

## 3. Diccionario mínimo verificable

Los nombres siguientes se verificaron en documentación 2025. Son columnas de origen, no campos nuevos ya implementados.

| Finalidad | Variable y regla | Fuente primaria leída |
| --- | --- | --- |
| Entrevista | `R_DEF=00`, entrevista lograda. | [Cuestionario sociodemográfico, portada](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/c_sdem_v5a.pdf). |
| Residencia | `C_RES` 1 habitual, 2 ausente definitivo, 3 nuevo; incluir 1 y 3. | [Ficha C_RES](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5654?name=C_RES). |
| Edad | `EDA`: 15–96 edades; 97 significa 97 o más; 98 edad desconocida de personas de 12+; 99 desconocida de menores. No interpretar 98 como 98 años. | [Ficha EDA](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5657?name=EDA). |
| Sexo registrado | `SEX`: 1 hombre, 2 mujer. No equivale a identidad de género. | [Cuestionario, pregunta 8](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/c_sdem_v5a.pdf). |
| Nivel | `CS_P13_1`: 05 normal, 06 técnica, 07 profesional, 08 maestría, 09 doctorado; `CS_P13_2`: años aprobados. | [Estructura 2025, página PDF 17](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_325_fd_c_bas_amp.pdf). |
| Egreso | `CS_P16`: 1 sí, 2 no, 9 desconocido; pregunta aplicable a niveles 05–09. | [Ficha CS_P16](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5667?name=CS_P16). |
| Ocupación económica | `CLASE2`: 1 ocupado, 2 desocupado, 3 inactivo disponible, 4 inactivo no disponible, 0 no aplica. La variable se construye para 12+; aplicar universo de publicación. | [Ficha CLASE2](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5688?name=CLASE2). |
| Ingreso mensual | `INGOCUP`; es ingreso mensual de ocupados, no salario exclusivo de subordinados. El cero observado en la tabla completa no identifica por sí mismo ingreso nulo. | [Ficha INGOCUP](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5729?name=INGOCUP). |
| Estado de ingreso | `ING7C`: 0 no aplica; 1–5 intervalos de ingreso; 6 no recibe ingresos; 7 no especificado. | [Ficha ING7C](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5694?name=ING7C). |
| Horas | `HRSOCUP`, horas trabajadas en la semana; distinguir cero de desconocido con la pregunta original y clasificación de jornada. | [Ficha HRSOCUP](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5728?name=HRSOCUP), [DUR9C](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5695?name=DUR9C). |
| Informalidad | `EMP_PPAL`: 1 informal, 2 formal, 0 no aplica, referido al trabajo principal. No sustituirlo por sector informal o ausencia de acceso médico. | [Ficha EMP_PPAL](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5739?name=EMP_PPAL). |
| Expansión trimestral | `FAC_TRI`, no `FAC_MEN`, ni peso unitario. Validar positivo, finito, no nulo; conservar escala oficial. | [Ficha FAC_TRI](https://www.inegi.org.mx/rnm/index.php/catalog/1121/variable/F42/V5685?name=FAC_TRI). |
| Diseño | `EST_D_TRI` para estratificación de diseño y `UPM` para conglomerados; no usar `EST` socioeconómico como sustituto. | [Diccionario SDEMT225](https://www.inegi.org.mx/rnm/index.php/catalog/1121/data-dictionary/F42?file_name=SDEMT225). |

`EDA=98` exige decisión explícita: la propuesta de campo exige edad conocida y registra exclusiones. Para reproducir tabulados oficiales, verificar por separado el tratamiento oficial de edad no especificada; no cambiar el filtro hasta obtener una coincidencia y luego ocultar el cambio. La reconstrucción oficial mantiene una categoría de edad no especificada, por lo que un `EDA >= 15` indiscriminado no documenta correctamente el universo.

### Carrera CMPE: resolver el código antes de calcular

La [CMPE 2016, páginas impresas 14–15 y 20, PDF 24–25 y 30](https://inegi.org.mx/contenidos/productos/prod_serv/contenidos/espanol/bvinegi/productos/nueva_estruc/702825086664.pdf) distingue campo detallado de cuatro dígitos, algunos campos unitarios de seis y claves de planes que pueden incorporar nivel educativo. Los campos requeridos son:

| Campo detallado CMPE 2016 | Etiqueta |
| --- | --- |
| `0313` | Ciencias políticas |
| `0321` | Comunicación y periodismo |
| `0331` | Derecho |

**Representación confirmada para 2026Q2:** el catálogo incluido `cs_p14_c.csv` contiene `31300`, `32100` y `33100` con esas etiquetas; el diccionario declara longitud 6. El perfil del integrador identifica en datos `031300`, `032100`, `033100`. El cruce explícito propuesto es `031300→0313`, `032100→0321`, `033100→0331`. Para este catálogo se justifica completar a seis posiciones los códigos numéricos; no aplicar la operación universalmente sin validar otros periodos. No quitar un supuesto prefijo educativo. `0312` no es Ciencias políticas en esta clasificación. Administración pública tampoco se incorpora automáticamente al campo político. Cualquier agrupación distinta requiere otro concepto y un cruce revisable.

Evidencia local leída: `.cache/research/enoe2026q2-metadata/{cs_p14_c.csv,diccionario_datos_sdem_enoe_2026_2t.csv}` y encabezado de `sdem_2026_q2.csv`. ZIP identificado por SHA-256 `9ef8877c363f6097da1a04b2077cbda96300cc474b38f835c4963d1dd8f953df`; vínculo primario: [conjunto de datos oficial 2026Q2](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/datosabiertos/2026/conjunto_de_datos_enoe_2026_2t_csv.zip). El primer receipt del probe conserva un fallo por assertion; el perfil posterior no debe sustituirlo ni tomarse como validación de todas las estimaciones.

### Ingreso y horas: evitar falsos ceros

La [reconstrucción oficial, sección 10.10–10.12, página impresa 108/PDF 123](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/recons_var_15ymas.pdf) enlaza horas con `P5C_THRS` en ampliado y `P5B_THRS` en básico; ingreso con `P6B2`. Esa sección usa 1–999997 para ingreso; la estructura 2025 y el diccionario incluido 2026Q2 muestran 1–999998 para `INGOCUP`. Para Q2 prevalece el diccionario específico del paquete: rango 1–999998, reservando la contradicción con el documento histórico en el log. `999999` no es monto válido. No multiplicar nuevamente un ingreso mensual ya construido por una frecuencia de pago.

Política de normalización propuesta:

1. Guardar valor original, estado y razón de exclusión por separado.
2. `ING7C=6` identifica sin ingreso; un `INGOCUP=0` con `ING7C=7` sigue desconocido.
3. Para el promedio principal conservar ingreso monetario positivo de monto conocido; rangos conocidos sin monto exacto no se convierten en puntos medios. Conservar cobertura ponderada de monto válido, sin ingreso y no respuesta.
4. Un ingreso positivo incompatible con clasificación de no ingreso, códigos especiales o monto desconocido bloquea la fila para ese cálculo hasta resolver la regla; no corregir por conveniencia.
5. Un promedio alternativo que incluya ceros confirmados requiere otro identificador y denominador. No sustituye silenciosamente al promedio positivo.
6. Horas reales cero pueden ser válidas para ausentes temporales; horas desconocidas no son cero. La reconstrucción, sección 3.16–3.17, distingue ausencia temporal, horas 0–14 y código 999/no especificado; confirmar la correspondencia con `DUR9C` en cada paquete. Para ingreso por hora, horas cero impiden dividir; tampoco equivale la media de razones a razón de totales.

## 4. Estimadores propuestos

Sea `w_i=FAC_TRI`, `D_i` indicador del dominio educativo/geográfico/etario, `O_i=1(CLASE2=1)` y `A_i` indicador de información válida para la métrica. Los indicadores se materializan sin NA; una ausencia real del dato se conserva en una columna de estado.

| Métrica | Numerador X | Denominador Y | Interpretación |
| --- | --- | --- | --- |
| Ocupados | Σ w D O | No aplica | Total de personas, no puestos ni vacantes. |
| Mujeres entre ocupados | Σ w D O 1(SEX=2) | Σ w D O 1(SEX∈{1,2}) | 100 X/Y; cobertura de sexo visible. |
| Ingreso mensual positivo conocido | Σ w D O A INGOCUP | Σ w D O A | Media en MXN nominales; A exige monto positivo válido. |
| Informalidad principal | Σ w D O 1(EMP_PPAL=1) | Σ w D O 1(EMP_PPAL∈{1,2}) | 100 X/Y; auditar categoría no aplica dentro de ocupados. |
| Horas semanales válidas | Σ w D O A HRSOCUP | Σ w D O A | Requiere normalización de horas previamente validada. |

Para cada métrica almacenar `n_unweighted_domain`, `n_unweighted_valid`, denominador ponderado, porcentaje ponderado de cobertura, UPM contribuyentes y exclusiones. `sample_size` es el número de personas observadas del denominador pertinente, nunca Σw. Desempleo, si se incorpora, usa desocupados/PEA, no desocupados/ocupados.

## 5. Varianza por diseño y dominios

La [metodología RNM 2025, apartados de muestreo y estimación](https://www.inegi.org.mx/rnm/index.php/catalog/1121) describe selección estratificada por conglomerados, pesos ajustados y rotación de viviendas. El [diseño ENOEN 2021, secciones 6.1, 7 y 8, PDF 5–7](https://www.inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_n_diseno_muestral.pdf) documenta conglomerados últimos y Taylor, además de agrupación oficial de estratos escasos. Es antecedente metodológico, **no certificación de que todos los detalles del operativo 2021 sigan vigentes en 2026**.

Propuesta implementable: estimador de conglomerados últimos con reemplazo, usando pesos finales y estratos de diseño publicados; identificarlo como aproximación con pesos finales. No inventar FPC ni afirmar varianza exacta que incorpore calibración sin información auxiliar suficiente. Validar esta decisión contra precisiones oficiales actuales antes de declararla aceptada.

Construir primero la estructura de diseño de la muestra respondente residente completa, antes de filtrar carrera, edad, ocupación o ingreso. Resolver `R_DEF=00` y `C_RES∈{1,3}` con tipos normalizados. El perfil Q2 contiene factores cero en el archivo bruto: auditar si pertenecen únicamente a registros fuera de ese universo; un factor cero dentro del universo de diseño requiere explicación y no se descarta silenciosamente. Definir estrato global a partir del identificador oficial y, si no es globalmente único, entidad + estrato. Comprobar anidamiento UPM/estrato. No modificar estratos para conseguir resultados finitos.

Para cada estrato h con m_h UPM originales y aportes de total T_hj:

```text
T_hj = Σ_personas_en_UPM(h,j) w_i D_i O_i y_i
T̄_h = Σ_j T_hj / m_h
V̂(T̂) = Σ_h [m_h/(m_h−1)] Σ_j (T_hj − T̄_h)²
```

Para razón R̂=X̂/Ŷ, crear aportes linealizados por persona y agregarlos por UPM:

```text
z_i = w_i (x_i − R̂ y_i) / Ŷ
Z_hj = Σ_i_en_UPM(h,j) z_i
V̂(R̂) = Σ_h [m_h/(m_h−1)] Σ_j (Z_hj − Z̄_h)²
SE = sqrt(V̂)
CV_percent = 100 × SE / abs(estimate), si estimate != 0
```

Aquí `x_i,y_i` incluyen el indicador de dominio y las condiciones de validez. Una persona fuera del dominio aporta cero algebraico; esto **no imputa cero al dato faltante**. Una UPM sin integrantes del dominio permanece con aporte cero. El m_h del cálculo proviene del diseño completo.

El [manual autoritativo de R survey 4.5-2, secciones svydesign, svyCprod y surveyoptions](https://r-forge.r-universe.dev/survey/doc/manual.html) documenta la aproximación sin FPC, preservación de UPM en dominios y manejo de estratos con una sola UPM. Usar R como oráculo independiente de la futura implementación Python; registrar versión y opciones. Esto no exige un servicio externo.

Reglas de fallo propuestas:

- Estrato de diseño con una sola UPM: `BLOCKED`, salvo tratamiento oficial documentado. No usar automáticamente `remove`, `certainty`, `adjust` o `average`; que el algoritmo acepte una opción no demuestra que sea apropiada.
- Una sola UPM **del dominio** dentro de un estrato con varias UPM de diseño es otro caso: conservar las demás con cero; registrar la escasez. No reducir m_h a uno.
- Denominador cero, falta de diseño o varianza no finita: estimación publicable nula, motivo visible. Ausencia de muestra no demuestra ausencia poblacional.
- Proporción observada 0/1 o media constante puede producir SE estimado cero: no describirla como certeza; exigir revisión de frontera y soporte antes de liberar.

Para el oráculo, construir `svydesign(ids=~UPM, strata=~stratum_id, weights=~FAC_TRI, nest=TRUE, data=full_design)` con `survey.lonely.psu="fail"`. Crear columnas explícitas de numerador/denominador con ceros fuera del dominio; usar `svytotal` y `svyratio`. No crear el diseño a partir del CSV previamente filtrado a Derecho.

## 6. Precisión y publicación

La [ficha oficial de indicadores de precisión 2025Q2](https://www.inegi.org.mx/rnm/index.php/catalog/1121/related-materials), sección “segundo trimestre”, define para encuestas de hogares CV alto de precisión en `[0,15)%`, moderado en `[15,30)%` y bajo en `[30,∞)%`. **Semaforización no equivale a una regla oficial de supresión por n=30.** El [XLSX oficial Q2](https://www.inegi.org.mx/rnm/index.php/catalog/1121/download/35892) es candidato a comparación: su enlace está identificado; sus celdas no fueron leídas en esta revisión.

Política conservadora propuesta del proyecto, adicional a los criterios de INEGI:

| Condición | Tratamiento propuesto |
| --- | --- |
| Diseño o universo no validado; sin SE/CI; denominador cero | `BLOCKED` o `UNKNOWN` según motivo; valor público null. |
| n válido <30, menos de 2 UPM contribuyentes o grados de libertad insuficientes | Suprimir cifra pública; conservar diagnóstico local. Umbral del proyecto, no certificación de confidencialidad ni norma INEGI. |
| CV <15%, controles superados | Candidato a `MEASURED`; publicar SE, intervalo y n. |
| 15% ≤ CV <30% | `REVIEW`, advertencia de precisión moderada, excluir rankings y afirmaciones de diferencia. |
| CV ≥30%, estimación en frontera o SE cero sospechoso | Cifra pública null y razón explícita; conservar estimación interna auditada. |

Propuesta operativa acordada con el integrador e implementada: intervalo nominal 90%, normal/Taylor para totales y medias, `estimate ± 1.6448536269514722 × SE`, identificado explícitamente como aproximación. Para proporciones interiores se usa logit-delta: `logit(p) ± z90 × SE(p)/(p(1−p))`, transformando ambos límites con logística. Fronteras 0/1 no reciben intervalos degenerados de certeza. Comprobar nivel y convención en el benchmark actual antes de afirmar equivalencia con INEGI. Guardar grados de libertad del diseño y diagnóstico de escasez; no recortar Wald a [0,100]. Una variante t/95% requiere otro método declarado. Guardar el intervalo analítico sin redondear; redondear solo presentación.

Ampliaciones necesarias del contrato antes de datos reales: `standard_error`, `variance_method`, `confidence_level`, `ci_lower`, `ci_upper`, `ci_method`, `design_df`, `n_psu_domain`, `n_strata_design`, `weighted_denominator`, `coverage_pct`, `suppression_reason`, versión/hash del diseño y universo. No guardar todos esos elementos únicamente en texto libre ni usar `coefficient_variation=null` como evidencia de precisión suficiente.

## 7. Comparabilidad temporal

2025Q1 ampliado y Q2–Q4 básico no son automáticamente incompatibles para variables armonizadas de SDEMT, pero el mapeo de preguntas económicas difiere. Cada par debe superar igualdad de población, código de campo, clasificación, geografía, definición de medida, tratamiento de no respuesta, factor trimestral, base de precios y método de estimación. Para 2026 y los periodos 2024 opcionales se requiere la misma prueba sobre paquetes reales.

La RNM 2025 describe rotación de 20% de viviendas por trimestre, con 80% persistente entre trimestres consecutivos. Por ello, una tendencia descriptiva comparable no habilita un test de muestras independientes. Para cambios:

```text
Var(θ̂_t − θ̂_s) = Var(θ̂_t) + Var(θ̂_s) − 2 Cov(θ̂_t, θ̂_s)
```

Si no hay una estimación defendible de covarianza de la muestra rotatoria, no publicar significancia, p-valores ni “creció con certeza”. Un agregado de cuatro trimestres tampoco contiene cuatro muestras independientes: no sumar ocupados como personas únicas ni dividir pesos entre cuatro y aplicar una varianza iid. Los ingresos nominales comparan montos nominales; no poder adquisitivo.

## 8. Reconciliación contra INEGI

Usar [tabulados del programa ENOE](https://www.inegi.org.mx/programas/enoe/15ymas/default.html#Tabulados) y sus [notas de revisión](https://inegi.org.mx/contenidos/programas/enoe/15ymas/doc/enoe_notas_tabulados.pdf). Conservar archivo, hoja, celda, edición, trimestre, unidad y precisión de redondeo. La comparación debe usar la misma revisión de factores y población que el microdato.

Secuencia de aceptación propuesta:

1. Nacional: población 15+, PEA, ocupados y desocupados, por sexo. Repetir una entidad; Jalisco, si se usa, tiene clave **14**, no 13. Comprobar clave con catálogo del paquete.
2. Informalidad del trabajo principal: cotejar total/porcentaje contra el indicador oficial equivalente, no sector informal ni informalidad de empleo secundario.
3. Distribución de ingreso: cotejar categorías `ING7C`, incluidos sin ingreso y no especificado. Solo comparar promedio si universo y tratamiento de no respuesta son idénticos.
4. SE, CV e intervalos de al menos nacional y una entidad contra el archivo oficial de precisiones del mismo trimestre. Coincidir en estimación puntual no valida la varianza.
5. Repetir en Q1 ampliado, Q2 básico y ambos lados del cambio de nombres 2025Q3; posteriormente 2026Q1/Q2 y cada periodo añadido.

Tolerancia: para una cifra tabulada redondeada a unidad u, aceptar únicamente el intervalo de redondeo ±u/2, más error flotante documentado. No aceptar porcentajes arbitrarios de discrepancia. Un tabulado en miles no permite exigir igualdad de personas individuales. Si no coincide, revisar universo/edad desconocida, edición de pesos, duplicados, condición de residencia y medida; no reajustar pesos para forzar coincidencia.

No se encontró en esta revisión un tabulado INEGI que valide directamente cada uno de los tres campos con exactamente este universo y promedio positivo. Las coincidencias nacionales validan márgenes; se necesitan además pruebas del cruce CMPE y un oráculo independiente para los dominios. No presentar un conteo de registros o una media sin pesos de la RNM como cifra oficial de población.

## 9. Casos de aceptación estadística

Los casos numéricos, de diseño y publicación se implementaron en `tests/test_survey.py`; los casos de codificación/universo y reconciliación de fuentes son aceptación pendiente del adaptador. La implementación no activa la fuente.

| Caso | Entrada/control | Resultado exigido |
| --- | --- | --- |
| Total por conglomerados | Dos estratos, dos UPM cada uno; aportes ponderados `[10,30]` y `[20,40]`. | Total 100; varianza 800; SE √800. |
| Razón Taylor | Un estrato, dos UPM, una persona por UPM, pesos 1, ingresos 2 y 4. | Media 3; varianza 1; SE 1. Caso numérico, no cumple criterio de publicación n. |
| Dominio escaso | Un estrato con dos UPM; indicador de dominio `[1,0]`, pesos 1. | Total 1; varianza 1. Filtrar primero produciría un diseño incorrecto. |
| Invariancia del peso | Multiplicar todos los pesos por c>0. | Total y SE total ×c; media, porcentaje, SE de razón y CV sin cambio. |
| Anidamiento | Igual código de UPM en estratos distintos. | Separarlos según identidad oficial; ningún cruce accidental. |
| Singleton real | Un estrato con una sola UPM en el diseño completo. | Fallo explícito; no varianza cero automática. |
| Sin observaciones | Campo ausente de la muestra. | Estado sin evidencia y cifra pública null; no “0 personas en México”. |
| Ingreso faltante | Cero físico con `ING7C=7`, blanco, código especial. | Excluir de monto válido; conservar no respuesta; no sumar ceros al promedio. |
| Cero confirmado | `ING7C=6`. | Contar en sin ingreso; fuera del promedio positivo. |
| Fronteras | CV exactamente 15/30; n exactamente 29/30; proporción 0/1. | Clasificación reproducible, límite inferior incluido correctamente; revisión de frontera. |
| Edad desconocida | EDA 97,98,99. | 97 adulto; 98/99 desconocidos según categoría, sin edad numérica inventada. |
| Educación | CS_P16 1/2/9; niveles 07/08/09. | Egreso desconocido no se trata como terminado; universos principal/ampliado separados. |
| Esquema y carrera | CSV con cero inicial; alias viejo/nuevo conflictivos; código no catalogado. | Preservar clave; conflictos bloquean; no asignación por ocupación ni aproximación de texto. |
| Población/factor | Mismo dato con FAC_MEN en lugar de FAC_TRI. | Rechazo antes de estimar. |
| Diferencia temporal | Dos trimestres rotatorios sin covarianza validada. | No test independiente ni significancia; descripción solamente si pasa comparabilidad. |

## 10. Condiciones abiertas para una implementación honesta

El estimador ya está implementado con fixtures. CMPE, encabezado y rango de ingreso de 2026Q2 están corroborados a nivel de metadatos; otros paquetes requieren la misma comprobación. La primera cifra real requiere cerrar: regla de edad no especificada para cada universo; estados de ingreso/horas; soporte de factores y estratos; comparación de precisión contra celdas oficiales; ampliación del contrato de salida. Resolver cada punto debe producir evidencia verificable y actualizar esta revisión, no reemplazar un desconocido con una convención implícita.

### Evidencia de implementación FINAL-04

Propiedad de este trabajo: `brujula/survey.py`, `tests/test_survey.py` y este documento. `SurveyDesign(weights, strata, psu)` conserva el marco completo; `total` y `ratio` devuelven estimación, varianza resumida como SE/CV/CI, soporte y estado. `estimate` es diagnóstico; **únicamente `value` es candidato a presentación**. Una estimación suprimida puede conservar SE/CI diagnósticos y nunca debe reaparecer a través de un fallback del renderer.

Los pesos cero requieren `allow_zero_weights=True` tras auditoría del llamador, no suman soporte y no pueden crear UPM de peso total cero. Identificadores vacíos, pesos negativos/no finitos, singleton de diseño, máscaras ambiguas, denominadores negativos o porcentajes fuera de rango fallan explícitamente. SE cero y CV indefinido en estimación cero se someten a revisión; no se clasifican como alta precisión automáticamente.

Verificación ejecutada: `.venv/Scripts/python.exe -m pytest tests/test_survey.py -q`, **24 pruebas aprobadas**. Incluye oráculos aritméticos independientes de la fórmula implementada, metamorfismo de escala, orden y UPM anidadas, límites CV/n y faltantes explícitos. El contraste contra R `survey` y contra precisiones oficiales sigue pendiente del integrador; no se ha afirmado equivalencia de producción.
