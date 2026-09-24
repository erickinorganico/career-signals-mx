# Versión final de investigación — 1.0.0

Estado: en ejecución. La instrucción del titular del 22 de septiembre de 2026
rechaza el MVP como entrega suficiente y solicita una versión final, precedida
por revisión de proyectos comparables. Este mandato amplía la entrega vigente;
v0.1.0 queda como demostración técnica histórica, no como producto terminado.

## Resultado que debe recibir el lector

Una investigación reproducible sobre formación y trabajo en México con datos
oficiales reales, perfiles de campos de estudio, contexto nacional, tendencias,
incertidumbre y brechas explícitas. El informe debe poder leerse, imprimirse,
citarse y compartirse sin instalar el repositorio. El paquete técnico permite
reconstruir cada cifra y auditar las decisiones metodológicas.

Se mantienen los límites de no construir una aplicación o servicio y de no usar
inferencia pagada. El producto editorial será HTML offline, Markdown, figuras,
tablas descargables y PDF. No se amplía a LATAM sin metodología por país.

## Referencias y decisiones de producto

- [Repositorios comparables](research/COMPARABLE-REPOSITORIES.md): aprender de
  pipelines laborales y bibliotecas estadísticas, sin copiar software de
  licencia incompatible ni adoptar tratamientos de faltantes sin revisión.
- [Auditoría de brechas](research/PRODUCT-GAP-AUDIT.md): organizar la publicación
  por preguntas, hallazgos, precisión, perfiles y método, no por un volcado JSON.
- La revisión estadística ENOE debe preceder a publicar estimaciones; un build
  exitoso no acredita una conclusión sustantiva.

## Cobertura y criterio de suficiencia

1. Ocho trimestres oficiales recientes, objetivo 2024-Q3 a 2026-Q2, comprobados
   en el catálogo INEGI. Los cambios de archivo y clasificación se versionan.
2. Población nacional como contexto y personas con educación profesional
   terminada como universo de perfiles. Derecho, Comunicación y periodismo y
   Ciencias políticas reciben perfiles detallados; el contexto comparativo
   abarca los campos profesionales identificables en la clasificación oficial.
3. Ocupación, participación, desocupación, ingreso monetario, informalidad,
   composición por sexo y condiciones laborales, cada una con denominador y
   no respuesta explícitos. Una métrica solo entra si su diccionario y
   estimador quedan verificados. Los conteos no representan vacantes.
4. Análisis territorial y por sexo donde la muestra lo permita, con supresión
   de resultados imprecisos visible; no ampliar cobertura rellenando ceros.
5. Estimadores con pesos, estratos y UPM, tamaño muestral observado, error estándar,
   intervalos y CV. La política de precisión es propia y debe ser comprobable.
6. Ocho trimestres no se concatenan como personas distintas: el panel rota y
   las muestras se superponen. Las tendencias son cortes transversales; no se
   declara significancia de cambios con una hipótesis de independencia falsa.

## Tareas y aceptación

| ID | Responsabilidad / archivos | Dependencia | Aceptación y verificación |
|---|---|---|---|
| FINAL-01 | Principal: alcance, catálogo de snapshots, decisión de adquisición | Investigación primaria | URLs publicadas, términos y metadatos preservados; separación adquirir/estimar/publicar; recibo por intento |
| FINAL-02 | Luna: `brujula/acquisition.py`, `tests/test_acquisition.py` | FINAL-01 | Allowlist, límites de tamaño, ZIP seguro, hashes y caché verificada; fallos trazables; pruebas offline |
| FINAL-03 | Revisor estadístico: método ENOE y oráculos independientes | Diccionarios oficiales | Variables/códigos exactos, fórmulas, dominios y singleton PSU explícitos; benchmarks oficiales identificados |
| FINAL-04 | Estadística: `brujula/survey.py`, `tests/test_survey.py` | FINAL-03 | Totales/ratios y varianza de diseño probados contra ejemplos calculables e implementación independiente |
| FINAL-05 | Principal: adaptador ENOE, contratos v2 y agregados | FINAL-02–04 | Ocho snapshots verificables; clasificación y universo correctos; cifras nacionales contrastadas con INEGI |
| FINAL-06 | Terra: publicación editorial estática y tests | Contrato v2 | Resumen, contexto, perfiles, tendencias, precisión y fuentes; HTML/PDF legibles, accesibles y sin red |
| FINAL-07 | Principal: flujo CLI, exports y actualización | FINAL-05–06 | Un flujo de refresh y otro de replay offline; DuckDB/CSV/Parquet; current inválido ante fallo |
| FINAL-08 | Revisión independiente y principal: release final | Todas | Auditoría numérica, conceptual, visual, privacidad/licencias; CI, replay y assets reales publicados en GitHub |

Cada asignación concreta divide estas áreas en cambios acotados con ownership;
los agentes no escriben en módulos compartidos sin contrato previo. Los tests
sintéticos siguen siendo controles de regresión y no aparecen como resultados
laborales en la portada final.

## Qué significa terminado

- El lector puede responder preguntas reales sobre los campos y las condiciones
  laborales usando el informe, localizar el universo y reconocer incertidumbre.
- Cada número y figura se vincula a estimación, snapshot/hash, método y fuente.
- El repositorio entrega datos agregados reutilizables, informe completo,
  diccionario, instalación, comandos y una guía de actualización probados.
- Las estimaciones se contrastan contra tabulados oficiales y un oráculo
  estadístico independiente, además de las pruebas de software.
- Publicación final revisada en `erickinorganico/career-signals-mx`; no se
  distribuyen registros de personas en el paquete editorial.
- Toda limitación material figura junto al resultado afectado. Si una fuente
  impide cumplir una parte esencial, se reporta ese bloqueo concreto sin llamar
  “final” a una maqueta o sustituir silenciosamente los datos por simulaciones.
