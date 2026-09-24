# Phase 1: Official Sources and Research Contract - Context

**Gathered:** 2026-09-22
**Status:** Ready for planning
**Decision authority:** El usuario instruyó seguir las opciones recomendadas de GSD y continuar autónomamente la entrega final. Se adoptan las decisiones siguientes dentro del alcance ya autorizado; no se reinterpretan como autorización de otros destinos de publicación.

<domain>
## Phase Boundary

Verificar los ocho insumos oficiales ENOE 2024-Q3–2026-Q2, cerrar la adquisición segura y definir contrato v2, poblaciones, denominadores y provenance. Esta fase no publica resultados laborales ni certifica el estimador; proporciona entradas y reglas inequívocas a la fase 2.
</domain>

<decisions>
## Implementation Decisions

### Fuente y reproducción
- Usar exclusivamente las ocho URLs exactas del catálogo aprobado, con sus SHA ya adquiridos y fijados. Validar también miembro SDEM, diccionario y catálogos, sin inventar URLs ni elegir el primer CSV por substring.
- Conservar intentos fallidos y éxitos posteriores; resolver current mediante el recibo inmutable y su hash. No volver a descargar archivos para cubrir una falla de validación que puede resolverse offline.
- Inventariar correcciones incluidas en los paquetes 2024 y el cambio ENT→CVE_ENT desde 2025-Q3; un alias compatible no implica automáticamente ruptura de concepto, pero debe quedar verificado.
- Publicar metadatos y agregados; ZIP y filas de personas permanecen en carpetas ignoradas. Términos y atribución INEGI acompañan los outputs.

### Universos y conceptos
- Contexto nacional: respuesta válida R_DEF=0 y residentes C_RES∈{1,3}; reproducir la convención oficial operativa 15<=EDA<=98 para benchmarks, declarando 98 como edad no especificada y nunca como 98 años.
- Cohorte principal de perfiles: respuesta/residencia válidas, edad conocida 15–97, CS_P13_1=7 y CS_P16=1; excluye técnicos, estudios incompletos y posgrados. Reportar las exclusiones. No llamarla el total de personas que alguna vez cursaron una licenciatura.
- Campos CS_P14_C se vinculan al catálogo incluido en cada paquete mediante normalización comprobada a seis dígitos. Foco: 033100, 032100 y 031300. 999999 y códigos ausentes tienen cobertura desconocida, sin inventar un campo.
- Campo de estudios, ocupación, industria, entidad, sexo registrado y periodo mantienen dimensiones distintas. No crear bridges automáticos.

### Contrato y valores públicos
- Mantener contrato v1 y pruebas sintéticas. Definir contrato v2 separado para investigación real, con grain único y registros estrictos.
- Incluir el método, diseño, precisión, soporte, unidad/base de precios y evidencia en cada estimación. `sample_size` significa n observado; no es tamaño efectivo.
- Separar el diagnóstico interno `estimate` de `value` público. La proyección pública omite estimación e intervalos que revelarían valores suprimidos.
- Definir denominadores y sentinelas con los diccionarios de los ocho paquetes. INGOCUP cero no es salario cero por sí solo; ingreso positivo conocido no describe a todos los ocupados.
- La política singleton permanece explícita y su aceptación numérica corresponde a fase 2. El contrato debe admitirla sin etiquetarla como precisión oficial ni activar publicación automáticamente.

### Agent discretion
- Nombres internos, distribución de archivos y pruebas acotadas compatibles con las convenciones existentes.
- Reutilizar código correcto ya escrito y verificarlo; no reimplementar para que parezca nuevo trabajo GSD.
</decisions>

<code_context>
## Existing Code Insights

### Reusable Assets
- `brujula/acquisition.py`: adquisición, caché, recibos, validación de ZIP y resolver; endurecimiento reciente con 19 pruebas aisladas.
- `brujula/runlock.py`: lock de sistema operativo.
- `brujula/resources.py`: recursos disponibles en checkout y wheel.
- `contracts/`, `data/catalog/`, `tests/test_quality.py`: patrón de JSON Schema y validación semántica.

### Established Patterns
- JSON UTF-8, hashes SHA-256, recibos finales inmutables y current mutable atómico.
- Fixtures aislados sin producción; control por estado, nunca nulos convertidos en cero.

### Integration Points
- `data/catalog/enoe-snapshots.json` y futuros contratos v2; el CLI real y renderer se integran en fases posteriores.
- `docs/CONTRACT.md` v1 se conserva como referencia de compatibilidad y enlaza la extensión nueva.
</code_context>

<specifics>
## Specific Ideas

Referencias revisadas: `renoe`, `joinENOE`, `surveytable`, `svy`, pipelines NHANES y otros de `docs/research/COMPARABLE-REPOSITORIES.md`. Se adoptan patrones de provenance, validación y comunicación, sin copiar código con licencias incompatibles. La entrega final debe ser presentable y sustantiva; no se reduce a un MVP.
</specifics>

<deferred>
## Deferred Ideas

Estimación y oráculos (fase 2), perfiles/comparaciones/claims (fase 3), informe y pipeline final (fase 4), release (fase 5). Son dependencias posteriores comprometidas, no funciones descartadas. No se agrega un frontend.
</deferred>
