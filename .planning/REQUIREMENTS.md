# Requirements: Brújula Laboral MX v1.0.0

**Defined:** 2026-09-22
**Core Value:** Entender y verificar conclusiones laborales útiles con universos, incertidumbre y evidencia explícitos.

## v1 Requirements

En este archivo v1 significa la entrega final 1.0.0. La demo sintética 0.1.0 es una línea histórica y no satisface estos requisitos.

### Fuentes y contrato

- [ ] **SRC-01**: El analista puede adquirir y resolver exactamente ocho ZIP oficiales ENOE de 2024-Q3 a 2026-Q2 mediante catálogo aprobado, SHA-256 fijado y caché verificada.
- [ ] **SRC-02**: Cada intento de adquisición deja recibo; errores de red, catálogo, contenido, hash y concurrencia no exponen un éxito previo como current vigente.
- [ ] **SRC-03**: Cada corte tiene inventario verificable de miembro SDEM, diccionario, catálogo de estudios, revisión, codificación y aliases geográficos; las correcciones de 2024 quedan identificadas.
- [ ] **SRC-04**: El lector puede consultar términos, atribución, fecha de adquisición y transformación; los registros individuales permanecen locales.
- [ ] **CTR-01**: Un contrato v2 estricto separa poblaciones, campos de estudios, ocupaciones, industrias, geografías, sexo registrado, periodos, métricas, evidencia y estado de precisión, sin relajar los gates sintéticos v1.
- [ ] **CTR-02**: La cohorte de profesionales con materias terminadas y el universo nacional tienen reglas de elegibilidad y denominadores explícitos; los posgrados, edades y campos desconocidos no se mezclan silenciosamente.

### Validez estadística

- [ ] **STAT-01**: El analista obtiene totales, proporciones y medias usando FAC_TRI, EST_D_TRI y UPM sobre el diseño completo, antes de restringir dominios.
- [ ] **STAT-02**: Cada estimación informa n observado, UPM, estratos, grados de libertad, error estándar, IC90, CV, política de singleton y método; cualquier aproximación propia se distingue de la precisión oficial.
- [ ] **STAT-03**: Valores con n<30, menos de dos UPM contribuyentes, CV>=30, denominador nulo o precisión degenerada quedan suprimidos con causa; n no se presenta como tamaño muestral efectivo.
- [ ] **STAT-04**: Python reproduce puntos y errores estándar de un oráculo R survey independiente en datos reales y controles analíticos; la comparación oficial documenta discrepancias sin ajustar tolerancias para ocultarlas.
- [ ] **STAT-05**: Los agregados nacionales y al menos una entidad se reconcilian con tablas oficiales de edición y universo compatibles, incluyendo una comparación explícita de precisión oficial.
- [ ] **STAT-06**: Las métricas de empleo, participación, desocupación, ingreso positivo conocido, cobertura de ingreso, informalidad del trabajo principal, composición por sexo y condiciones laborales verificadas tienen numerador, denominador, unidad, no respuesta y reglas de sentinelas comprobados.

### Investigación y análisis

- [ ] **ANA-01**: El lector dispone de perfiles detallados para Derecho, Comunicación y periodismo y Ciencias políticas, más contexto de los demás campos profesionales identificables y la cohorte total.
- [ ] **ANA-02**: El lector puede seguir los ocho cortes trimestrales nacionales con cambios descriptivos; no se suman como personas distintas ni se declara significancia suponiendo independencia.
- [ ] **ANA-03**: El ledger de comparación bloquea deltas por cambio de fuente, universo, geografía, métrica, concepto, base de precios, clasificación o método, y por extremos suprimidos.
- [ ] **ANA-04**: El lector consulta diferencias por sexo registrado y cobertura por entidad donde la precisión lo permite, con ausencias y supresiones visibles.
- [ ] **ANA-05**: El informe muestra cobertura muestral y de respuesta, exclusiones y limitaciones por periodo/campo, incluyendo edad y campo desconocidos y no respuesta de ingreso.
- [ ] **ANA-06**: Cada hallazgo tiene identificador y referencias exactas a estimaciones, fuente y método; el gate rechaza prosa causal, cantidades nuevas y recomendaciones personales sin evidencia.

