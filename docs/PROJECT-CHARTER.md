# Mandato y autoridad del proyecto

Estado: decisión de alcance aceptada. Fecha: 2026-09-22.

Brújula Laboral MX es un repositorio de investigación, Analytics y automatización
local para interpretar evidencia sobre el mercado laboral mexicano. Este mandato
normaliza el handoff corregido sin incluir rutas privadas ni material de otros
proyectos. No sustituye la [especificación](SPEC.md) o el [alcance](SCOPE.md).

## Entrega y autorización

El titular autorizó crear y mantener público el repositorio
`erickinorganico/career-signals-mx`, conservar commits pequeños y subir avances
después de verificaciones proporcionales. También autorizó trabajo local,
instalación de dependencias open source sin costo monetario y subagentes
nativos de Codex.

La entrega vigente de esta etapa es la planeación, los specs, README, alcance y
su publicación. El objetivo posterior sigue siendo completar el observatorio;
un documento aceptado no acredita su implementación.

Quedan fuera de esta versión una aplicación, frontend, backend de aplicación,
interfaz navegable y hosting obligatorio. Sí corresponden scripts, CLI,
tablas/relaciones, contratos, pipelines, recibos, gráficos y reportes estáticos.

Solo se publican datos sintéticos propios o datos públicos con condiciones de
redistribución verificadas. No se autorizan fuentes restringidas, scraping que
contradiga términos, credenciales en archivos, inferencia pagada ni material
propietario de otros proyectos. Leer una fuente no autoriza activarla para
ingesta numérica. Las pruebas locales con fixtures son parte del trabajo
autorizado; no requieren confirmaciones repetidas.

## Precedencia documental

1. Las instrucciones explícitas más recientes del titular definen el alcance.
2. Este mandato y [SCOPE](SCOPE.md) documentan los límites y entregables.
3. [PRD](PRD.md) define requisitos y criterios de valor; [SPEC](SPEC.md) y
   [CONTRACT](CONTRACT.md) los contratos técnicos.
4. [ADRs](decisions/README.md) registran decisiones y sus reemplazos.
5. [PLAN](PLAN.md) ordena tareas; [STATUS](STATUS.md) registra evidencia actual.

Si aparece una contradicción, se registra en el backlog/riesgos y se corrige
según esta precedencia; no se convierte una implementación incompleta en
autoridad. Solo se consulta al titular cuando falta una decisión material que
no pueda resolverse dentro de lo autorizado.

## Invariantes

Campo de estudio, ocupación, industria, geografía, periodo y fuente se modelan
por separado. Un bridge editorial es una hipótesis trazable en REVIEW. La
ausencia no es cero. Cada resultado numérico exige fuente, fecha, población,
unidad, método y evidencia; cada figura mantiene esas notas al exportarse.
No se infieren causalidad, vacantes por carrera ni certeza individual.

El alcance comienza en México. La expansión a datos reales, nuevos indicadores
o países requiere resolver los contratos y comparabilidad correspondientes,
sin suponer que la disponibilidad pública equivale a permiso o equivalencia.

## Orquestación

Sol define e integra planes; Luna atiende tareas acotadas; Terra puede construir
módulos de datos/visualización; Astra revisa ambigüedad metodológica y hace la
revisión adversarial de cierre. Cada despacho tiene ownership y evidencia de
aceptación. Esto no implica cambios automáticos de modelo dentro de una tarea.
El historial efectivo está en [ORCHESTRATION](ORCHESTRATION.md).
