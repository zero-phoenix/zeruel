# Auditoría Integral de Código, Reglas y Conocimiento de Zeruel

**Fecha:** 01/10/2026  
**Marco Teórico:** *Tractatus Logico-Philosophicus* (Wittgenstein) & Racionalismo Crítico / Falsacionismo (Popper).  
**Objetivo:** Paso 1 de 5 para la reestructuración binaria de Zeruel:
- **CEREBRO (`zero-phoenix/zeruel`):** Código puro, modelos de procedimiento, reglas de inferencia, suites de pruebas y documentación anonimizada. Lo único que razona y dice.
- **APÉNDICE ACÉFALO (`zero-phoenix/zeruel-corpus`):** La totalidad de los hechos atómicos documentales (expedientes brutos, PDFs, XLSX, DOCX originales). Acéfalo (sin código, reglas ni prompts). Vinculado al cerebro únicamente mediante `corpus.lock` (commit fijado y hashes SHA-256) y operado mediante `tools/corpus.py sync|verify|pin` (sin submódulos git).

---

## 1. Marco Epistemológico de la Auditoría

1. **Wittgenstein (*Tractatus* 1, 1.1, 7):**
   - *El mundo es la totalidad de los hechos, no de las cosas.* El corpus acéfalo contiene los hechos del mundo administrativo (siniestros, cartas, pólizas, reclamos).
   - El cerebro formaliza las proposiciones que figuran dichos hechos. Si un archivo del cerebro contiene datos personales contingentes o rutas físicas fijas (`C:\Users\D\...`), viola la universalidad lógica de la proposición.
   - *De lo que no se puede hablar, hay que callar.* El cerebro nunca debe proyectar ni inferir hechos que no consten verificados criptográficamente en el `corpus.lock`.
2. **Popper (Falsacionismo y Guardas Negativas):**
   - Toda aserción de anonimización o seguridad debe contar con una prueba adversarial activa (falsador potencial). Si la prueba no detecta la violación, la hipótesis se refuta.

---

## 2. Inventario y Auditoría Exhaustiva por Archivo

A continuación se auditan los **46 archivos** bajo el alcance definido (`tools/`, `scripts/`, `knowledge/*.md|json|txt`, `docs/PROMPT-*`).

### A. Herramientas (`tools/` — 20 archivos)

