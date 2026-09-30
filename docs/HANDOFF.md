# Relevo de Zeruel — para el siguiente agente (GPT 6.1 u otro)

Última actualización: 30/09/2026, por Claude (Opus 5.5) desde DESKTOP-B6D864U. Todo lo necesario está en este repositorio; los archivos locales de esa PC **no** estarán disponibles.

## 1. Tu papel
Ingeniero principal y supervisor de Zeruel. Continúa desde este estado sin repetir avances. Español, mensajes cortos. Antes de actuar: lee `README.md`, `docs/STATUS.md`, `docs/first-milestone.md`, `docs/browser-extension-plan.md`, `docs/reviews/deepseek-2026-09.md` y este archivo; haz `git fetch` y revisa `git log`.

**Método (popperiano):** hipótesis concreta → falsador → prueba adversarial o mutación → resultado → corrección de la causa → prueba de regresión. Etiqueta siempre la evidencia como **real** o **simulada**. No declares nada operativo sin evidencia real.

## 2. Reglas inalterables
- Sin tarjeta, recargas, pagos, créditos promocionales ni facturación.
- **Motor:** Antigravity CLI (`agy`) con la suscripción **Google AI Pro** del propietario (decisión del 30/09/2026, porque Gemini CLI dejó de atender a AI Pro el 18/06/2026). Modelo `gemini-3.8-flash-high`.
- **Respaldo:** Gemini API en capa gratuita, solo tras `paused_quota`, solo la prueba sintética, sin facturación. Nunca Vertex ni rutas facturables.
- Nunca extraer tokens de la app de escritorio Antigravity ni automatizar apps para eludir restricciones. La sesión de `agy` la crea el propietario iniciando sesión.
- Cuenta única: david.chavez.nge@gmail.com. Sin cuentas secundarias.
- Apps Script nunca con acceso «Cualquiera» ni «Cualquier persona con cuenta de Google».
- `cloud_gate_passed=false` hasta superar **toda** la matriz de `docs/first-milestone.md`.
- Render Free se suspende y pierde archivos: sin keepalive artificial.
- Credenciales, capturas, expedientes y memoria personal **fuera** del repositorio público. Nunca pedir secretos por chat.
- Memoria real y flujos jurídicos: no antes de superar la matriz. Excepción autorizada por el propietario (30/09/2026): la extensión de Edge **anonimizada** de la sección 5b.
- Acciones irreversibles (vincular Apps Script, aceptar condiciones, cargar secretos remotos, fusionar a `main`) → confirmación explícita del propietario en el momento.

