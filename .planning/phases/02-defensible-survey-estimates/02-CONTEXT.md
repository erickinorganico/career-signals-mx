# Phase 2: Defensible Survey Estimates - Context

**Gathered:** 2026-09-22  
**Status:** Research complete; planning follows verified Phase 1 interfaces.  
**Decision authority:** El usuario pidió continuar autónomamente y seguir las recomendaciones de GSD. Se adoptan las decisiones metodológicas recomendadas dentro del alcance aprobado y se documentan sus límites; no se necesita una elección adicional para cada detalle de implementación.

<domain>
## Phase Boundary

Convertir los ocho paquetes oficiales verificados en estimaciones reproducibles y auditables. Esta fase cierra el adaptador, las definiciones de métricas, los controles de precisión y las conciliaciones con R y tablas oficiales. Los perfiles editoriales y las comparaciones temporales pertenecen a la fase 3; la publicación multiformato y su CLI integrada pertenecen a la fase 4.
</domain>

<decisions>
## Implementation Decisions

### Marco, poblaciones y códigos
- Construir el diseño con **todas** las personas de respuesta y residencia válidas, antes de restringir edad, estudios, entidad, sexo u ocupación. Conservar UPM con contribución nula al dominio.
- Reutilizar las dos poblaciones y los códigos CMPE de la fase 1. Contexto nacional operativo 15..98, aclarando 98 como edad desconocida; cohorte profesional 15..97 con materias terminadas. Los campos desconocidos permanecen desconocidos y sus exclusiones se reportan.
- Verificar los ocho hashes, el miembro exacto y los diccionarios antes de interpretar filas. La auditoría de lexemas encontró blancos y relleno ASCII U+0020; registrar esas frecuencias antes de normalizar exclusivamente ese carácter. No aceptar conversiones difusas, decimales, valores no finitos o códigos nuevos sin explicación.
- Separar PEA (`CLASE1=1`) de ocupados (`CLASE2=1`). La auditoría inicial confundió estos dominios; la corrección y el segundo barrido completo pasaron en los ocho cortes. El adaptador debe conservar un control de regresión que impida repetir esa confusión.
- No serializar filas individuales en git, fixtures públicos, logs ni paquetes de publicación. Los oráculos individuales temporales quedan ignorados localmente; sus resultados públicos son agregados.

### Estimación y precisión
- Taylor por UPM última con FAC_TRI, EST_D_TRI y UPM. Mantener el motor existente y controles analíticos independientes.
- `singleton_policy="fail"` sigue siendo el valor predeterminado del motor. El adaptador de estos cortes selecciona explícitamente `adjust`, equivalente al oráculo R, y declara aproximación propia `REVIEW`, `official_precision=false`. El valor puede mostrarse si cumple los demás gates; la etiqueta REVIEW no equivale por sí sola a supresión.
- Totales y medias: IC90 normal; proporciones: IC90 logit delta cuando no son degeneradas. Documentar el método exacto y evitar alegar intervalos oficiales.
- Mostrar n observado del denominador, UPM y estratos contribuyentes, UPM/estratos del diseño completo, grados de libertad y política de singleton. Ninguno se etiqueta como tamaño muestral efectivo.
- Suprimir valor público con n<30, menos de dos UPM contribuyentes, CV>=30%, denominador cero o precisión degenerada. Proporciones 0/100 y SE cero mantienen diagnóstico interno pero no una falsa certeza pública. CV 15..<30 conserva valor con advertencia REVIEW.
- La proyección v2 es la única frontera pública: conserva cobertura observada y oculta estimación, denominadores ponderados e intervalos que revelen una celda suprimida.

