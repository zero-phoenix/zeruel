# Prompt de continuación — Claude Opus 5.5 (esfuerzo bajo), celular por USB

**Cómo usarlo:** abre una sesión nueva de Claude Code en la carpeta
`C:\Users\Admin\Documents\Codex\2026-09-29\github-plugin-github-openai-curated-remote\work\zeruel`,
elige Opus 5.5 con esfuerzo bajo y pega todo lo que está entre las líneas.
Revisado por dos revisores independientes (técnico y de seguridad) el 30/09/2026.

---

Eres el ingeniero principal de **Zeruel** (repositorio `zero-phoenix/zeruel`, checkout en la carpeta actual). Continúas el trabajo de otro agente. Responde en español, con mensajes cortos. Etiqueta toda evidencia como **REAL** o **SIMULADA**; nunca declares algo operativo sin evidencia real.

## 0. Lee primero (sin ejecutar nada más)
1. `git fetch` y `git log --oneline -5` (al día con `origin/main`).
2. `docs/HANDOFF.md`: secciones 2 (reglas), 3 (estado), 7 (trampas) y 11 (último relevo).
3. `docs/STATUS.md` (final) y la matriz de `docs/first-milestone.md`.
4. **Si existe `$env:USERPROFILE\.zeruel-private\c4-state.json`**, vienes de un apagado: ve directo a la Fase C5.

## 1. Reglas duras (prioridad sobre todo lo demás)
- **La PC es un Celeron que se congela.** Elige siempre lo más ligero. Prohibido:
  - capturas de escritorio, herramientas computer-use y scrcpy;
  - Docker, instalaciones pesadas y búsquedas recursivas en disco;
  - más de **un** proceso en segundo plano (el servidor `adb` cuenta: ciérralo con `& $adb kill-server` al terminar cada fase).
  Lee el celular como **texto**, nunca como imagen, con 3 s o más entre lecturas.
- **Credenciales:** nunca escribas contraseñas, tokens ni secretos en ningún campo, ni los pidas por chat. Si Google pide contraseña o 2FA, detente y pídeselo al propietario.
- **Nunca apagues ni reinicies las PCs ni el celular** (nada de `adb reboot`). El propietario apaga las PCs.
- **Ajustes del celular:** solo con permiso explícito; anota el valor original y restáuralo.
- **GitHub:** ramas y PR. Pide autorización una sola vez, en un único mensaje con la lista de PR. Fusiona solo los que el propietario autorice por número.
- **Render:** tras fusionar a `main`, «Manual Deploy → Deploy latest commit» desde tu navegador integrado (el autodeploy está desactivado).
- **Límites del servicio:**
  - Apps Script guarda como máximo 50 pruebas (`paused_storage_limit`). Esta sesión usa solo las imprescindibles: B, C1, dos en C3, C4 y D.
  - Si aparece `paused_uncertain`, `paused_storage_limit` o `blocked_*`, detente e informa. No ejecutes `recover` sin el propietario.
- **Bucles:** todos con límite. `adb devices` como máximo 10 intentos (cada 3 s). Lectura de un resultado, como máximo 40 lecturas. Si fallas dos veces, detente y explica.

## 2. Utilidades (las variables NO persisten entre comandos)
- **Encabezado de cada comando:**
  `$ProgressPreference='SilentlyContinue'; $adb="$env:USERPROFILE\platform-tools\adb.exe";`
  Llama siempre con `& $adb ...`. En PowerShell usa `$env:USERPROFILE` y `$env:TEMP`, nunca `%USERPROFILE%`.
- **Id nuevo de 32 hex:** `-join ((1..32) | % { '{0:x}' -f (Get-Random -Maximum 16) })`.
- **Leer la pantalla** (en UTF-8; `exec-out cat` corrompe «é» y «·» en PS 5.1):
  1. `& $adb shell uiautomator dump /sdcard/zr.xml | Out-Null`
  2. `& $adb pull /sdcard/zr.xml "$env:TEMP\zr.xml" | Out-Null`
  3. `& $adb shell rm /sdcard/zr.xml`
  4. `$x=[IO.File]::ReadAllText("$env:TEMP\zr.xml")`
  Busca fragmentos ASCII («Acceder con Google», «Ejecutar prueba», «Completado», «Consultar punto») en `text=` o `content-desc=` y toma `bounds="[x1,y1][x2,y2]"`. Si el volcado no trae el contenido de Chrome, repítelo una vez tras 3 s; si sigue sin traerlo, pide al propietario ese toque concreto. Borra `$env:TEMP\zr.xml` al terminar cada fase: puede contener datos de pantalla.
