# Reportes estáticos

Estado: especificación de salida; implementación pendiente. El módulo de
reportes está ausente en el checkpoint auditado. No hay una demo verificada.

La API prevista `brujula.report.render_report(payload, output_dir)` debe generar `report.md`, `report.html` y figuras SVG/PNG desde un payload ya validado. No inicia un servidor, no descarga fuentes y no interpreta ausencias como cero.

Las barras deberán comparar el último periodo nacional disponible para cada métrica. La tendencia deberá mostrar ingreso mensual medio por campo; `null`, `UNKNOWN`, `BLOCKED` y pares no comparables rompen la línea. Cada figura imprime fuente, periodo, unidad, universo y advertencia de precisión.

El reporte deberá conservar el aviso **DATOS SINTÉTICOS ILUSTRATIVOS**, separa campo de estudio de ocupación, presenta frescura del periodo de negocio separada del timestamp de ejecución, y lista términos/licencias/estado de las fuentes. Si el payload está bloqueado, crea únicamente un reporte de bloqueo sin cifras ni gráficas.

La salida deberá ser determinista para el mismo payload, salvo los campos de receipt que pertenezcan al payload de entrada. Las URLs se muestran como texto en el Markdown; el HTML escapa todo contenido de payload y no ejecuta scripts.