## 3. Estado verificado
| Área | Estado | Evidencia |
|---|---|---|
| Recuperación del checkpoint (lease, generación, journal, `recover` manual) | Fusionado (PR #1, #2) | Simulada: 50 Python, 22 Node |
| Motor `agy` 1.2.14 (SHA-512, binario de root, `--sandbox`) | Fusionado (PR #3) | **Real** en contenedor 512 MB / 0,1 CPU: `synthetic_success` 12–20 s, ~210 MB |
| Herramientas del modelo | Denegadas en modo `-p` | **Real**: `denied_actions: RunCommand`, sin archivos creados |
| Render `zeruel-synthetic-probe` (`srv-dau6eq9srm7s73avnsb0`) | Live en `main` (tras PR #18) con 7 variables (5 secretos + `ZERUEL_GOOGLE_CLIENT_ID`, `ZERUEL_OWNER_EMAIL`); autodeploy desactivado | **Real** 30/09: `synthetic_success` con `agy`, checkpoint privado, idempotencia, recuperación tras reinicio, arranque en frío 28,3 s tras 17 min sin uso |
| Acceso web | Google solo para el propietario (redirección OIDC, prefiltro local, ≤10 consultas/min a tokeninfo) + token legado | **Real**: owner acepta, token basura y cabecera no ASCII → 401. Revisión adversarial: 4 hallazgos corregidos (PR #18) |
| Apps Script «Zeruel — punto de control sintético» | Vinculado al proyecto estándar 1096719789550; código = `main`; Ejecutable de API «Solo yo» | **Real** 30/09 (manifiesto `executionApi.access: MYSELF`) |
| Google Cloud | Proyecto `zeruel-checkpoint-09292354` sin facturación; 24 APIs conservadas; pantalla de consentimiento «Zeruel» en producción (solo `userinfo.email`); cliente OAuth de escritorio | **Real** 30/09 |
| Sesión `agy` (Google AI Pro) | Creada en Codespace con `tools/agy-login-codespace.ps1`; copiada a Render por el propietario | **Real** 30/09: `"status":"SUCCESS"`, `ZERUEL_OK` (en el codespace, no en Render) |
| DeepSeek | ≤ US$0,2143 gastados de US$1 | `docs/reviews/` |

## 4. Próximos pasos (fase 2), en orden
1. **Proyecto Cloud:** sin facturación confirmado en la consola el 30/09/2026. Revisa recursos y dependencias de las 24 APIs antes de retirar las innecesarias. El propietario decidió **conservar Analytics Hub y revisar recursos antes**; no desactivarla sin nueva confirmación. Apps Script debe permanecer habilitada. No deshabilitar servicios administrativos por suponer que son innecesarios.
2. **Vincular Apps Script** (Configuración del proyecto → cambiar proyecto → número 1096719789550). **Irreversible**: revoca autorizaciones y no permite volver al predeterminado. Pide confirmación al propietario inmediatamente antes.
3. Subir `apps-script/SyntheticCheckpoint.gs` y manifiesto (solo `userinfo.email`); propiedades privadas `ZERUEL_OWNER_EMAIL` y `ZERUEL_CHECKPOINT_SECRET` (aleatorio ≥ 32, generado por script sin mostrarlo). Implementar como **Ejecutable de API, Solo yo**.
4. Cliente OAuth del propietario con `userinfo.email` (+ el mínimo que exija `scripts.run`; justificar cualquier ámbito extra antes). Obtener refresh token por flujo oficial.
5. **Render:** autorización del propietario para almacenar secretos; cargar `ZERUEL_AGY_OAUTH_TOKEN`, `ZERUEL_CHECKPOINT_DEPLOYMENT_ID`, `ZERUEL_CHECKPOINT_SECRET`, `ZERUEL_CHECKPOINT_OAUTH_JSON` y, si existe, `ZERUEL_GEMINI_FREE_KEY`, sin imprimirlos. Despliegue manual de `main`.
6. **Matriz real** con datos sintéticos: propietario acepta; otra identidad rechazada; HMAC/replay; renovación de token; reinicio y suspensión de Render; idempotencia; `recover` real sobre una lease vencida; cuota agotada + respaldo; tarea lanzada desde el móvil con ambos Windows apagados (coordinar con el propietario; no los apagues tú). Registrar tiempo, RAM y CPU.
7. Actualizar `docs/STATUS.md` con evidencia real y límites.

## 5. Lo que NO está en el repositorio (debe recrearse)
- **Sesión de `agy`:** el propietario inicia sesión otra vez. **Sin Docker local (preferido en la PC Celeron):** `gh auth refresh -s codespace`, `gh codespace create -R zero-phoenix/zeruel -m basicLinux32gb --idle-timeout 30m --retention-period 1h`, `docker build -t zeruel .` dentro del codespace y luego `powershell -ExecutionPolicy Bypass -File tools\agy-login-codespace.ps1 -Codespace <nombre>`; el propietario copia la sesión a Render y se borra el codespace. En Windows con Docker: `docker build -t zeruel .` y luego `tools/agy-login.ps1` (abre el enlace completo y pasa el código; guarda la sesión en `%USERPROFILE%\.zeruel-private\agy-home`). En Linux/macOS basta ejecutar `agy` en una terminal.
- **Clave DeepSeek:** el propietario la define en la variable `DEEPSEEK_API_KEY`. Al crear un registro nuevo, usa `DEEPSEEK_SPENT_BEFORE=0.2143` para no exceder el US$1 total.
- Clave gratuita de AI Studio (opcional), secreto del checkpoint y credenciales OAuth: se generan en la fase 2.

## 5b. Tarea en paralelo: extensión de Edge anonimizada
Autorizada por el propietario el 30/09/2026. Carpeta `extension/`, Manifest V3, carga «desempaquetada» en `edge://extensions`, sin tiendas ni pagos. Objetivo: aprender cómo trabaja el propietario en el teletrabajo para después entrenar a Zeruel (al final lo hará Zeruel). Base: `docs/browser-extension-plan.md`.
- **Anonimizar todo en el propio equipo, antes de guardar nada:** nombres, DNI/RUC, direcciones, correos, teléfonos, números de expediente, póliza, cuenta y tarjeta, montos vinculados a personas y texto de documentos pasan a marcadores (PERSONA_1, EXPEDIENTE_1, EMPRESA_1, MONTO_1…). En las capturas se difumina el texto. Solo se conserva la estructura: pantalla, acción, orden y decisión.
- Nada sin anonimizar sale del equipo, se envía a GPT, DeepSeek u otro servicio, ni se sube al repositorio.
- Indicador permanente (activo / pausado / desconectado), pausa inmediata y activación diaria por el propietario.
- Solo sitios autorizados. Registra clics, navegación, cambios de pestaña, formularios enviados y capturas por acción, todo anonimizado. Nunca contraseñas, campos de contraseña, pantallas de inicio de sesión, tokens ni todas las teclas.
- Escritorio remoto: capturas anonimizadas y zonas de exclusión.
- Registros locales; el propietario los exporta a mano ya anonimizados. Procedimientos anonimizados en `docs/procedimientos/`.
- Prueba que falle si un registro o exportación contiene datos personales sin anonimizar (con datos ficticios). Probar en Edge, evidencia real vs simulada.

### Aclaración del propietario — 30/09/2026
El texto es necesario, también el obtenido de imágenes con escritura manuscrita o tipeada. La vista exclusivamente estructural no satisface el objetivo final. La anonimización debe distinguir nombre de hombre, nombre de mujer, apellido, tarjeta, crédito, póliza y las restantes categorías. Usar NOMBRE_DESCONOCIDO si el género no está establecido; no adivinarlo por el nombre. OCR y clasificación deben ejecutarse localmente; originales solo en memoria transitoria, nunca en registros, exportaciones ni servicios externos. La base estructural es una entrega parcial y no autoriza observar expedientes reales. Texto/OCR requieren pruebas propias y bloqueo ante contenido sin revisar.

También se exige copiar íntegramente formato: tipografía, tamaño, estilo, interlineado, márgenes, tablas, encabezados y pies de página. Los marcadores deben conservar ubicación y estilo. Preferir estructura del documento editable cuando exista autorización y acceso; los píxeles del remoto/OCR no proporcionan por sí solos una fuente, interlineado o pie editable exactos. Reconstrucciones deben identificarse y compararse con fixtures sintéticos. No declarar fidelidad íntegra hasta verificarla.

## 6. DeepSeek como asistente
`python tools/deepseek_assist.py <prompt> <salida> [tokens]`. Solo código público, diffs depurados y preguntas acotadas; nunca conversaciones, capturas, expedientes, memoria ni secretos. Reserva previa del coste máximo; una llamada incierta conserva la reserva y no se reintenta. Usa ≥ 60 000 tokens de salida (el razonamiento consume el tope). Verifica cada hallazgo antes de aceptarlo; registra aceptados y rechazados en `docs/reviews/`.

## 7. Trampas conocidas
- Windows + Git Bash: usa `MSYS_NO_PATHCONV=1` con `docker` (si no, `/root` se convierte en `C:/...`). Evita comillas anidadas complejas en heredocs; escribe scripts a archivo.
- `agy` exige terminal (TTY) para iniciar sesión y espera el código **60 s**. Las terminales parten la URL larga: ábrela completa (lo hace `tools/agy-login.ps1`).
- `agy --json-schema` se atasca con 0,1 CPU: no usarlo.
- `agy` pide el ámbito `cloud-platform` y descarga binarios auxiliares en `$HOME` (`webm_encoder`). Vigilar.
- `gcloud billing ...` puede quedarse esperando una respuesta interactiva: usa `--quiet` y ejecútalo solo.
- Fusionar un PR propio puede requerir aprobación del propietario.
- **PC del propietario (Celeron):** se congela con capturas de escritorio, Docker o procesos pesados. Trabajo pesado en la nube (Codespaces/Render); leer páginas como texto.
- El navegador integrado del agente no acepta pegar desde el portapapeles de Windows y falla al iniciar sesión en GitHub con Google: los secretos los pega el propietario en Edge.
- Git Credential Manager muestra un selector de 3 cuentas y falla («string binding is invalid»): en el checkout se configuró `credential.helper` local a `gh auth git-credential` (cuenta `zero-phoenix`).

## 8. Formato de cierre de cada sesión
Título «Relevo»: fecha y host; cambios; rama y último commit publicado; versión desplegada; pruebas reales y simuladas; gasto DeepSeek; configuración y bloqueos; próximo paso exacto; procesos que deben seguir activos. Actualiza este archivo y `docs/STATUS.md`.

## 9. Relevo — 30/09/2026 10:40 (UTC-5), DESKTOP-NLTEF6C
- **Cambios:** piloto de extensión Edge (`extension/`), OCR local con Tesseract.js (`tools/prepare_local_ocr.py` regenera `extension/vendor/`, ignorado por Git), anonimizador por spans tipados, modelo de formato, revisión local `docs/reviews/local-2026-09-30.md`. Trabajo de Codex rescatado sin commitear y publicado por Claude (Opus 5.5).
- **Rama:** `feat/edge-learning-local` (base `ce77356`). No fusionada a `main`.
- **Desplegado:** Render sigue en `6f07373` (no revalidado).
- **Pruebas simuladas:** 50 Python y 61 Node (22 backend + 39 extensión) aprobadas. **Real:** OCR sintético impreso en navegador de prueba (no Edge); proyecto Cloud sin facturación.
- **DeepSeek:** US$0 en esta sesión; acumulado US$0,2143.
- **Bloqueos:** extensión no instalada en Edge; recursos de Analytics Hub sin revisar; Apps Script sin vincular.
- **Próximo paso exacto:** (a) el propietario carga `extension/` desempaquetada en Edge tras `python tools/prepare_local_ocr.py` y se ejecuta la lista «Pendiente» de `docs/browser-extension-plan.md` con la fixture; (b) integrar el modelo de formato con captura/revisión; (c) fase 2 sección 4, paso 1 (revisar recursos Analytics Hub) y paso 2 con confirmación.
- **Node en esta PC:** no está en PATH; usar el de `%USERPROFILE%\.cache\codex-runtimes\...\node\bin\node.exe` y pasar los archivos `*.test.js` explícitamente (Node 24 no acepta carpetas en `--test`).

## 10. Relevo — 30/09/2026 ~14:30 (UTC-5), DESKTOP-NLTEF6C (Claude Opus 5.5)
- **Cambios:** fusionados a `main` los PR #6–#12: extensión Edge (probada real: pausa ante login y exportación sin datos personales), fase 2 pasos 1–5, `docs/PRIVACY.md`, `tools/get_checkpoint_oauth.py`, `tools/agy-login-codespace.ps1`.
- **Desplegado:** Render Live en `dc7eced` con los 5 secretos. Autodeploy desactivado: tras cada cambio relevante, «Manual Deploy → Deploy latest commit».
- **Pruebas reales:** extensión en Edge; Apps Script vinculado y desplegado «Solo yo»; refresh token OAuth; `agy` `SUCCESS`/`ZERUEL_OK` en codespace; arranque de Render sin errores. **Simuladas:** 50 Python y 61 Node.
- **DeepSeek:** US$0 en esta sesión; acumulado US$0,2143.
- **Bloqueos:** la tarea sintética **en Render** no se ha ejecutado (requiere que el propietario pegue `ZERUEL_ACCESS_TOKEN` en https://zeruel-synthetic-probe.onrender.com); `cloud_gate_passed=false`.
- **Próximo paso exacto:** el propietario lanza una tarea en la web del servicio; esperado `synthetic_success`. Si falla, leer `/api/status` y logs de Render. Después, resto de la matriz (sección 4, paso 6), incluida la prueba desde el móvil con los Windows apagados.
- **Procesos activos:** ninguno local. Codespace de login borrado; queda «silver-space-carnival» apagado (no creado por el agente; GitHub lo elimina tras 30 días sin uso).

## 11. Relevo — 30/09/2026 ~15:35 (UTC-5), DESKTOP-NLTEF6C (Claude Opus 5.5)
- **Cambios:** PR #14–#18: acceso con Google solo para el propietario (redirección OIDC con `state`/`nonce`; GIS/FedCM fallaba), endurecimiento tras revisión adversarial de 4 agentes (prefiltro local, límite de tokeninfo, comparación en bytes, pruebas no vacías), evidencia de matriz.
- **Desplegado:** Render Live con `main` (PR #18). Tras cada cambio: «Manual Deploy → Deploy latest commit».
- **Pruebas reales:** `synthetic_success` ×4 (antes y después del endurecimiento; 5–8 s, ~210 MB); checkpoint privado consultable; idempotencia; reinicio; arranque en frío 28,3 s; 401 limpio con token basura y cabecera no ASCII. **Simuladas:** 61 Python (5/5 mutantes detectados), 61 Node.
- **DeepSeek:** US$0; acumulado US$0,2143.
- **Pendiente de la matriz:** tarea desde el móvil con ambos Windows apagados (solo el propietario); renovación del token OAuth en un proceso vivo >1 h; cuota agotada + respaldo; otra identidad Google real en vivo. `cloud_gate_passed=false`.
- **Próximo paso exacto:** el propietario apaga ambos Windows y, desde el celular con datos móviles, entra en https://zeruel-synthetic-probe.onrender.com → «Acceder con Google» → «Ejecutar prueba sintética»; al volver informa el estado. Si es `synthetic_success`, marcar la prueba y evaluar `cloud_gate_passed` con la matriz completa.
- **Nota para agentes:** el agente puede entrar a la web desde su navegador integrado eligiendo la cuenta de Google ya abierta (sin contraseña); los secretos siempre los pega el propietario en Edge.

## 12. Relevo — 30/09/2026 16:03 (UTC-5), host cloud `384c4b694068` (Codex)

- **REAL (Git):** `git fetch origin` realizado; base `1afaffd` (PR #20). Rama `feat/mobile-autorun`, último commit de implementación publicado `5c93327`; el commit de documentación de este relevo se consulta con `git log -1 origin/feat/mobile-autorun`. Pendiente autorización explícita del propietario para fusionar el PR.
- **Cambios:** autorun en `web/app.js` para la prueba sintética fija; servidor sin cambios. Solo ids de 32 hex minúsculas, Google silencioso, un reintento interactivo validando `state`, validación del propietario en servidor antes del envío, sondeo existente y cancelación por desconexión. Se consume el id pendiente una vez antes de enviar, incluso si se pierde la respuesta; consultar su checkpoint con el id que queda en el campo. Token de Google solo en memoria. Documentación de estado/matriz actualizada.
- **SIMULADA:** 61 Python + 39 Node (22 checkpoint, 17 web) aprobadas; comprobación sintáctica Node aprobada. Ninguna evidencia nueva de ejecución en Render ni en móvil.
- **REAL (informado por el propietario, actualización posterior):** celular conectado a Windows, depuración USB activada y `adb devices` muestra `device` después del bloque de instalación oficial entregado en chat. Sin lectura directa por el agente; modelo y versión de Android pendientes. No afirmar ejecución móvil de Zeruel a partir de esta conexión.
- **Desplegado:** no comprobado desde este entorno. Histórico: Render Live con PR #18; autorun de esta rama no desplegado. Autodeploy desactivado: tras autorización y fusión, usar «Manual Deploy → Deploy latest commit» y leer eventos/logs como texto.
- **Bloqueos:** el agente trabaja en `/workspace/zeruel` en Linux cloud, no en el Windows Celeron. No tiene acceso a su USB, navegador con sesiones del propietario ni eventos `Get-WinEvent`. Continuar las fases A–D desde un contexto que sí tenga acceso local, o mediante acciones concretas del propietario. No pedir secretos; contraseña/2FA exclusivamente por el propietario. No cambiar timeout del celular sin permiso y valor original; no apagar las PCs.
- **REAL (investigación documental posterior):** ADB inalámbrico requiere computadora y Android en la misma red ([Android](https://developer.android.com/tools/adb#connect-to-a-device-over-wi-fi)); no enlaza por sí solo este cloud con el USB de Windows. El entorno sigue con `vpn_configured:false` y sin destinos TCP autorizados. La [documentación de OpenAI](https://developers.openai.com/codex/enterprise/cloud-local-access) distingue ejecución Local y Cloud y señala que los chats anteriores conservan su modo: continuar en un chat Local del Windows es la ruta que aprovecha ADB existente sin otro agente local. El catálogo también ofrece Remote Desktop Commander para terminal remota, sin conexión confirmada ni consumo del agente Windows verificado; no se instaló ni se abrió ADB a Internet. Pendiente localizar la opción Local en la interfaz del propietario; no se creó otro chat.
- **REAL (actualización posterior, conector remoto):** el catálogo ahora confirma Remote Desktop Commander instalado. El propietario intentó `npx @wonderwhy-er/desktop-commander@latest remote` y aportó error PowerShell: `npx` no reconocido. Sin herramienta remota callable ni agente Windows conectado. El [README oficial](https://github.com/wonderwhy-er/DesktopCommanderMCP/blob/main/src/remote-device/README.md) requiere Node ≥18 y proceso persistente; la versión npm 0.2.52 tiene dependencias Puppeteer/Sharp y un servidor MCP hijo. No instalar a ciegas: localizar primero Node/npm/npx portable de Codex con consultas de rutas concretas, sin búsqueda recursiva. Conservar las restricciones de recursos y procesos del propietario; no pedir ni publicar códigos de autorización o secretos.
- **REAL (actualización posterior, runtime Windows):** propietario confirmó Node portable `v24.19.0` y ausencia de npm/npx en las rutas concretas. `tools/install-portable-npm.ps1` instala solo npm 10.9.4 portable (2 714 849 bytes descargados; SHA-512 fijado), define `npx` solo en esa consola y no arranca el agente remoto. **REAL en Linux:** integridad y versiones de npm/npx verificadas. PowerShell/Windows aún sin prueba; solicitar resultado `10.9.4`. El conector sigue sin enlace operativo comprobado. Evitar descargar Chromium o lanzar varios agentes; el cliente remoto oficial tiene dependencias y un hijo MCP persistente. Una implementación propia sin npm sería otro cliente del protocolo y no se creó.
- **REAL (actualización posterior, bootstrap completado):** propietario pegó la salida completa: npm/npx `10.9.4` listo en Windows. Captura de cuenta y catálogo confirman Remote Desktop Commander conectado/instalado. Aquí siguen sin aparecer herramientas remotas del complemento. `tools/start-remote-device.ps1` está preparado con versión 0.2.52, sin descarga de Chromium ni persistencia de tokens; no se ejecutó ni se verificó en Windows. Exige `-AllowAdditionalProcesses` para respetar la autorización pendiente: el cliente oficial abre agente y MCP hijo, además de ADB existente. Pedir excepción temporal citando la regla original de un proceso en segundo plano antes de lanzarlo. Otras dependencias y consumo aún sin medir; no prometer que este chat podrá controlarlo hasta disponer de herramientas y una llamada real. Alternativa de menor carga: ejecución Local del Windows con ADB existente.
- **Pendientes exactos:** nivel Pro verificado oficialmente; cuota/respaldo sin forzar gasto; concurrencia; bloqueo expirado; trabajador antiguo; escritura parcial; `recover` real; respuesta perdida; recuperación de checkpoint anterior tras suspensión; renovación en proceso vivo >1 h sin reinicio; ejecución móvil con ambos Windows apagados. También otra identidad Google real rechazada y HMAC/replay real. La matriz sigue parcial, `cloud_gate_passed=false`.
- **Próximo paso exacto:** comprobar modelo y Android por ADB; `device` ya informado por el propietario. Si falla dos veces, detener la fase A. Abrir la web en el móvil, entrar con Google y lanzar la prueba manual con PCs encendidas, registrar id y recuperar checkpoint autenticado. Para autorun: aprobar el PR concreto, desplegar manualmente, comprobar primero nuevo id con PCs encendidas; validar N=60 y N=120 con desconexión antes de N=600 y apagado por el propietario.
- **DeepSeek:** US$0; acumulado histórico ≤ US$0,2143.
- **Procesos activos del agente:** ninguno. Sin Docker, instalaciones pesadas, capturas, lecturas de pantalla, scripts en el móvil ni keepalive en esta sesión. Si el propietario ejecutó el bloque de instalación, ADB puede mantener su servidor local; comprobarlo antes de otro proceso en segundo plano.
