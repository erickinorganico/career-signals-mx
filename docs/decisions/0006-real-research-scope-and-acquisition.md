# ADR-0006 — Investigación real y adquisición ENOE

Fecha: 2026-09-22 local. Estado: adquisición aprobada; publicación numérica
sujeta a validación estadística. Reemplaza la restricción de entrega únicamente
sintética para la versión final solicitada expresamente por el titular.

## Decisión y autoridad

El titular pide ir más allá del MVP, revisar repositorios similares y entregar
la versión final. La autorización previa incluye trabajo local, dependencias
gratuitas, subagentes y publicación del proyecto en el repositorio GitHub
designado. El integrador registra esta decisión después de revisar las fuentes
primarias; una propuesta de subagente no activa datos por sí misma.

Se autoriza adquirir ocho paquetes ENOE publicados por INEGI, 2024-Q3 a
2026-Q2, enumerados en [el registro exacto](../../data/catalog/enoe-snapshots.json).
La consulta de metadatos y la adquisición local permiten validar la estadística;
no equivalen a aceptar resultados numéricos ni publicar registros de personas.

## Evidencia primaria

- [Programa y microdatos ENOE](https://www.inegi.org.mx/programas/enoe/15ymas/).
- [Ficha 2026-Q2](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=3946334)
  y [ficha 2026-Q1](https://www.inegi.org.mx/app/descarga/ficha.html?ag=0&f=csv&tit=3634157).
- [Términos de libre uso INEGI](https://www.inegi.org.mx/inegi/terminos.html):
  permiten transformación y difusión con créditos, metadatos conservados y
  aviso de elaboración propia, sin atribuir el análisis ni aval al Instituto.
- [Configuración pública del programa](https://www.inegi.org.mx/programas/enoe/15ymas/data/pestana/pestanadata.js)
  anuncia renombre de claves geográficas desde 2025-Q3 y adición de CVEGEO.

Las URLs de ZIP proceden del catálogo público que utiliza la página de INEGI;
no se activan URLs adivinadas, otros hosts ni fuentes comerciales. Se conservan
los paquetes sin modificar y se registran SHA-256, tamaño, instante y resultado
de cada intento. Se verifica cada caché antes de reutilizarla. Los archivos raw
y registros individuales quedan fuera de Git y del release editorial.

## Gates posteriores

El adapter debe verificar diccionario, códigos de educación/carrera, universo,
pesos, estratos, UPM, no respuesta y comparabilidad. La publicación necesita
varianza de diseño, política de precisión, contraste con cifras oficiales y
revisión independiente. Si falla una descarga o validación, el intento queda
registrado y la actualización actual no hereda la vigencia de un éxito previo.

El [plan final](../FINAL-RELEASE-PLAN.md) establece la entrega real. Las fuentes
OLA, IMCO y Data México no quedan activadas para redistribución de cifras por
esta decisión. Se mantiene la exclusión de frontend, backend, hosting e
inferencia pagada.