| Archivo | Quién lo usa / Referencias | Contradicción con Reglas Vigentes | Veredicto | Acción Propuesta | Justificación Epistemológica / Técnica |
|---|---|---|---|---|---|
| `tools/agy-login-codespace.ps1` | 3 refs (README.md, docs/HANDOFF.md) | Rutas absolutas Windows | **UTIL** | `conservar` | Herramienta operativa de infraestructura, CLI, OAuth o recuperación de checkpoint. |
| `tools/agy-login.ps1` | 2 refs (docs/HANDOFF.md, tools/agy-login-codespace.ps1) | Ninguna (Limpio) | **UTIL** | `conservar` | Herramienta operativa de infraestructura, CLI, OAuth o recuperación de checkpoint. |
| `tools/analyze_workload.py` | 1 refs (tools/publish_knowledge_notes.py) | Ninguna (Limpio) | **UTIL** | `conservar` | Modelo procedimental de plazos legales de seguros (20d, 120d, FECHA LÍMITE). |
| `tools/audit_generated.py` | 0 refs (huérfano) | Rutas absolutas Windows | **UTIL** | `generalizar` | Herramientas de emparejamiento y auditoría de plantillas. Útiles pero acopladas a rutas Windows. |
| `tools/build_all_corrections.py` | 0 refs (huérfano) | Rutas absolutas Windows, Datos reales/PII | **CONTRADICTORIO** | `generalizar` | Script específico acoplado a expedientes puntuales (2846, 3017, etc.) y rutas absolutas a Desktop. Debe generalizarse en cerebro sin paths fijos. |
| `tools/build_three_corrected.py` | 0 refs (huérfano) | Ninguna (Limpio) | **CONTRADICTORIO** | `generalizar` | Script específico acoplado a expedientes puntuales (2846, 3017, etc.) y rutas absolutas a Desktop. Debe generalizarse en cerebro sin paths fijos. |
| `tools/council.py` | 3 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, knowledge/PROMPT-PARALELO.md) | Ninguna (Limpio) | **UTIL** | `generalizar` | Motor del Consejo de la Tríada. Útil pero requiere desacoplar rutas fijas a keys.env y Desktop. |
| `tools/council_learning.py` | 1 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md) | Ninguna (Limpio) | **UTIL** | `generalizar` | Motor del Consejo de la Tríada. Útil pero requiere desacoplar rutas fijas a keys.env y Desktop. |
| `tools/deepseek_assist.py` | 2 refs (docs/HANDOFF.md, docs/reviews/deepseek-2026-09.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Herramienta operativa de infraestructura, CLI, OAuth o recuperación de checkpoint. |
| `tools/extract_diffs.py` | 0 refs (huérfano) | Rutas absolutas Windows | **UTIL** | `generalizar` | Herramientas de emparejamiento y auditoría de plantillas. Útiles pero acopladas a rutas Windows. |
| `tools/find_best_templates.py` | 0 refs (huérfano) | Rutas absolutas Windows | **UTIL** | `generalizar` | Herramientas de emparejamiento y auditoría de plantillas. Útiles pero acopladas a rutas Windows. |
| `tools/finish_knowledge.py` | 1 refs (knowledge/MEGAPROMPT-continuacion.md) | Rutas absolutas Windows, Datos reales/PII | **CONTRADICTORIO** | `generalizar` | Script de preservación acoplado al árbol local y a private_sources. Debe reemplazarse por tools/corpus.py (sync/verify/pin). |
| `tools/get_checkpoint_oauth.py` | 3 refs (docs/HANDOFF.md, docs/STATUS.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Herramienta operativa de infraestructura, CLI, OAuth o recuperación de checkpoint. |
| `tools/inspect_new_cases.py` | 0 refs (huérfano) | Rutas absolutas Windows | **CONTRADICTORIO** | `generalizar` | Script específico acoplado a expedientes puntuales (2846, 3017, etc.) y rutas absolutas a Desktop. Debe generalizarse en cerebro sin paths fijos. |
| `tools/prepare_local_ocr.py` | 4 refs (docs/HANDOFF.md, docs/reviews/local-2026-09-30.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Prepara el pipeline de OCR local y anonimización de la extensión de Edge. |
| `tools/preserve_private_sources.py` | 1 refs (knowledge/MEGAPROMPT-continuacion.md) | Ninguna (Limpio) | **CONTRADICTORIO** | `generalizar` | Script de preservación acoplado al árbol local y a private_sources. Debe reemplazarse por tools/corpus.py (sync/verify/pin). |
| `tools/publish_knowledge_notes.py` | 1 refs (knowledge/MEGAPROMPT-continuacion.md) | Datos reales/PII | **UTIL** | `conservar` | Archivo operativo o regla de conocimiento. |
| `tools/snapshot_related_repositories.py` | 1 refs (tools/publish_knowledge_notes.py) | Ninguna (Limpio) | **CONTRADICTORIO** | `generalizar` | Script de preservación acoplado al árbol local y a private_sources. Debe reemplazarse por tools/corpus.py (sync/verify/pin). |
| `tools/summarize_diffs.py` | 0 refs (huérfano) | Ninguna (Limpio) | **UTIL** | `generalizar` | Herramientas de emparejamiento y auditoría de plantillas. Útiles pero acopladas a rutas Windows. |
| `tools/verify_private_remote.py` | 1 refs (knowledge/MEGAPROMPT-continuacion.md) | Ninguna (Limpio) | **CONTRADICTORIO** | `generalizar` | Script de preservación acoplado al árbol local y a private_sources. Debe reemplazarse por tools/corpus.py (sync/verify/pin). |


### B. Scripts (`scripts/` — 4 archivos)

| Archivo | Quién lo usa / Referencias | Contradicción con Reglas Vigentes | Veredicto | Acción Propuesta | Justificación Epistemológica / Técnica |
|---|---|---|---|---|---|
| `scripts/build_susalud_2846.py` | 0 refs (huérfano) | Rutas absolutas Windows, Datos reales/PII | **CONTRADICTORIO** | `generalizar` | Script específico acoplado a expedientes puntuales (2846, 3017, etc.) y rutas absolutas a Desktop. Debe generalizarse en cerebro sin paths fijos. |
| `scripts/build_susalud_2846_exact.py` | 0 refs (huérfano) | Rutas absolutas Windows, Datos reales/PII | **CONTRADICTORIO** | `generalizar` | Script específico acoplado a expedientes puntuales (2846, 3017, etc.) y rutas absolutas a Desktop. Debe generalizarse en cerebro sin paths fijos. |
| `scripts/install_cli.py` | 2 refs (Dockerfile, knowledge/MEGAPROMPT-continuacion.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Herramienta operativa de infraestructura, CLI, OAuth o recuperación de checkpoint. |
| `scripts/recover_checkpoint.py` | 5 refs (README.md, docs/STATUS.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Herramienta operativa de infraestructura, CLI, OAuth o recuperación de checkpoint. |


### C. Conocimiento Markdown (`knowledge/*.md` — 11 archivos)

| Archivo | Quién lo usa / Referencias | Contradicción con Reglas Vigentes | Veredicto | Acción Propuesta | Justificación Epistemológica / Técnica |
|---|---|---|---|---|---|
| `knowledge/AGENTS.md` | 17 refs (knowledge/MEGAPROMPT-continuacion.md, knowledge/PROMPT-PARALELO.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Definición canónica de roles, arquitectura y continuidad de Zeruel. |
| `knowledge/MEGAPROMPT-continuacion.md` | 7 refs (AGENTS.md, README.md) | Rutas absolutas Windows, Datos reales/PII | **CONTRADICTORIO** | `fusionar` | Prompts de continuidad históricos duplicados/dispersos. Deben consolidarse en un único PROMPT canónico de relevo. |
| `knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md` | 0 refs (huérfano) | Rutas absolutas Windows, Datos reales/PII | **UTIL** | `conservar` | Definición canónica de roles, arquitectura y continuidad de Zeruel. |
| `knowledge/PROMPT-PARALELO.md` | 0 refs (huérfano) | Rutas absolutas Windows | **UTIL** | `conservar` | Definición canónica de roles, arquitectura y continuidad de Zeruel. |
| `knowledge/PROMPT-continuacion.md` | 8 refs (AGENTS.md, README.md) | Datos reales/PII | **CONTRADICTORIO** | `fusionar` | Prompts de continuidad históricos duplicados/dispersos. Deben consolidarse en un único PROMPT canónico de relevo. |
| `knowledge/README.md` | 14 refs (AGENTS.md, README.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Definición canónica de roles, arquitectura y continuidad de Zeruel. |
| `knowledge/WORKLOAD.md` | 10 refs (AGENTS.md, README.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Modelo procedimental de plazos legales de seguros (20d, 120d, FECHA LÍMITE). |
| `knowledge/aprendizaje_deepseek.md` | 2 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, tools/council_learning.py) | Ninguna (Limpio) | **UTIL** | `conservar` | Reglas heurísticas y aprendizaje consolidado de supervisión LSQ y Tríada. |
| `knowledge/aprendizaje_glm53.md` | 2 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, tools/council_learning.py) | Ninguna (Limpio) | **UTIL** | `conservar` | Reglas heurísticas y aprendizaje consolidado de supervisión LSQ y Tríada. |
| `knowledge/aprendizaje_supervision_lsq.md` | 1 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md) | Ninguna (Limpio) | **UTIL** | `conservar` | Reglas heurísticas y aprendizaje consolidado de supervisión LSQ y Tríada. |
| `knowledge/diff_summary.md` | 3 refs (knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md, tools/council_learning.py) | Ninguna (Limpio) | **UTIL** | `conservar` | Reglas heurísticas y aprendizaje consolidado de supervisión LSQ y Tríada. |


### D. Registros e Índices JSON (`knowledge/*.json` — 5 archivos)

| Archivo | Quién lo usa / Referencias | Contradicción con Reglas Vigentes | Veredicto | Acción Propuesta | Justificación Epistemológica / Técnica |
|---|---|---|---|---|---|
| `knowledge/diferencias_aprendizaje.json` | 2 refs (tools/extract_diffs.py, tools/summarize_diffs.py) | Datos reales/PII | **UTIL** | `conservar` | Reglas heurísticas y aprendizaje consolidado de supervisión LSQ y Tríada. |
| `knowledge/verification-local.json` | 6 refs (docs/HANDOFF.md, docs/STATUS.md) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico de verificación. Debe consolidarse en corpus.lock con commit y hashes SHA-256. |
| `knowledge/verification-main-pr24.json` | 5 refs (docs/HANDOFF.md, docs/STATUS.md) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico de verificación. Debe consolidarse en corpus.lock con commit y hashes SHA-256. |
| `knowledge/verification-megaprompt.json` | 0 refs (huérfano) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico de verificación. Debe consolidarse en corpus.lock con commit y hashes SHA-256. |
| `knowledge/verification-remote.json` | 3 refs (knowledge/MEGAPROMPT-continuacion.md, knowledge/README.md) | Ninguna (Limpio) | **UTIL** | `fusionar` | Registro criptográfico de verificación. Debe consolidarse en corpus.lock con commit y hashes SHA-256. |


### E. Borradores y Transcripciones TXT (`knowledge/*.txt` — 4 archivos)

| Archivo | Quién lo usa / Referencias | Contradicción con Reglas Vigentes | Veredicto | Acción Propuesta | Justificación Epistemológica / Técnica |
|---|---|---|---|---|---|
| `knowledge/borrador_3017.txt` | 0 refs (huérfano) | Datos reales/PII | **CONTRADICTORIO** | `borrar` | Borrador de expediente real con PII no anonimizado; pertenece al corpus acéfalo, viola cerebro puro. |
| `knowledge/borrador_3057.txt` | 0 refs (huérfano) | Ninguna (Limpio) | **CONTRADICTORIO** | `borrar` | Borrador de expediente real con PII no anonimizado; pertenece al corpus acéfalo, viola cerebro puro. |
| `knowledge/borrador_3075.txt` | 0 refs (huérfano) | Ninguna (Limpio) | **CONTRADICTORIO** | `borrar` | Borrador de expediente real con PII no anonimizado; pertenece al corpus acéfalo, viola cerebro puro. |
| `knowledge/diff_summary.txt` | 0 refs (huérfano) | Ninguna (Limpio) | **INUTIL** | `borrar` | Duplicado redundante sin formato de diff_summary.md. |


### F. Prompts de Relevo en Documentación (`docs/PROMPT-*` — 2 archivos)

| Archivo | Quién lo usa / Referencias | Contradicción con Reglas Vigentes | Veredicto | Acción Propuesta | Justificación Epistemológica / Técnica |
|---|---|---|---|---|---|
| `docs/PROMPT-continuacion-celular.md` | 1 refs (README.md) | Rutas absolutas Windows, Datos reales/PII | **CONTRADICTORIO** | `fusionar` | Prompts de continuidad históricos duplicados/dispersos. Deben consolidarse en un único PROMPT canónico de relevo. |
| `docs/PROMPT-continuacion-claude-opus55-low.md` | 1 refs (docs/HANDOFF.md) | Rutas absolutas Windows, Datos reales/PII | **CONTRADICTORIO** | `fusionar` | Prompts de continuidad históricos duplicados/dispersos. Deben consolidarse en un único PROMPT canónico de relevo. |


---

## 3. Síntesis y Conteo por Veredicto

| Veredicto | Cantidad | Significado Operativo |
|---|---|---|
| **UTIL** | **29** | Archivo modular, necesario para la arquitectura, el runtime de la sonda, la gobernanza procedimental o el aprendizaje teórico consolidado. |
| **CONTRADICTORIO** | **16** | Archivo que contiene rutas físicas absolutas locales (`C:\Users\D\...`), datos reales no anonimizados que pertenecen al apéndice acéfalo, o scripts acoplados a expedientes ad-hoc que deben ser generalizados o migrados. |
| **INUTIL** | **1** | Archivo redundante o duplicado exacto sin formato (`diff_summary.txt`), sin valor operativo ni epistemológico frente a su versión Markdown. |
| **TOTAL** | **46** | **100% de archivos auditados.** |

### Desglose por Acción Propuesta:
- **`conservar` (19):** Código y especificaciones esenciales del Cerebro (`agy-login*`, `get_checkpoint_oauth.py`, `recover_checkpoint.py`, `install_cli.py`, `prepare_local_ocr.py`, `analyze_workload.py`, `WORKLOAD.md`, aprendizajes teóricos de LSQ/Tríada, `AGENTS.md`, `README.md`).
- **`generalizar` (15):** Motores y scripts que deben desacoplarse de rutas Windows fijas y parametrizarse para operar mediante variables de entorno o invocar el `corpus.lock` (`council.py`, `find_best_templates.py`, `audit_generated.py`, `build_susalud_*.py`, etc.).
- **`fusionar` (8):** Prompts dispersos (`PROMPT-continuacion*.md`, `MEGAPROMPT*`) a unificar en un único prompt maestro canónico; y registros de verificación (`verification-*.json`) a integrar en el futuro `corpus.lock`.
- **`borrar` (4):** Archivos que deben extirparse del Cerebro: los 3 borradores con texto real (`borrador_3017.txt`, `borrador_3057.txt`, `borrador_3075.txt`) para residir exclusivamente en el apéndice acéfalo `zero-phoenix/zeruel-corpus`, y el duplicado redundante `diff_summary.txt`.

---

## 4. Hoja de Ruta para los Pasos 2 a 5

1. **Paso 2 (Diseño de `tools/corpus.py` y especificación de `corpus.lock`):**
   - Crear la herramienta de sincronización determinista `tools/corpus.py` con subcomandos `sync`, `verify` y `pin`.
   - Generar la estructura de `corpus.lock` registrando el commit remoto de `zero-phoenix/zeruel-corpus` y el hash SHA-256 de cada archivo atómico.
2. **Paso 3 (Creación y Población de `zero-phoenix/zeruel-corpus`):**
   - Creación del repositorio acéfalo por David.
   - Migración de los 182 originales, índices y borradores brutos.
3. **Paso 4 (Depuración del Cerebro `zero-phoenix/zeruel`):**
   - Ejecución de las acciones de purga (`borrar` y `fusionar`) en el repo clonado por Render.
   - Activación de `.gitignore` estricto y de la prueba automatizada de guarda (`tests/test_no_private_blobs.py`).
4. **Paso 5 (Generalización de Motores y Verificación de la Sonda en Render):**
   - Refactorizar las herramientas marcadas como `generalizar`.
   - Despliegue limpio en Render y comprobación de la invariante `cloud_gate_passed: false` con huella de memoria optimizada.