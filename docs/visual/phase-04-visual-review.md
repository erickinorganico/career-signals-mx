# Revisión visual del informe público v1.0.0

Se revisó una edición local del paquete público validado de la ENOE, no los microdatos. El paquete de análisis usado fue `.cache/research/phase4-analysis/analysis.json`, SHA-256 `71d9fb7d6ceb20cff39a1a10f8428bcb239629e2e723b6e001816bd6d564bce3`. La edición cubre 2024-Q3 a 2026-Q2 y se generó el 2026-09-23 UTC. Los números y las afirmaciones provienen del modelo de publicación validado; la maquetación no calcula resultados nuevos.

## Alcance comprobado

El mismo modelo produjo Markdown, HTML, nueve pares SVG/PNG y PDF A4. Los 446 registros, 141 comparaciones y 38 afirmaciones usados en la edición tienen 625 identificadores canónicos distintos y localizables en los tres documentos. El PDF final tiene 97 páginas, texto español extraíble y fuentes DejaVu incrustadas. La comparación de inventario de claves no encontró identificadores faltantes o adicionales, ni IDs HTML duplicados. Los 96 cambios de las series focales aparecen impresos con periodos, cambio absoluto, fuentes de ambos extremos y referencia completa en el apéndice. La unión de puntos de los paneles impresos conserva exactamente los puntos de las nueve figuras declaradas.

Los archivos examinados tienen estas huellas SHA-256:

| Archivo local | SHA-256 |
| --- | --- |
| `report.html` | `8113128bd78f38f2ad4cab03663543b019d712de9149f1618c8cb94e8e907afd` |
| `report.md` | `1492abdc73309e5acc3191ce7e15242223411d71a2ab52375eef9aa662dfc3cc` |
| `report.pdf` | `438ac478296fc23c29d04eecb47b4d3bf9bff6ff9815c3cd9781652ac95c1721` |

## Lectura de página y figuras

Se rasterizaron páginas A4 reales de apertura, perfiles, comparaciones, sexo registrado, entidades y otros campos. Los márgenes son 19 mm arriba, 18 mm a los lados y 20 mm abajo; el cuerpo es de 10,5 pt con interlínea 1,4. Las tablas impresas usan cinco columnas y 8,2 pt, conservan tokens numéricos íntegros, repiten encabezados y muestran universo, estado, motivo, muestra, fuente y referencia. Los identificadores completos del apéndice son buscables y permanecen en una línea. La tabla de comparaciones, inicialmente oculta en impresión por su contenedor de pantalla, fue añadida expresamente al PDF; no se imprimió el libro completo de 4.209 comparaciones.

Las figuras exportadas por separado muestran unidad en español, sexo registrado con su etiqueta y código, periodo y fuente INEGI ENOE. Sus intervalos IC90 se atribuyen al cálculo aproximado del proyecto, sin presentar precisión oficial. Las figuras con unidades o universos distintos se dividen en paneles; un valor no disponible no se coloca en cero. Los paneles A4 se dibujan a 6,8 pulgadas de ancho físico, con títulos envueltos y pies dentro del área. La figura de 115 campos conserva todos sus códigos y se divide en paneles impresos de hasta 16 filas; la de entidades contiene los 32 puntos declarados. Se verificó visualmente el archivo PNG de sexo registrado, además del SVG y el PDF. En la página A4 32 se inspeccionaron las filas de ingreso a resolución de 1600 px: los números permanecen completos, las unidades nominales pasan a otra línea y no invaden la columna de estado.

La primera lectura de A4 detectó tablas de 11 columnas ilegibles, rótulos de gráfico demasiado pequeños, títulos recortados, una etiqueta de valor ausente por fuera del eje y páginas casi vacías por saltos forzados. La versión examinada usa cinco columnas, ancho físico de impresión, títulos envueltos, límites categóricos que incluyen filas nulas y paginación natural con artículos breves juntos. El contraste calculado del texto principal `#172B3A` sobre blanco es 14,55:1 y del texto secundario `#405464` es 7,86:1.

## Navegador y límites

La validación de navegador se efectuó sobre archivos locales, sin solicitudes de red. Se revisaron escritorio de 1440 px, móvil de 390 px y zoom nativo de Chrome al 200 % (ancho interior 720 px), con inspección de desplazamiento de figuras y tablas, portada, evolución y evidencia. El ancho del documento coincidió con el viewport en las tres vistas: 1440/1440, 390/390 y 720/720 px. Los gráficos anchos conservan desplazamiento propio. Los enlaces largos de evidencia y huellas de fuentes permiten ruptura visual en pantalla; los IDs del apéndice impreso permanecen íntegros. La última corrección afectó solo las celdas de la tabla alternativa oculta en pantalla y visible en impresión; se reutilizó el control de navegador de la versión anterior con la misma tabla de pantalla y CSS de pantalla. No se afirma certificación PDF/UA ni accesibilidad total: se verificaron texto extraíble, títulos y descripciones SVG, texto alternativo con alcance y valores públicos, tablas semánticas, foco en regiones desplazables y contraste de colores.

Los archivos de control locales quedan en `.cache/research/phase4-report-review/` y no se publican con el producto. El informe conserva enlaces a archivos oficiales de INEGI y su atribución; no consulta la red al abrir o imprimir la edición local.