### Publicación editorial y operación

- [ ] **PUB-01**: El lector recibe un informe en español organizado por preguntas, con apertura, hasta tres hallazgos sustentados, contexto nacional, perfiles, evolución, territorio, límites, métodos y fuentes.
- [ ] **PUB-02**: El mismo run validado produce HTML offline, Markdown equivalente y PDF imprimible; no requiere credenciales, servidor, JavaScript ni recursos de red.
- [ ] **PUB-03**: Figuras SVG/PNG y tablas semánticas muestran unidades, incertidumbre, fuente, universo y estados; son legibles en impresión, móvil y zoom al 200%.
- [ ] **PUB-04**: CSV, Parquet y DuckDB públicos preservan dimensiones, null, precisión y provenance, con diccionario de datos y claves que enlazan figuras y claims.
- [ ] **PUB-05**: Una proyección pública única impide que estimaciones internas suprimidas, errores estándar o intervalos que revelen esas cifras reaparezcan en cualquier formato o texto alternativo.
- [ ] **OPS-01**: El analista puede ejecutar adquisición/refresco y replay offline con CLI documentada; el replay reproduce el contenido numérico de los mismos snapshots sin confundir timestamps de ejecución con determinismo de datos.
- [ ] **OPS-02**: El pipeline sella cada run con hashes, recibo final y manifiesto antes de actualizar current; fallo o crash impiden resolver la publicación como vigente y conservan el historial.
- [ ] **OPS-03**: Los consumidores verifican manifiesto, hashes, catálogo y estado de las adquisiciones requeridas antes de abrir reportes o exports; fallos posteriores de adquisición invalidan la vista current dependiente.

### Entrega y verificación

- [ ] **REL-01**: README en español/inglés, scope, PRD, arquitectura, método, instalación, comandos, guía de actualización, contribución y citación describen capacidades reales y límites actuales.
- [ ] **REL-02**: Instalaciones limpias y pruebas en Windows/Ubuntu verifican fixtures sin producción; el bundle real recibe revisión independiente numérica, conceptual y visual, además de replay offline.
- [ ] **REL-03**: El paquete público pasa revisión de secretos, licencias, atribución y ausencia de microdatos; solo artefactos validados se publican en erickinorganico/career-signals-mx.
- [ ] **REL-04**: Un release 1.0.0 enlaza código, informe, figuras, agregados, manifiesto y evidencia de aceptación; la versión final no se declara completa con gates materiales pendientes.
- [ ] **GSD-01**: Requisitos, fases, planes revisados, ejecución, verificaciones, revisión de código y auditoría final quedan trazables en GSD; las recomendaciones se siguen conservando las autorizaciones y restricciones del proyecto.

## Future Requirements

Ninguna función necesaria para esta entrega se difiere por conveniencia. Nuevas fuentes, deflactación con INPC y extensiones de país requieren contratos y revisión de comparabilidad propios; no forman parte de las promesas de este hito.

## Out of Scope

| Feature | Reason |
|---------|--------|
| Aplicación, frontend, backend o hosting | Entrega autorizada de investigación local y documentos estáticos |
| APIs pagadas, LLM externos o mensajes a terceros | Fuera de autorización y presupuesto |
| Causalidad, ranking universal o asesoría individual | No sustentados por el diseño de esta investigación |
| Microdatos individuales públicos | Publicación limitada a agregados y evidencia redistribuible |
| Agrupar trimestres como muestra independiente | Panel rotatorio con dependencia |

## Traceability

Pendiente de asignación por gsd-roadmapper. Todos los requisitos están pendientes de verificación integral; los módulos y descargas existentes son evidencia de avance parcial.

**Coverage:** 31 requisitos; deben asignarse exactamente una vez a las fases del roadmap.

---
*Last updated: 2026-09-22 after research and explicit user authorization to follow GSD recommendations.*
