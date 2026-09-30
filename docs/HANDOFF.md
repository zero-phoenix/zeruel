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
| Render `zeruel-synthetic-probe` (`srv-dau6eq9srm7s73avnsb0`) | Live en `6f07373` (código viejo), autodeploy desactivado | Dashboard: https://dashboard.render.com/web/srv-dau6eq9srm7s73avnsb0 |
| Apps Script «Zeruel — punto de control sintético» | Código remoto viejo; proyecto Cloud predeterminado | https://script.google.com/home/projects/1CBRJQOLkMf-Fy6JVpsj0fqKx-9KyjeKbQw9wrsFE3F_lWjzHpQdRsxth/edit |
| Google Cloud | Condiciones aceptadas por el propietario. Proyecto `zeruel-checkpoint-09292354` (nº 1096719789550) creado, **sin vincular** | Tiene 24 APIs activas por defecto; facturación **no verificada** |
| DeepSeek | ≤ US$0,2143 gastados de US$1 | `docs/reviews/` |

## 4. Próximos pasos (fase 2), en orden
1. **Proyecto Cloud:** `gcloud billing projects describe zeruel-checkpoint-09292354` (si pregunta por habilitar la API de facturación, responde con `--quiet`/no y verifica en la consola). Revisa las 24 APIs; deja solo las necesarias (`script.googleapis.com`). Sin facturación.
2. **Vincular Apps Script** (Configuración del proyecto → cambiar proyecto → número 1096719789550). **Irreversible**: revoca autorizaciones y no permite volver al predeterminado. Pide confirmación al propietario inmediatamente antes.
3. Subir `apps-script/SyntheticCheckpoint.gs` y manifiesto (solo `userinfo.email`); propiedades privadas `ZERUEL_OWNER_EMAIL` y `ZERUEL_CHECKPOINT_SECRET` (aleatorio ≥ 32, generado por script sin mostrarlo). Implementar como **Ejecutable de API, Solo yo**.
4. Cliente OAuth del propietario con `userinfo.email` (+ el mínimo que exija `scripts.run`; justificar cualquier ámbito extra antes). Obtener refresh token por flujo oficial.
5. **Render:** autorización del propietario para almacenar secretos; cargar `ZERUEL_AGY_OAUTH_TOKEN`, `ZERUEL_CHECKPOINT_DEPLOYMENT_ID`, `ZERUEL_CHECKPOINT_SECRET`, `ZERUEL_CHECKPOINT_OAUTH_JSON` y, si existe, `ZERUEL_GEMINI_FREE_KEY`, sin imprimirlos. Despliegue manual de `main`.
6. **Matriz real** con datos sintéticos: propietario acepta; otra identidad rechazada; HMAC/replay; renovación de token; reinicio y suspensión de Render; idempotencia; `recover` real sobre una lease vencida; cuota agotada + respaldo; tarea lanzada desde el móvil con ambos Windows apagados (coordinar con el propietario; no los apagues tú). Registrar tiempo, RAM y CPU.
7. Actualizar `docs/STATUS.md` con evidencia real y límites.

## 5. Lo que NO está en el repositorio (debe recrearse)
- **Sesión de `agy`:** el propietario inicia sesión otra vez. En Windows con Docker: `docker build -t zeruel .` y luego `tools/agy-login.ps1` (abre el enlace completo y pasa el código; guarda la sesión en `%USERPROFILE%\.zeruel-private\agy-home`). En Linux/macOS basta ejecutar `agy` en una terminal.
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

## 6. DeepSeek como asistente
`python tools/deepseek_assist.py <prompt> <salida> [tokens]`. Solo código público, diffs depurados y preguntas acotadas; nunca conversaciones, capturas, expedientes, memoria ni secretos. Reserva previa del coste máximo; una llamada incierta conserva la reserva y no se reintenta. Usa ≥ 60 000 tokens de salida (el razonamiento consume el tope). Verifica cada hallazgo antes de aceptarlo; registra aceptados y rechazados en `docs/reviews/`.

## 7. Trampas conocidas
- Windows + Git Bash: usa `MSYS_NO_PATHCONV=1` con `docker` (si no, `/root` se convierte en `C:/...`). Evita comillas anidadas complejas en heredocs; escribe scripts a archivo.
- `agy` exige terminal (TTY) para iniciar sesión y espera el código **60 s**. Las terminales parten la URL larga: ábrela completa (lo hace `tools/agy-login.ps1`).
- `agy --json-schema` se atasca con 0,1 CPU: no usarlo.
- `agy` pide el ámbito `cloud-platform` y descarga binarios auxiliares en `$HOME` (`webm_encoder`). Vigilar.
- `gcloud billing ...` puede quedarse esperando una respuesta interactiva: usa `--quiet` y ejecútalo solo.
- Fusionar un PR propio puede requerir aprobación del propietario.

## 8. Formato de cierre de cada sesión
Título «Relevo»: fecha y host; cambios; rama y último commit publicado; versión desplegada; pruebas reales y simuladas; gasto DeepSeek; configuración y bloqueos; próximo paso exacto; procesos que deben seguir activos. Actualiza este archivo y `docs/STATUS.md`.