### Métricas completas y denominadores
- Totales de población, ocupados, PEA y desocupados; tasas de empleo, participación y desocupación con denominadores propios.
- Ingreso mensual nominal positivo conocido: ING7C 1..5, INGOCUP 1..999998, ocupado. Cero y 999999 no se convierten en salario observado. Mostrar cobertura, ingreso no especificado y sin ingreso por separado.
- Informalidad del trabajo principal con EMP_PPAL, composición por sexo registrado y posición en la ocupación con categorías oficiales y exclusiones explícitas. No denominarlas informalidad del sector o TIL1.
- Subocupación: contar `SUB_O=1` dentro de ocupados y dividir por ocupados; no usar todos los residentes ni transformar el código fuente 0 en una etiqueta universal de no subocupado. Los ocho catálogos y cruces SUB_O×CLASE2 están auditados.
- Horas semanales conocidas: incluir HRSOCUP 1..168 con DUR9C 2..8 y cero observado con DUR9C=1 (ausencia temporal); excluir DUR9C=9 (no especificado) aunque su campo físico sea cero. Nombrar explícitamente la inclusión de ausentes y publicar cobertura de horas conocidas entre ocupados. Los ocho cruces auditados respaldan esta separación; cualquier combinación inesperada queda fuera con diagnóstico, nunca se infiere un cero observado.
- Las definiciones son datos versionados: numerador, denominador, unidad, base de precios, sentinelas y referencias a diccionario. Conservar campo de estudios, ocupación, industria y geografía separados.

### Aceptación independiente
- Regenerar el oráculo de 2026-Q2 con la cohorte final de edad conocida: el prototipo de Derecho incluía 98 y no satisface esta aceptación.
- Usar R survey local con opciones explícitas `survey.lonely.psu="adjust"`, `survey.adjust.domain.lonely=FALSE`, diseño completo y mismas máscaras. Cubrir contexto nacional, los tres campos focales, una entidad, totales, proporciones e ingreso.
- Declarar antes de ejecutar tolerancia Python/R `rtol=1e-10`, `atol=1e-8` para puntos y errores estándar. Registrar diferencias crudas firmadas y rechazar discrepancias, sin adaptar tolerancias a los resultados.
- Conciliar la edición oficial 2025-Q2 nacional y Baja California: seis totales exactos y tasas dentro del intervalo de redondeo oficial de cuatro decimales. Conservar también diferencia cruda y resultado de la prueba estricta original.
- Comparar errores estándar oficiales sin afirmar igualdad: existe una discrepancia documentada (hasta aproximadamente -0.3715% relativo en el total nacional de población). La política `adjust` es reproducible e independiente pero no reproduce una eventual reasignación oficial de estratos no publicada. Conservar el ledger completo y la limitación; no fingir un mapa de colapso oficial ni subir tolerancias para borrar diferencias.
- Publicar las diferencias como evidencia del método propio. Que una precisión sea aproximada no impide un resultado útil y honestamente etiquetado si pasa los gates de estabilidad, oráculo y soporte.

### Agent discretion
- Dividir implementación en planes que puedan verificarse de forma independiente; ejecutar secuencialmente en el checkout compartido.
- Reutilizar prototipos comprobados, pero trasladar su lógica necesaria a código versionado y pruebas reproducibles. Los archivos ignorados de investigación no pueden ser la única implementación del producto.
- Agregar NumPy como dependencia directa porque el estimador ya lo importa. Usar uv y caché local; no introducir paquetes o servicios de pago.
</decisions>

<code_context>
## Existing Code Insights

- `brujula/source_inventory.py` resuelve inventarios completos de ocho paquetes sin emitir personas.
- `brujula/populations.py` y `brujula/research_contract.py` serán interfaces verificadas al concluir la fase 1; inspeccionar sus firmas reales antes de planear integración.
- `brujula/survey.py` y sus pruebas ya cubren totales, razones, dominios, precisión y singleton adjust. Falta estrato contribuyente y adaptación de variables reales.
- `.cache/research/` contiene auditorías agregadas, prototipos del oráculo, libro oficial y comprobaciones. R y paquetes están disponibles localmente; no forman parte del runtime Python público.
- El v1 sintético conserva contrato y comportamiento; no usarlo para demostrar aceptación de resultados reales.
</code_context>

<deferred>
## Deferred Ideas

La fase 3 consume estimaciones aceptadas para perfiles, cobertura territorial, cambios descriptivos y claims. La fase 4 integra CLI, pipeline e informes. No se difiere ninguna métrica comprometida por conveniencia, y no se agrega frontend ni servicio.
</deferred>
