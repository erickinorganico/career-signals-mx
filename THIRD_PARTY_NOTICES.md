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
solo incluye código, contratos, catálogo y fixture propios; no redistribuye
las dependencias. El [resultado de pip-audit](docs/evidence/dependency-audit.json)
no encontró vulnerabilidades conocidas en ese conjunto durante la revisión.

El [catálogo de fuentes](docs/SOURCES.md) documenta condiciones de INEGI,
OLA/STPS, Data México e IMCO. La auditoría pública conserva enlaces y notas
metodológicas, no microdatos ENOE ni cifras OLA redistribuidas. No se incluye
código, consultas o datos propietarios de otras organizaciones.

Para una futura derivación de ENOE se debe conservar atribución a INEGI y al
producto específico, periodo, fecha de consulta/actualización, metadatos y una
nota de transformación que no implique aval de INEGI. La revisión debe hacerse
sobre los términos vigentes del dataset y snapshot seleccionado, no solo sobre
esta nota de planificación.