- **Pulsar:** `& $adb shell input tap <cx> <cy>`, en el centro de los límites.
- **Abrir la web en Chrome:** `& $adb shell am start -a android.intent.action.VIEW -p com.android.chrome -d "<url>"`.
- **Consultar un resultado** (nunca abras `/api/checkpoint/<id>` como URL: sin cabecera responde 401):
  - En tu navegador integrado, abre la web, pulsa «Acceder con Google», elige la cuenta del propietario y ejecuta en la página:
    `await (await fetch('/api/checkpoint/<id>',{headers:{Authorization:'Google '+idToken}})).text()`.
  - El `idToken` caduca a la hora: si recibes 401, vuelve a entrar.
- **Epoch a hora local:** `[DateTimeOffset]::FromUnixTimeSeconds(<n>).LocalDateTime`.

## 3. Fase A — ADB
1. Pide al propietario (un solo mensaje):
   - Ajustes → Acerca del teléfono → pulsar 7 veces «Número de compilación».
   - Ajustes → Sistema → Opciones de desarrollador → activar «Depuración USB».
   - Puede mantener el anclaje USB.
2. Pide permiso para descargar el paquete oficial `https://dl.google.com/android/repository/platform-tools-latest-windows.zip` (~7 MB). Con el sí:
   - `Invoke-WebRequest -UseBasicParsing <url> -OutFile "$env:TEMP\pt.zip"`
   - `Expand-Archive "$env:TEMP\pt.zip" -DestinationPath $env:USERPROFILE -Force`
   - `Remove-Item "$env:TEMP\pt.zip"`
   Así adb queda en `$env:USERPROFILE\platform-tools\adb.exe`.
3. `& $adb devices`: pide al propietario que acepte «¿Permitir depuración USB?» y marque «Permitir siempre». Máximo 10 intentos hasta ver `device`.
4. `& $adb shell getprop ro.product.model` y `& $adb shell getprop ro.build.version.release`.
5. Confirma que el celular tiene **datos móviles propios**: `& $adb shell settings get global mobile_data` debe dar 1, y el propietario confirma que no navega por Wi-Fi de ninguna de las PCs.

## 4. Fase B — Prueba desde el celular (PC encendida)
1. Abre la web en Chrome.
2. Pulsa «Acceder con Google», la cuenta del propietario y «Ejecutar prueba sintética».
3. Lee hasta «Completado» (máximo 40 lecturas) y anota el `id`.
4. Confírmalo con «Consultar un resultado» (sección 2).
Evidencia **REAL** de «lanzada desde el móvil» (con la PC encendida).

## 5. Fase C — Tarea desde el celular con ambos Windows apagados
**C1. Ejecución automática** (PR en `web/app.js`; el servidor no cambia):
- Extrae el cuerpo de `$('google').onclick` a `async function startGoogle(prompt)`; el botón llama a `startGoogle('select_account')`.
- Haz que `connect()` devuelva `true` solo si `/api/status` respondió bien.
- `finishGoogle()` pasa a ser `async`, y se llama `finishGoogle()` sin esperar al final del script.
- Al cargar, si `location.hash` coincide con `^#autorun=([a-f0-9]{32})$`:
  - guarda el id en `sessionStorage` (`zeruel_autorun`) y borra el hash con `history.replaceState`;
  - llama a `startGoogle('none')`.
- En `finishGoogle()`, valida `state` también en errores. Solo ante `interaction_required`, `login_required` o `consent_required`, con autorun pendiente y sin reintento previo: marca `zeruel_autorun_retry` y llama a `startGoogle('select_account')`.
- Tras `if (await connect())` con autorun pendiente:
  1. borra `zeruel_autorun` **antes** de lanzar;
  2. pon el id en el campo `task`;
  3. `const d = await request('/api/probe', {id})`;
  4. si `d.state === 'active'`, usa el `poll` existente.
- Comprueba con `& "$env:USERPROFILE\.cache\codex-runtimes\codex-primary-runtime\dependencies\node\bin\node.exe" --check web\app.js` y `python -m unittest discover -s tests`.
- PR, autorización, fusión y despliegue.
- **Prueba REAL con la PC encendida:** abre `<web>/#autorun=<id nuevo>` y **no toques el celular**. Solo cuenta si llega a `synthetic_success` sin ningún toque. Si aparece el selector de cuentas o una pantalla de consentimiento, detente y consulta al propietario antes de seguir.

**C2. Pantalla despierta** (antes de cualquier lanzamiento programado): con permiso,
- `& $adb shell settings get system screen_off_timeout`: anota el valor;
- `& $adb shell settings put system screen_off_timeout 1800000`;
- el propietario deja el celular desbloqueado en la pantalla de inicio, sin tocarlo.
Sin esto, el reposo detiene `sleep` y el bloqueo impide que Chrome ejecute la página.

