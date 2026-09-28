# Sitio de resultados

El propietario autorizó el 28 de septiembre de 2026 una portada editorial
estática en GitHub Pages y un README visual para la investigación publicada.
Esta ampliación de presentación no reabre el análisis ni modifica el tag
`v1.0.0`, sus cifras o sus archivos de entrega.

URL: https://erickinorganico.github.io/career-signals-mx/

`site/` contiene la portada y sus estilos. `scripts/build_site.py` descarga
el ZIP de investigación del release 1.0.0 y comprueba su tamaño, SHA-256 y
miembros contra `docs/evidence/phase-05-release-inventory.json`. Distribuye
los archivos de investigación auditados junto con la portada; no captura
fuentes nuevas ni publica microdatos. Las fuentes tipográficas son locales.

```powershell
.venv/Scripts/python.exe scripts/build_site.py --output .cache/pages
# Para reutilizar una descarga verificada:
.venv/Scripts/python.exe scripts/build_site.py --archive .cache/release-v1/final-candidate-v6/assets/brujula-laboral-mx-investigacion.zip --output .cache/pages
```

El workflow `pages.yml` construye en las solicitudes de cambio y publica
solo desde `main`. Si falla la validación, no se ejecuta el despliegue.
El sitio sigue identificado como la edición histórica 1.0.0; su despliegue
no equivale a una actualización de la ENOE. No tiene backend, formularios,
analítica de visitantes ni dependencias JavaScript.

Las imágenes del README son copias exactas de las figuras de la publicación.
La portada mantiene visibles el periodo, los universos, el ingreso condicionado
y la precisión no oficial `REVIEW`. El informe completo conserva las tablas,
intervalos, fuentes y evidencia. Código y materiales externos mantienen sus
licencias y atribuciones respectivas.

## Verificación de presentación

La portada se revisó en navegador a 1440 × 1000 y 390 × 844 píxeles:
encabezado, resultados, navegación y gráfica territorial. No se observó
desbordamiento horizontal; las tres instancias de imagen cargaron.
El README enlaza tres figuras PNG copiadas sin cambios del informe sellado.
El constructor comprueba destinos y anclas locales antes de crear el artefacto.
La publicación pública se puede consultar en el historial del workflow
[Publish research site](https://github.com/erickinorganico/career-signals-mx/actions/workflows/pages.yml).
