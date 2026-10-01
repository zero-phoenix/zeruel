# Auditoría Integral de Código, Reglas y Conocimiento de Zeruel

**Fecha:** 01/10/2026  
**Marco Epistemológico:** *Tractatus Logico-Philosophicus* (Wittgenstein) & Racionalismo Crítico / Falsacionismo (Popper).  
**Metodología Dialéctica:** Debate deliberativo formal del Consejo de la Tríada (DeepSeek V4.1 Flash + GLM-5.3 Max vía `tools/council.py`) con síntesis ejecutiva de Zeruel.  
**Objetivo:** Paso 1 de 5 para la reestructuración binaria arquitectónica:  
- **CEREBRO (`zero-phoenix/zeruel`):** Código puro, modelos de procedimiento, reglas de inferencia, suites de pruebas y especificaciones universales. Lo único que razona, infiere y dice (*Tractatus*).
- **APÉNDICE ACÉFALO (`zero-phoenix/zeruel-corpus`):** La totalidad de los hechos atómicos documentales (expedientes brutos, PDFs, XLSX, DOCX originales). Acéfalo (estrictamente sin código, reglas ni prompts). Vinculado al cerebro únicamente mediante `corpus.lock` (commit fijado y hashes SHA-256) y operado mediante `tools/corpus.py sync|verify|pin` (sin submódulos git).

---

## 1. Marco Teórico y Criterios de Clasificación

1. **Wittgenstein (*Tractatus* 1, 1.1, 7):**
   - *El mundo es la totalidad de los hechos, no de las cosas.* Los hechos administrativos (expedientes, resoluciones dictadas, pólizas) pertenecen exclusivamente al apéndice acéfalo.
   - El cerebro formaliza las proposiciones lógicas que figuran dichos hechos. Si un archivo del cerebro contiene rutas fijas a entornos de un desarrollador particular (`C:\Users\D\...`) o datos personales no anonimizados, vulnera la universalidad lógica de la proposición.
   - *De lo que no se puede hablar, hay que callar.* El cerebro nunca debe proyectar ni afirmar hechos que no consten verificados criptográficamente en el `corpus.lock`.
2. **Popper (Falsacionismo y Guardas Negativas):**
   - Un archivo es **UTIL** si sobrevive a la prueba de falsación (resuelve una clase de problemas, es portable, comprobable y sin supuestos espurios).
   - Un archivo es **CONTRADICTORIO** si existe tensión interna real entre lo que declara ser y su implementación (hardcodeo de rutas locales, PII en repositorios públicos/de código, o verificación de blobs privados en el repositorio erróneo).
   - Un archivo es **INUTIL** si es un duplicado redundante sin pipeline de sincronización, o un artefacto consumido de un solo uso sin valor operativo ni epistemológico.
3. **Protocolo de Privacidad y Consulta a Subagentes:**
   - En estricto cumplimiento de la regla de seguridad y confidencialidad, las consultas al Consejo de la Tríada enviaron **únicamente código abstracto, nombres de archivo, rutas estructurales e invariantes**, sin exponer jamás contenidos de expedientes, PII ni claves.

---

## 2. Inventario y Auditoría Exhaustiva por Archivo (46 Archivos)

A continuación se auditan de forma exhaustiva los **46 archivos** del alcance (`tools/`, `scripts/`, `knowledge/*.md|json|txt`, `docs/PROMPT-*`).

### A. Herramientas (`tools/` — 20 archivos)

