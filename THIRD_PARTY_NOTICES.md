# Licencias y atribución

El código, documentación y fixtures originales de este repositorio se publican
bajo [MIT](LICENSE). Los paquetes instalados no se redistribuyen aquí:
`.venv`, cachés y artefactos de ejecución están excluidos de Git.

Dependencias directas declaradas: Python, DuckDB, jsonschema y Matplotlib;
pytest se utiliza para verificación. Las versiones fijadas están en
[pyproject.toml](pyproject.toml) y [requirements.txt](requirements.txt).
Sus licencias propias no se reemplazan por la licencia MIT del proyecto.
Antes de empaquetar binarios o distribuir entornos, el gate de release deberá
inventariar también dependencias transitivas y conservar sus avisos.

Para 0.1.0 se revisaron los metadatos de los 23 paquetes fijados, sin entradas
carentes de información de licencia. El [inventario](docs/evidence/dependency-licenses.json)
conserva expresiones SPDX o metadatos/clasificadores del paquete instalado.
Los avisos completos permanecen con cada distribución. El wheel del proyecto
incluye también recursos authored y cuatro fuentes DejaVu con su licencia
íntegra; no redistribuye los paquetes Python dependientes. El
[resultado histórico de pip-audit](docs/evidence/dependency-audit.json)
no encontró vulnerabilidades conocidas en el conjunto de 0.1.0 revisado
entonces; no constituye una auditoría nueva de esta edición.

El [catálogo de fuentes](docs/SOURCES.md) documenta condiciones de INEGI,
OLA/STPS, Data México e IMCO. La auditoría pública conserva enlaces y notas
metodológicas, no microdatos ENOE ni cifras OLA redistribuidas. No se incluye
código, consultas o datos propietarios de otras organizaciones.

Para una futura derivación de ENOE se debe conservar atribución a INEGI y al
producto específico, periodo, fecha de consulta/actualización, metadatos y una
nota de transformación que no implique aval de INEGI. La revisión debe hacerse
sobre los términos vigentes del dataset y snapshot seleccionado, no solo sobre
esta nota de planificación.

La prueba y auditoría del PDF usan `pypdf==6.19.0` (BSD-3-Clause, copyright
de sus contribuyentes); no forma parte del motor de generación de PDF.
Identidad, wheel y SHA-256 revisados: [auditoría de dependencia](docs/evidence/phase-04-pdf-audit-dependency.json).
El PDF se genera con `weasyprint==70.0`, declarado como extra `pdf`; se aplican
las licencias y avisos de su propia distribución y dependencias nativas.
Los cuatro archivos DejaVu TTF se distribuyen con su `LICENSE_DEJAVU` completo
en cada publicación y wheel.
