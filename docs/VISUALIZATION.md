# Reportes estáticos

Estado: implementación local offline. El módulo `brujula.report` genera
documentos estáticos y figuras desde un payload ya validado; no hay servidor ni
dependencia de navegador.

La API `brujula.report.render_report(payload, output_dir)` genera `report.md`,
`report.html` y pares SVG/PNG deterministas. Su resultado contiene rutas
relativas: `{markdown:"report.md", html:"report.html", charts:[...]}`. No
inicia un servidor, no descarga fuentes y no interpreta ausencias como cero.

Las barras usan el último periodo nacional declarado por métrica. Conservan
los campos sin valor con la etiqueta «Sin dato», sin barras de altura cero ni
reemplazo por un trimestre anterior. La
tendencia muestra ingreso mensual medio por campo y geografía; `null`,
`UNKNOWN`, `BLOCKED` y pares sin una comparación declarada compatible rompen la
línea. Cada figura muestra fuente, periodo, geografía, unidad, universo,
precisión y el aviso persistente **DATOS SINTÉTICOS ILUSTRATIVOS**. Cada figura
tiene una tabla equivalente en Markdown y HTML.

El reporte conserva el aviso **DATOS SINTÉTICOS ILUSTRATIVOS**, separa campo de
estudio de ocupación, presenta frescura del periodo de negocio separada del
timestamp de ejecución, y lista términos/licencias/estado de las fuentes. Si el
payload está bloqueado, crea únicamente un diagnóstico sin cifras, tablas de
datos ni gráficas.

La salida es determinista para el mismo payload, salvo los campos de receipt
que pertenezcan al payload de entrada. Matplotlib usa el backend no interactivo
`Agg`, un `svg.hashsalt` fijo y metadatos estables. Las URLs se muestran como
texto en el Markdown; el HTML escapa todo contenido de payload y no emite
scripts, estilos remotos ni recursos de red.