| Archivo | Referencias / Tests | Contradicción con Reglas Vigentes (Evidencia Concreta) | Veredicto | Acción | Justificación Técnica y Dialéctica (Debate Tríada) |
|---|---|---|---|---|---|
| `tools/agy-login-codespace.ps1` | 5 refs (README.md, docs/HANDOFF.md, etc.) | Línea 17: ruta absoluta local C:\Users\D\... contradice destino nominal Codespace. | **UTIL** | `generalizar` | Herramienta operativa de login device-code para Codespaces. Requiere parametrizar ruta con $env:USERPROFILE. *Debate:* DeepSeek señaló tensión entre nombre y path local; GLM-5.3 propuso generalizar bajo contrato de config layering. |
| `tools/agy-login.ps1` | 3 refs (docs/HANDOFF.md, tools/agy-login-codespace.ps1, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Script nativo de autenticación OAuth sin rutas absolutas ni acoplamiento indebido. *Debate:* Coincidencia total en el Consejo: herramienta CLI esencial a conservar. |
| `tools/analyze_workload.py` | 2 refs (tools/publish_knowledge_notes.py, docs/AUDITORIA-codigo.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Motor procedimental de cómputo de plazos procesales legales de seguros (20d, 120d, FECHA LÍMITE). *Debate:* DeepSeek advirtió validar días hábiles/feriados y reloj inyectable; GLM-5.3 ratificó como núcleo procedimental con tests. |
| `tools/audit_generated.py` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 8, 9, 10: rutas absolutas a C:\Users\D\Desktop y carpetas de expedientes. | **UTIL** | `generalizar` | Utilidad de comparación estructural de resoluciones generadas vs modelos. Requiere CLI con argumentos dinámicos. *Debate:* Coincidencia: lógica analítica reutilizable acoplada a Desktop; requiere desacople y generalización CLI. |
| `tools/build_all_corrections.py` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 3, 38, 150: C:\Users\D\Desktop; líneas 37-39, 170-171: PII y hechos reales de casos 3017, 3057, 3075. | **CONTRADICTORIO** | `generalizar` | Script monolítico acoplado a 3 expedientes con datos reales y rutas duras a Desktop; viola Cerebro universal. *Debate:* DeepSeek propuso clasificarlo INUTIL por ser script de un solo uso; GLM y Zeruel sintetizan CONTRADICTORIO por tensión con Cerebro y necesidad de generalizar el motor. |
| `tools/build_three_corrected.py` | 1 ref (docs/AUDITORIA-codigo.md; 0 en código) | Docstring línea 3 promete 'los 3 casos', pero cuerpo contiene funciones genéricas XML (clean_highlights_zip, replace_paragraph_text) sin main() ejecutable. | **CONTRADICTORIO** | `generalizar` | Tensión entre docstring de casos y lógica pura reusable de manipulación OOXML. Debe extraerse a tools/docx_utils.py. *Debate:* DeepSeek identificó contradicción fértil (docstring ad-hoc vs cuerpo genérico); GLM respaldó extracción a biblioteca general. |
| `tools/council.py` | 3 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, knowledge/PROMPT-PARALELO.md, docs/AUDITORIA-codigo.md) | Línea 14: Path.home() fijo a keys.env; salidas de debate sin direccionamiento por sesión. | **UTIL** | `generalizar` | Motor canónico del Consejo de la Tríada (DeepSeek V4.1 + GLM-5.3). Debe parametrizar resolución de keys y evitar colisiones concurrentes. *Debate:* DeepSeek alertó sobre race conditions y CWD; GLM-5.3 propuso nombres direccionados por sesión y contratos de salida. |
| `tools/council_learning.py` | 2 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, docs/AUDITORIA-codigo.md) | Líneas 19, 21, 22: rutas absolutas a C:\Users\D\Desktop. | **UTIL** | `generalizar` | Generador de síntesis de aprendizaje tripartito a partir de diffs. Debe recibir rutas por argumento CLI o variable de entorno. *Debate:* Coincidencia: algoritmo de aprendizaje valioso que debe desacoplarse de la máquina del autor. |
| `tools/deepseek_assist.py` | 4 refs (docs/HANDOFF.md, docs/reviews/deepseek-2026-09.md, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Wrapper de asistencia directa por CLI a DeepSeek sin rutas hardcodeadas. *Debate:* Coincidencia total: herramienta CLI limpia a conservar. |
| `tools/extract_diffs.py` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 48, 49, 91: rutas absolutas a carpetas de Desktop. | **UTIL** | `generalizar` | Extractor de diferencias estructurales entre borradores y modelos definitivos. Debe recibir paths por parámetro. *Debate:* Coincidencia: pipeline analítico útil que requiere interfaz CLI desacoplada. |
| `tools/find_best_templates.py` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 3, 8: rutas absolutas a Desktop; líneas 33, 39, 45: acoplamiento a números de caso. | **UTIL** | `generalizar` | Algoritmo de similitud para selección de plantilla óptima. Requiere desacoplar paths fijos. *Debate:* Coincidencia: heurística de matching reutilizable a generalizar como biblioteca de selección de plantillas. |
| `tools/finish_knowledge.py` | 2 refs (knowledge/MEGAPROMPT-continuacion.md, docs/AUDITORIA-codigo.md) | Líneas 56, 57: rutas absolutas a Desktop y carpetas privadas locales. | **CONTRADICTORIO** | `generalizar` | Script de empaquetado de notas y hashes previo a la separación; debe migrarse a tools/corpus.py. *Debate:* DeepSeek lo catalogó UTIL condicional previo a ingesta; GLM y Zeruel determinan CONTRADICTORIO con el nuevo estándar de corpus.lock. |
| `tools/get_checkpoint_oauth.py` | 5 refs (docs/HANDOFF.md, docs/STATUS.md, etc.) | Línea 7: ruta absoluta local C:\Users\D\... para extracción de credenciales OAuth. | **UTIL** | `generalizar` | Extractor de credenciales OAuth para recuperación de checkpoints en Render. Debe usar Path.home() estándar. *Debate:* DeepSeek cuestionó seguridad del path fijo; GLM-5.3 propuso contrato formal de almacén de credenciales con permisos 0600. |
| `tools/inspect_new_cases.py` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 3, 10: rutas a Desktop\Nuevas correcciones; línea 46: acoplamiento a casos específicos. | **CONTRADICTORIO** | `generalizar` | Inspector acoplado a estructura de carpetas de expedientes de un usuario específico; viola neutralidad del Cerebro. *Debate:* Coincidencia: herramienta atada a layout local que debe convertirse en comando CLI abstracto. |
| `tools/prepare_local_ocr.py` | 5 refs (docs/HANDOFF.md, docs/reviews/local-2026-09-30.md, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Pipeline de preparación de OCR local y sanitización para la extensión de Edge. *Debate:* Coincidencia total: componente modular sin rutas absolutas, esencial para el pipeline de ingesta segura. |
| `tools/preserve_private_sources.py` | 2 refs (knowledge/MEGAPROMPT-continuacion.md, docs/AUDITORIA-codigo.md) | Líneas 52-54: crea y escribe en knowledge/private_sources y knowledge/private_index dentro de zero-phoenix/zeruel. | **CONTRADICTORIO** | `generalizar` | Copia e indexa documentos privados brutos dentro del repo del Cerebro; contradice frontalmente la separación CEREBRO vs APÉNDICE ACÉFALO. *Debate:* Coincidencia total en el Consejo: contradicción estructural de jurisdicción; debe sustituirse por tools/corpus.py sync. |
| `tools/publish_knowledge_notes.py` | 2 refs (knowledge/MEGAPROMPT-continuacion.md, docs/AUDITORIA-codigo.md) | Líneas 46, 55: referencias a rutas relativas acopladas a repositorios y private sources locales. | **UTIL** | `generalizar` | Publicador de notas técnicas de conocimiento. Requiere desacoplar dependencias directas a carpetas locales privadas. *Debate:* Coincidencia: herramienta de publicación válida pero dependiente de layout interno a flexibilizar. |
| `tools/snapshot_related_repositories.py` | 2 refs (tools/publish_knowledge_notes.py, docs/AUDITORIA-codigo.md) | Línea 21: escribe árboles en knowledge/repositories/; línea 35: importa preserve_private_sources. | **CONTRADICTORIO** | `generalizar` | Descarga e incrusta metadatos de repositorios satélites dentro de knowledge/ del Cerebro importando módulo privado. *Debate:* Coincidencia: propaga el acoplamiento indebido de preserve_private_sources; debe desacoplarse hacia configuración modular. |
| `tools/summarize_diffs.py` | 1 ref (docs/AUDITORIA-codigo.md) | Línea 41: ruta absoluta a Desktop. | **UTIL** | `generalizar` | Generador de tablas de resumen de diferencias. Requiere parametrizar archivo JSON de entrada. *Debate:* Coincidencia: algoritmo de análisis léxico y estilístico a generalizar como utilidad CLI. |
| `tools/verify_private_remote.py` | 2 refs (knowledge/MEGAPROMPT-continuacion.md, docs/AUDITORIA-codigo.md) | Líneas 10, 11: verifica git blobs bajo knowledge/private_sources dentro del repo; línea 55: escribe verification-remote.json. | **CONTRADICTORIO** | `generalizar` | Verifica criptográficamente blobs privados dentro del repositorio de código en vez de validar contra corpus.lock en el corpus. *Debate:* Coincidencia total: criptografía válida pero aplicada sobre el sujeto equivocado; debe subsumirse en tools/corpus.py verify. |

### B. Scripts (`scripts/` — 4 archivos)

| Archivo | Referencias / Tests | Contradicción con Reglas Vigentes (Evidencia Concreta) | Veredicto | Acción | Justificación Técnica y Dialéctica (Debate Tríada) |
|---|---|---|---|---|---|
| `scripts/build_susalud_2846.py` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 17, 18, 76: C:\Users\D\Desktop; líneas 1, 18, 66: acoplado al caso 2846-2026/CC1. | **CONTRADICTORIO** | `generalizar` | Script ad-hoc para un solo expediente con rutas duras a Desktop; contradice el principio de Cerebro como motor abstracto. *Debate:* DeepSeek lo calificó INUTIL por ser artefacto consumido; GLM-5.3 y Zeruel señalan CONTRADICTORIO por tensión arquitectónica y rescate de la regla de Susalud. |
| `scripts/build_susalud_2846_exact.py` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 19, 20, 41: C:\Users\D\Desktop; líneas 2, 20, 211: acoplado al caso 2846-2026/CC1. | **CONTRADICTORIO** | `generalizar` | Bifurcación (fork ad-hoc) de build_susalud_2846.py con rutas fijas; síntoma de falta de parametrización en el motor. *Debate:* Coincidencia: code smell flagrante (parche sobre parche de un solo caso); la lógica debe generalizarse en el pipeline de improcedencias. |
| `scripts/install_cli.py` | 3 refs (Dockerfile, knowledge/MEGAPROMPT-continuacion.md, docs/AUDITORIA-codigo.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Instalador oficial del CLI de Antigravity utilizado en entornos locales y Dockerfile. *Debate:* DeepSeek exigió chequear checksum del binario; GLM-5.3 ratificó utilidad directa para despliegues automatizados. |
| `scripts/recover_checkpoint.py` | 6 refs (README.md, docs/STATUS.md, tests/test_checkpoint_recovery.py, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Script canónico de recuperación de checkpoints y tareas en nube; probado en la suite de pruebas automatizada. *Debate:* Coincidencia total: verificado empíricamente con tests unitarios y respaldo en CI. |

### C. Conocimiento Markdown (`knowledge/*.md` — 11 archivos)

| Archivo | Referencias / Tests | Contradicción con Reglas Vigentes (Evidencia Concreta) | Veredicto | Acción | Justificación Técnica y Dialéctica (Debate Tríada) |
|---|---|---|---|---|---|
| `knowledge/AGENTS.md` | 19 refs (knowledge/MEGAPROMPT-continuacion.md, knowledge/PROMPT-PARALELO.md, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Especificación formal de gobernanza, roles (Tríada), protocolo de handoff y arquitectura viva de Zeruel. *Debate:* Coincidencia total: núcleo procedimental y constitucional del Cerebro. |
| `knowledge/MEGAPROMPT-continuacion.md` | 8 refs (AGENTS.md, README.md, etc.) | Líneas 83, 84, 306: rutas absolutas locales; líneas 42, 69, 70: rutas a knowledge/private_sources. | **CONTRADICTORIO** | `fusionar` | Megaprompt histórico superado por la nueva separación CEREBRO vs CORPUS; contiene paths absolutos obsoletos. *Debate:* DeepSeek advirtió peligro de cargar rutas muertas; GLM propuso factorizar en perfiles bajo el estándar PROMPT-CONTINUIDAD-APRENDIZAJE.md. |
| `knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 28, 32, 38: mención de rutas locales en sección histórica; líneas 90-92: mención de casos. | **UTIL** | `conservar` | Prompt maestro canónico recién consolidado para la continuidad operativa de Zeruel en entornos limpios. *Debate:* Coincidencia total en el debate: constituye el nuevo CORE universal de relevo y memoria acumulada. |
| `knowledge/PROMPT-PARALELO.md` | 1 ref (docs/AUDITORIA-codigo.md) | Líneas 14, 19: rutas locales; línea 26: cita knowledge/private_sources. | **UTIL** | `conservar` | Protocolo formal de orquestación y scheduling para subagentes concurrentes (no relevo secuencial). *Debate:* DeepSeek demostró que no es un prompt de relevo redundante sino un orquestador ortogonal; GLM ratificó preservarlo. |
| `knowledge/PROMPT-continuacion.md` | 10 refs (AGENTS.md, README.md, etc.) | Línea 7: referencia a knowledge/private_sources y parámetros de sesión superados. | **CONTRADICTORIO** | `fusionar` | Prompt de relevo histórico intermedio; subsumido por PROMPT-CONTINUIDAD-APRENDIZAJE.md. *Debate:* Coincidencia: duplicación histórica que debe consolidarse bajo el estándar canónico único. |
| `knowledge/README.md` | 15 refs (AGENTS.md, README.md, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Directorio índice y visión global de la arquitectura del conocimiento de Zeruel. *Debate:* Coincidencia total: documentación modular esencial a conservar. |
| `knowledge/WORKLOAD.md` | 11 refs (AGENTS.md, README.md, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Especificación técnica y legal de plazos procesales (20d, 120d, FECHA LÍMITE) y procedimientos de seguros CC1. *Debate:* DeepSeek destacó necesidad de anclaje normativo; GLM-5.3 lo confirmó como especificación declarativa de dominio. |
| `knowledge/aprendizaje_deepseek.md` | 3 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, tools/council_learning.py, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Registro de heurísticas críticas, auditoría adversarial y falsacionismo popperiano destilado por DeepSeek. *Debate:* Coincidencia: memoria heurística esencial de la Tríada que nutre la supervisión crítica. |
| `knowledge/aprendizaje_glm53.md` | 3 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, tools/council_learning.py, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Registro de invariantes semánticas, contratos de datos y arquitectura modular destilado por GLM-5.3. *Debate:* Coincidencia: memoria arquitectónica esencial para la escalabilidad multipropósito de Zeruel. |
| `knowledge/aprendizaje_supervision_lsq.md` | 2 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, docs/AUDITORIA-codigo.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Síntesis tripartita de supervisión y reglas de formato, imputación y estructura de resoluciones de seguros. *Debate:* Coincidencia: canon estilístico y procesal derivado de la supervisión real. |
| `knowledge/diff_summary.md` | 4 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, tools/council_learning.py, etc.) | Ninguna (Limpio) | **UTIL** | `conservar` | Registro estructurado de diferencias bloque por bloque de los 8 casos de entrenamiento. *Debate:* Coincidencia: bitácora canónica con formato Markdown referenciada en el motor de aprendizaje. |

### D. Registros e Índices JSON (`knowledge/*.json` — 5 archivos)

| Archivo | Referencias / Tests | Contradicción con Reglas Vigentes (Evidencia Concreta) | Veredicto | Acción | Justificación Técnica y Dialéctica (Debate Tríada) |
|---|---|---|---|---|---|
| `knowledge/diferencias_aprendizaje.json` | 3 refs (tools/extract_diffs.py, tools/summarize_diffs.py, docs/AUDITORIA-codigo.md) | Líneas 3, 4, 81: rutas absolutas a Desktop en metadatos de diffs. | **UTIL** | `conservar` | Estructura JSON de entrenamiento usada activamente por tools/extract_diffs.py y summarize_diffs.py. *Debate:* GLM-5.3 propuso esquematizar con JSON Schema y relativizar paths para su consumo en pipelines de ML/testing. |
| `knowledge/verification-local.json` | 7 refs (docs/HANDOFF.md, docs/STATUS.md, etc.) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico de hashes locales pre-separación. Debe integrarse en la especificación corpus.lock. *Debate:* DeepSeek propuso clasificarlo fósil; GLM y Zeruel sintetizan fusionar su trazabilidad en el nuevo corpus.lock. |
| `knowledge/verification-main-pr24.json` | 6 refs (docs/HANDOFF.md, docs/STATUS.md, etc.) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico de verificación remota de PR #24. Debe consolidarse en corpus.lock. *Debate:* Misma síntesis: evidencia histórica de integridad a subsumir en el archivo de bloqueo. |
| `knowledge/verification-megaprompt.json` | 1 ref (docs/AUDITORIA-codigo.md) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico de hashes del megaprompt. Debe consolidarse en corpus.lock. *Debate:* Misma síntesis: consolidar trazabilidad criptográfica. |
| `knowledge/verification-remote.json` | 4 refs (knowledge/MEGAPROMPT-continuacion.md, knowledge/README.md, etc.) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico generado por verify_private_remote.py. Debe consolidarse en corpus.lock. *Debate:* Misma síntesis: consolidar en corpus.lock y remover JSONs individuales sueltos. |

### E. Borradores y Transcripciones TXT (`knowledge/*.txt` — 4 archivos)

| Archivo | Referencias / Tests | Contradicción con Reglas Vigentes (Evidencia Concreta) | Veredicto | Acción | Justificación Técnica y Dialéctica (Debate Tríada) |
|---|---|---|---|---|---|
| `knowledge/borrador_3017.txt` | 1 ref (docs/AUDITORIA-codigo.md; 0 en código) | Línea 1 expediente 3017, líneas 26, 42: PII no anonimizado (Alessandra Martínez, póliza Pacífico, siniestro real). | **CONTRADICTORIO** | `borrar` | Borrador fáctico con datos personales y hechos reales de seguros; pertenece exclusivamente al corpus acéfalo. *Debate:* Coincidencia total en el Consejo: presencia de PII viola la premisa constitutiva del Cerebro puro; borrar y migrar al corpus. |
| `knowledge/borrador_3057.txt` | 1 ref (docs/AUDITORIA-codigo.md; 0 en código) | Línea 1 expediente 3057, líneas 2, 9, 10, 13: PII no anonimizado (Jessica Vásquez Cotillo, cónyuge, póliza Rímac 1016201425800). | **CONTRADICTORIO** | `borrar` | Borrador fáctico con datos personales y médicos sensibles; viola el principio de universalidad del Cerebro. *Debate:* Coincidencia total: cuerpo extraño en el Cerebro; debe migrarse a zero-phoenix/zeruel-corpus y purgarse de Zeruel. |
| `knowledge/borrador_3075.txt` | 1 ref (docs/AUDITORIA-codigo.md; 0 en código) | Línea 1 expediente 3075, líneas 2, 9, 10, 15: PII no anonimizado (Nilo Fidencio Escate Palacios, dirección Tacna, póliza Chubb 01-2025). | **CONTRADICTORIO** | `borrar` | Borrador fáctico con datos personales y reclamos patrimoniales reales; incompatible con el repositorio de código puro. *Debate:* Coincidencia total: expulsión obligatoria del Cerebro hacia el apéndice acéfalo. |
| `knowledge/diff_summary.txt` | 1 ref (docs/AUDITORIA-codigo.md; 0 en código) | Duplicado idéntico en texto plano de diff_summary.md sin script generador ni pipeline consumidor (0 refs en código). | **INUTIL** | `borrar` | Archivo redundante que duplica diff_summary.md; sin build target que lo sincronice, genera drift estático innecesario. *Debate:* DeepSeek argumentó utilidad teórica como derivado para máquinas; GLM y Zeruel concluyen que sin build pipeline formal es INUTIL en git y debe borrarse. |

### F. Prompts de Relevo en Documentación (`docs/PROMPT-*` — 2 archivos)

| Archivo | Referencias / Tests | Contradicción con Reglas Vigentes (Evidencia Concreta) | Veredicto | Acción | Justificación Técnica y Dialéctica (Debate Tríada) |
|---|---|---|---|---|---|
| `docs/PROMPT-continuacion-celular.md` | 2 refs (README.md, docs/AUDITORIA-codigo.md) | Líneas 4, 37: rutas absolutas locales C:\Users\D\...; parámetros de sesión móviles superados. | **CONTRADICTORIO** | `fusionar` | Prompt de relevo para terminal móvil con rutas duras; debe factorizarse como perfil móvil del estándar canónico. *Debate:* DeepSeek destacó su condición de variante de canal; GLM propuso arquitectura Core + Profiles, refactorizando en delta sin paths locales. |
| `docs/PROMPT-continuacion-claude-opus55-low.md` | 2 refs (docs/HANDOFF.md, docs/AUDITORIA-codigo.md) | Líneas 17, 19, 33: rutas absolutas locales C:\Users\D\...; parámetros de sesión Claude superados. | **CONTRADICTORIO** | `fusionar` | Prompt de relevo para Claude con rutas duras; debe factorizarse como perfil de modelo bajo el estándar canónico. *Debate:* Coincidencia: no duplicar el Core; parametrizar las restricciones de modelo en perfil modular sin rutas fijas. |

---

## 3. Deliberación Dialéctica del Consejo: Coincidencias y Desacuerdos

Durante la deliberación automatizada multi-agente entre **DeepSeek V4.1 Flash** (crítica falsacionista) y **GLM-5.3 Max** (diseño estructural y contratos modulares), moderada por **Zeruel**, se identificaron consensos profundos y desacuerdos metodológicos clave:

### 1. `tools/build_three_corrected.py` frente a `tools/build_all_corrections.py`
- **Coincidencia:** Ambos modelos reconocieron que `build_three_corrected.py` carece por completo de rutas duras a `Desktop` y no contiene PII, disponiendo de primitivas funcionales puras (`clean_highlights_zip` y `replace_paragraph_text`).
- **Desacuerdo:** DeepSeek propuso clasificar `build_all_corrections.py` como `INUTIL` (por ser un artefacto de un solo uso ya consumido, puramente desechable), mientras que clasificó `build_three_corrected.py` como `CONTRADICTORIO` debido a una «tensión fértil» entre su docstring (que promete 3 casos) y su cuerpo (genérico y huérfano). GLM-5.3 y Zeruel argumentaron que ambos deben catalogarse como `CONTRADICTORIO` con la regla del Cerebro puro: en el primer caso se rescata su lógica para generalizar un motor abstracto de casos, y en el segundo se extraen sus funciones a `tools/docx_utils.py`.

### 2. Preservación Histórica (`preserve_private_sources.py` y `verify_private_remote.py`)
- **Coincidencia Total:** Ambos modelos coincidieron en el veredicto **CONTRADICTORIO**. DeepSeek demostró el contraejemplo fatal: verificar criptográficamente blobs bajo `knowledge/private_sources` dentro del repo de código certifica integridad sobre la jurisdicción equivocada. GLM-5.3 ratificó que vulnera la inversión de dependencias y propuso que ambas funciones sean absorbidas por el nuevo comando `tools/corpus.py sync|verify` gobernado por `corpus.lock`.

### 3. Redundancia de `knowledge/diff_summary.txt`
- **Desacuerdo:** DeepSeek rechazó inicialmente el calificativo de «duplicado redundante», señalando que un `.txt` sin formato es una representación para máquinas útil para pipelines que no parsean Markdown. GLM-5.3 contraargumentó que un artefacto derivado sin un objetivo de build automatizado en CI (`make render-plain`) genera drift silencioso entre autores y herramientas.
- **Síntesis de Zeruel:** Veredicto **INUTIL** para control de versiones en git. Mantener dos gemelos estáticos en el Cerebro sin pipeline que los regenere viola la economía ontológica (*navaja de Ockham*). Debe eliminarse de git.

### 4. Factorización de Prompts: Monolito vs. Core + Perfiles
- **Desacuerdo Inicial:** Frente a la propuesta ingenua de fusionar todos los prompts en uno solo, DeepSeek advirtió dos falacias de diseño: confundir relevo con orquestación (`PROMPT-PARALELO.md` es un scheduler ortogonal, no un relevo secuencial), y confundir canónico con único (móvil y Claude son especializaciones legítimas de entorno).
- **Síntesis de GLM-5.3 y Zeruel:** Se adoptó el patrón **Core + Profiles**. `knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md` se consagra como el CORE universal canónico y libre de rutas locales; `PROMPT-PARALELO.md` se conserva como orquestador; y los prompts con rutas duras (`MEGAPROMPT-continuacion.md`, `PROMPT-continuacion.md`, `PROMPT-continuacion-celular.md`, `PROMPT-continuacion-claude-opus55-low.md`) se declaran **CONTRADICTORIOS** para ser unificados o factorizados como perfiles delta dependientes del Core.

### 5. Borradores con Texto Real (`borrador_3017.txt`, `3057.txt`, `3075.txt`)
- **Coincidencia Total e Irrefutable:** Ambos modelos y Zeruel dictaminaron que la presencia de datos personales (nombres de denunciantes, cónyuges, pólizas y reclamos no anonimizados) constituye un cuerpo extraño flagrante en el Cerebro. Su veredicto es unívocamente **CONTRADICTORIO**, y su acción inexorable es **borrar** del Cerebro y migrar a `zero-phoenix/zeruel-corpus` en los pasos 3 y 4.

---

## 4. Síntesis Numérica y Conteo de Veredictos

| Veredicto | Cantidad | Porcentaje | Criterio Epistemológico |
|---|---|---|---|
| **UTIL** | **29** | 63.0% | Sobrevive a la falsación: código modular, gobernanza procedimental, motor dialéctico o especificación canónica. |
| **CONTRADICTORIO** | **16** | 34.8% | Tensión comprobada empíricamente: rutas absolutas Windows, datos personales (PII) reales, o acoplamiento a fuentes privadas. |
| **INUTIL** | **1** | 2.2% | Redundancia estática exacta sin pipeline de sincronización (`diff_summary.txt`). |
| **TOTAL** | **46** | **100.0%** | **Totalidad de archivos auditados bajo el alcance.** |

### Distribución por Acción Propuesta:
- **`generalizar` (18):** Reemplazo de rutas duras por interfaces CLI/env var, o abstracción de bibliotecas (`tools/docx_utils.py`, `tools/corpus.py`).
- **`conservar` (16):** Módulos limpios del Cerebro (`agy-login.ps1`, `recover_checkpoint.py`, `AGENTS.md`, `WORKLOAD.md`, aprendizajes consolidados de la Tríada).
- **`fusionar` (8):** Prompts históricos a factorizar bajo `PROMPT-CONTINUIDAD-APRENDIZAJE.md`, y registros JSON a integrar en `corpus.lock`.
- **`borrar` (4):** Purgar del Cerebro los 3 borradores con PII (`borrador_3017.txt`, `3057.txt`, `3075.txt`) para residir exclusivamente en el apéndice acéfalo, y descartar el duplicado plano `diff_summary.txt`.

---

## 5. Hoja de Ruta para los Pasos 2 a 5

1. **Paso 2 (Diseño de `tools/corpus.py` y Contrato `corpus.lock`):**
   - Desarrollar la herramienta de sincronización determinista `tools/corpus.py` con subcomandos `sync`, `verify` y `pin`.
   - Especificar el esquema JSON de `corpus.lock` fijando el commit remoto de `zero-phoenix/zeruel-corpus` y los hashes SHA-256 de cada archivo atómico.
2. **Paso 3 (Creación y Población de `zero-phoenix/zeruel-corpus`):**
   - David crea el repositorio privado acéfalo en GitHub.
   - Migración de los 182 documentos originales, índices y los 3 borradores reales (`borrador_3017.txt`, `3057.txt`, `3075.txt`).
3. **Paso 4 (Depuración y Limpieza del Cerebro `zero-phoenix/zeruel`):**
   - Ejecución de las acciones de purga (`borrar` y `fusionar`) en el repositorio.
   - Incorporación de guardas negativas estrictas en `.gitignore` y suite de pruebas CI (`tests/test_no_private_blobs.py`).
4. **Paso 5 (Generalización de Motores y Despliegue en Render):**
   - Refactorizar las 18 herramientas y scripts marcados como `generalizar`.
   - Despliegue en Render y validación de la invariante `cloud_gate_passed: false` con bajo consumo de memoria.