**C3. Programar el lanzamiento:**
1. Crea el script fuera del repositorio:
   `$f="$env:TEMP\zr.sh"; [IO.File]::WriteAllText($f, "sleep N`ninput keyevent KEYCODE_WAKEUP`nam start -a android.intent.action.VIEW -p com.android.chrome -d '<web>/#autorun=<id>'`n")`
2. `& $adb push $f /data/local/tmp/zr.sh` y `& $adb shell "nohup sh /data/local/tmp/zr.sh >/dev/null 2>&1 &"`.
3. Valida con N=60 y el cable conectado. Después con N=120, pidiendo al propietario que **desconecte el cable** justo tras programarlo y lo reconecte a los 3 min. Consulta el resultado de cada id.
4. **Plan B**, si no sobrevive a la desconexión: pide al propietario que guarde `<web>/#autorun=<id>` como marcador y lo abra con un toque cuando las PCs estén apagadas. Sigue siendo «lanzada desde el móvil».

**C4. Ejecución real:**
1. Genera un id nuevo y programa N=600.
2. **Antes de avisar**, guarda en `$env:USERPROFILE\.zeruel-private\c4-state.json` (fuera del repositorio):
   - el id;
   - la hora programada (epoch UTC);
   - el `screen_off_timeout` original;
   - la URL y si se usó el plan B.
   Muéstraselo también al propietario en el chat.
3. Di al propietario: «Desconecta el cable y apaga ahora las dos PCs; enciéndelas dentro de 20 min o más. Al volver, abre una sesión nueva con este mismo prompt».

**C5. Al volver** (sesión nueva):
1. Lee `c4-state.json` y consulta el resultado del id.
2. **Criterio de éxito:** `state` es `synthetic_success` y `completed` cae entre el apagado y el arranque de esta PC. Busca con `Get-WinEvent -FilterHashtable @{LogName='System'; StartTime=<hora programada − 1 h>}` y filtra estos Id:
   - 1074 (apagado);
   - 12 (Kernel-General, arranque);
   - 27 (Kernel-Boot);
   - 1 (Power-Troubleshooter, reanudación);
   - 41 y 6008 (apagado brusco).
   Con el inicio rápido de Windows 11 no aparecen 6005/6006: no los exijas.
3. El propietario confirma por chat que la otra PC también estaba apagada durante ese intervalo.
4. Restaura `screen_off_timeout`, ejecuta `& $adb shell rm /data/local/tmp/zr.sh` y borra `c4-state.json` y `$env:TEMP\zr.sh`.
5. Evidencia **REAL** de «Móvil y equipos apagados» solo si se cumplen los tres puntos.
6. Conserva el autorun: el propietario decidió que sea permanente el 30/09/2026. Sigue exigiendo autenticación del propietario; no autoriza ninguna tarea fuera de la prueba sintética fija.

## 6. Fase D — Renovación del token OAuth en un proceso vivo
El token se pide en la **primera llamada al checkpoint** del proceso, no al arrancar, y se renueva unos 54 min después.
1. En los eventos de Render anota la hora del último arranque.
2. Haz una consulta de resultado (sección 2) de un id existente. Esa hora es **T1**.
3. Lanza **un** proceso en segundo plano (adb cerrado) que llame a `/healthz` cada 10 min hasta T1 + 70 min.
4. A partir de T1 + 61 min, vuelve a entrar con Google y lanza una prueba. Exige `synthetic_success` con `checkpoint_saved: true`.
5. Confirma en Render que no hubo reinicio entre el arranque y la prueba. Solo entonces es evidencia **REAL** de «Renovación».
6. No fuerces la cuota agotada (gasta la suscripción): queda «no probada», con motivo.

## 7. Cierre
- **Limpieza:**
  - `& $adb kill-server`;
  - borra `$env:TEMP\zr.xml` y `$env:TEMP\zr.sh`;
  - ajustes del celular restaurados;
  - ningún proceso en segundo plano.
- Actualiza `docs/STATUS.md`, `docs/HANDOFF.md` (sección 12) y la columna de estado de `docs/first-milestone.md`.
- `cloud_gate_passed` pasa a `true` solo si **todas** las filas tienen evidencia REAL y el propietario lo aprueba. Si no, lista lo que falta.
- PR con los documentos; fusión solo con autorización.
- Mensaje final «Relevo»: fecha y host; cambios; rama y último commit; versión desplegada; pruebas reales y simuladas; bloqueos; próximo paso exacto; procesos activos (ninguno).

---
