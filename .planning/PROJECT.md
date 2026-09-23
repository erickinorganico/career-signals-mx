# Brújula Laboral MX

## What This Is

Un proyecto de investigación reproducible sobre el trabajo en México, destinado a lectores que quieren entender resultados laborales por campo de estudios y a analistas que necesitan verificarlos. La entrega final es una publicación editorial en español con datos oficiales ENOE, incertidumbre visible, tablas reutilizables y un pipeline local que permite reconstruir cada cifra.

El usuario rechazó expresamente la entrega sintética v0.1.0 como producto final. Este hito entrega investigación real; conservar una demo funcional no satisface su objetivo.

## Core Value

Que una persona pueda entender y verificar una conclusión laboral útil sin confundir muestras pequeñas, datos faltantes, carreras, ocupaciones o diferencias metodológicas.

## Requirements

### Validated

- Pipeline sintético local con recibos, manifiestos, hashes y fallo que invalida current — v0.1.0, evidencia técnica en GitHub; no equivale a adopción o utilidad validada con lectores.
- Exportación CSV, Parquet, DuckDB y reportes estáticos sintéticos — v0.1.0.
- Publicación autorizada y acceso verificado a erickinorganico/career-signals-mx — repositorio existente.
- Ocho snapshots ENOE con inventario offline, metadatos, poblaciones explícitas y contrato v2 interno/público — Phase 1, 27/27 criterios y seis prohibiciones comprobadas; cierre canónico GSD sin advertencias. Ver `01-VERIFICATION.md` y `01-VALIDATION.md`.

### Active

- [x] Adquirir y versionar ocho cortes ENOE oficiales, 2024-Q3 a 2026-Q2, con licencia, metadatos y recibos verificables — Phase 1; microdatos conservados localmente.
- [ ] Estimar por diseño complejo, contrastar resultados con INEGI y R, y suprimir cifras que no cumplan la política de precisión.
- [ ] Publicar contexto nacional y egresados profesionales, con foco en Derecho, Comunicación y Ciencias políticas y referencias de otros campos oficiales.
- [ ] Mostrar evolución trimestral, diferencias por sexo, cobertura territorial y condiciones laborales con universos explícitos.
- [ ] Entregar informe editorial offline HTML/Markdown/PDF, gráficas SVG/PNG, datos tabulares y evidencia de cada conclusión.
- [ ] Completar documentación, reproducción desde instalación limpia, pruebas, auditoría GSD y release público verificable.

### Out of Scope

- Frontend, backend, servicio hospedado o aplicación navegable: AGENTS.md delimita investigación local y publicaciones estáticas.
- Fuentes de vacantes, APIs pagadas, inferencia externa o datos propietarios: no forman parte del catálogo aprobado ni del presupuesto.
- Efectos causales de estudiar una carrera, recomendaciones personales o ranking universal: ENOE transversal no los demuestra.
- Publicar microdatos individuales: se conservan localmente; la entrega pública contiene agregados y evidencia redistribuible.
- Sumar personas entre trimestres o asumir muestras independientes: el panel rotatorio comparte observaciones.

## Context

Python 3.12, CLI local, DuckDB, JSON Schema y Matplotlib. El código v1 protege la demo sintética y necesita un contrato v2 para investigación oficial. Existen investigaciones recientes en `docs/research/COMPARABLE-REPOSITORIES.md`, `PRODUCT-GAP-AUDIT.md` y `ENOE-METHOD-REVIEW.md`; deben reutilizarse y profundizarse solo donde hay vacíos.

La ampliación está definida en `docs/FINAL-RELEASE-PLAN.md` y ADR 0006. La adquisición y el estimador tienen implementación parcial y pruebas aisladas; todavía no constituyen una publicación oficial validada. La prueba con 2026-Q2 reproduce exactamente los totales nacionales al aplicar 15<=EDA<=98, pero identifica 13 estratos con una sola UPM: el tratamiento y su limitación deben quedar explícitos antes de publicar incertidumbre.

R 4.6.1 y survey 4.5 están instalados en la caché ignorada como oráculo de validación, no como dependencia del producto Python. El prototipo concuerda en los casos probados; la contrastación versionada con la cohorte final de edad conocida y todos los criterios de Phase 2 sigue pendiente. La precisión con ajuste propio de estratos singleton siempre será explícitamente no oficial.

## Constraints

- **Autorización:** trabajo local, subagentes y publicación en el repositorio público indicado autorizados; otros despliegues no.
- **Datos:** fuentes oficiales aprobadas, atribución INEGI y aviso de transformación; conservar null y separar campo de estudios, ocupación, industria, geografía y periodo.
- **Precisión:** no activar cifras por decisión de un agente; usar evidencia, contrato, verificaciones y reglas de supresión. Un ajuste de varianza propio nunca se presentará como precisión oficial.
- **Operación:** descargas y ejecuciones con recibos; current inválido ante fallo; no reusar éxito histórico como actualidad.
- **Presupuesto:** herramientas gratuitas y modelos nativos de Codex; ninguna inferencia de pago adicional.
- **Colaboración:** propiedad de archivos, preservar cambios concurrentes, subagentes sin delegación adicional.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Hito v1.0.0 de investigación real, alcance completo | Corrección explícita del usuario al MVP | Activo |
| Seguir recomendaciones GSD | Instrucción del usuario del 22 de septiembre | Primera fase completa con investigación, planes, revisiones, controles negativos, seguridad y verificación |
| Cinco fases sustanciales con revisión de planes y verificación | Granularidad gruesa recomendada, sin recortar entregables | Roadmap activo; Phase 1 completa |
| Cohorte principal CS_P13_1=7 y CS_P16=1, edad conocida 15–97 | No mezclar campo de licenciatura y posgrado ni edad desconocida | Contrato y reglas verificados en Phase 1 |
| Intervalos 90%, CV y supresión | Incertidumbre interpretable y coherente con encuesta | Método y oráculo pendientes |
| Informe estático offline y datos exportables | Entrega útil dentro del alcance autorizado | Activo |

## Evolution

Después de cada fase se actualizarán requisitos verificados, decisiones y límites, con referencias a la evidencia. Al cerrar el hito se revisarán alcance, utilidad prometida y resultados reales; ningún pendiente se convertirá en completo por existir documentación o una prueba aislada.

---
*Last updated: 2026-09-22 after Phase 1 canonical completion; numerical and release acceptance remain pending.*
