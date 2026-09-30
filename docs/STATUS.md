# Estado del primer hito â€” 29 de septiembre de 2026, Lima

## Comprobado

- Repositorio creado por Antigravity; cÃ³digo del primer hito publicado por Codex.
- Gemini CLI oficial `0.62.0` instalado en el directorio de trabajo aislado. Integridad SHA-512 verificada; archivo descargado: 20.787.241 bytes.
- El CLI instalado informa versiÃ³n `0.62.0`.
- 22 pruebas Python y 9 pruebas Node pasan localmente. Cubren autenticaciÃ³n del servicio, exclusiÃ³n de secretos, bloqueo de rutas facturables, cuota, concurrencia, HMAC, replay, persistencia simulada e idempotencia.
- La prueba real local se detiene con `blocked_auth`, sin llamar al modelo.
- Acceso a Render recuperado; workspace visible: My Workspace. Servicio `zeruel-synthetic-probe` creado con Docker, rama main, Free (US$0/mes, 0.1 CPU, 512 MB) y despliegue automÃ¡tico desactivado. No se conectÃ³ un proveedor Git adicional: se usÃ³ el repositorio pÃºblico.
- Render informa `Deploy succeeded|Live` para el commit `6f07373`. InstalaciÃ³n del CLI oficial y SHA-512 comprobadas tambiÃ©n durante la construcciÃ³n en nube.
- AplicaciÃ³n disponible en https://zeruel-synthetic-probe.onrender.com. Acceso autenticado probado en la interfaz; la prueba real se detiene con `blocked_persistence` antes de ejecutar Gemini, porque el punto de control externo aÃºn no estÃ¡ configurado.
- Clave de acceso configurada como secreto de Render. Ninguna credencial de Gemini se ha cargado en Render.
- Plan de extensiÃ³n para Edge, Chrome, Brave y Firefox registrado en `docs/browser-extension-plan.md`; no se ha implementado ni activado captura.
- No se aÃ±adiÃ³ tarjeta, no se habilitÃ³ facturaciÃ³n, no se cargaron expedientes y no se activÃ³ observaciÃ³n del escritorio. No queda un proceso de Gemini esperando el acceso.

## Pendiente y bloqueante

- AutenticaciÃ³n oficial de Gemini CLI con la cuenta del propietario y verificaciÃ³n del nivel de suscripciÃ³n.
- AutorizaciÃ³n y configuraciÃ³n segura de las credenciales remotas y del punto de control Apps Script.
- Prueba real de inferencia, renovaciÃ³n, suspensiÃ³n, reinicio, persistencia externa y uso mÃ³vil con equipos apagados.
- Mediciones de CPU/RAM en Render. Las pruebas sintÃ©ticas no son una mediciÃ³n del rendimiento del agente completo.

**El primer hito NO estÃ¡ superado. El resto de la implementaciÃ³n permanece condicionado a su validaciÃ³n, segÃºn el plan aprobado.**

El archivo `docs/ci-template.yml` es una plantilla y no estÃ¡ activo. Las pruebas anteriores se ejecutaron localmente; el primer hito aÃºn carece de validaciÃ³n real de Google.

## Acceso privado: avance posterior

- Propietario exclusivo requerido; cuentas secundarias pendientes. No se publicÃ³ la configuraciÃ³n web con acceso Cualquiera.
- CÃ³digo actualizado guardado en Apps Script: entrada web deshabilitada, funciÃ³n privada con comprobaciÃ³n de identidad y manifiesto limitado a userinfo.email. Propiedad privada del propietario configurada.
- Transporte Python para API OAuth preparado y probado con respuestas simuladas. Deshabilitado el antiguo transporte web.
- Pendientes: proyecto Cloud estÃ¡ndar comÃºn, cliente OAuth, implementaciÃ³n API Solo yo, permisos reales, almacenamiento autorizado de credenciales y despliegue actualizado en Render. La versiÃ³n Live anterior sigue en blocked_persistence.

## Relevo desde DESKTOP-B6D864U â€” 29 de septiembre de 2026, Lima

- Checkout nuevo y limpio en `C:\Users\D\Documents\Codex\zeruel`, basado en `main` `63e77959eb5f805ac5caa17cba73586dfd51f59d`. La modificaciÃ³n local de `README.md` en la PC original no se tocÃ³ y debe inspeccionarse maÃ±ana antes de sincronizar.
- Google anunciÃ³ oficialmente que Gemini CLI dejÃ³ de servir solicitudes de Google AI Pro el 18/06/2026: https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ . La inferencia de Zeruel permanece bloqueada bajo el fundamento actual. No se autorizaron otros CLI, Gemini API ni Vertex.
- La consola de Google Cloud, abierta con `david.chavez.nge@gmail.com`, muestra una aceptaciÃ³n inicial de Condiciones del Servicio. No se aceptaron, no se creÃ³ proyecto ni se habilitÃ³ facturaciÃ³n. Apps Script sigue visible bajo la cuenta principal; no se vinculÃ³ un proyecto estÃ¡ndar ni se desplegÃ³ el ejecutable de API.
- Se iniciÃ³ sesiÃ³n en Render con `david.chavez.nge@gmail.com` sin conceder acceso nuevo a la aplicaciÃ³n GitHub. El dashboard reconfirmÃ³ **Live** en `6f073737d81057fcdc7f77b5941e535ea4e6feaf`, plan **Free**, Docker y rama `main`. El estado funcional `blocked_persistence` es el Ãºltimo resultado de la prueba previa; no se repitiÃ³ hoy la llamada a la aplicaciÃ³n.
- Este relevo actualiza documentaciÃ³n y corrige la codificaciÃ³n mixta previa de `STATUS.md` y `first-milestone.md`; no toca cÃ³digo de ejecuciÃ³n, credenciales, expedientes ni servicios. Pasaron 22 pruebas Python y 9 Node locales; no se hicieron pruebas de integraciÃ³n real ni de inferencia. `cloud_gate_passed` sigue `false`.
- PrÃ³ximo paso externo: aceptar personalmente las condiciones de Google Cloud si se desean usar sus servicios; despuÃ©s revisar el proyecto estÃ¡ndar concreto y confirmar la vinculaciÃ³n irreversible del script. El commit desplegado en Render permanecerÃ¡ en `6f07373` hasta decidir un despliegue manual; el despliegue automÃ¡tico estÃ¡ desactivado. NingÃºn proceso nuevo debe permanecer activo.

## RecuperaciÃ³n segura â€” DESKTOP-B6D864U, 29/09/2026

- Trabajo en rama `fix/checkpoint-recovery`, basado en `main` `a295068`. Se conserva intacta la modificaciÃ³n pendiente del README de la PC original.
- Cada bloqueo lleva una generaciÃ³n privada. Una respuesta antigua no puede cerrar otro bloqueo; repetir el mismo resultado solo reintenta persistencia. Cambiar el resultado se rechaza.
- La intenciÃ³n se registra antes de inferir y el reporte se conserva localmente con escritura atÃ³mica. Una escritura parcial, reinicio sin reporte o bloqueo vencido queda incierto y no vuelve a invocar el modelo. Render Free puede perder el registro local; el bloqueo remoto conserva la pausa. Recuperar una operaciÃ³n vencida exige diagnÃ³stico del propietario; no existe reinicio automÃ¡tico de inferencia.
- CorrecciÃ³n de la auditorÃ­a: las 30 pruebas Python y 14 Node de esta etapa no cubrÃ­an renovaciÃ³n entre claim y complete, trabajador antiguo frente a otra lease, respuesta HTTP perdida explÃ­cita ni fallo en la segunda escritura del claim. Esas brechas se cubren en la etapa siguiente.
- Corregida la contradicciÃ³n del protocolo: OAuth ya estÃ¡ implementado; falta validar su identidad y permisos reales.
- Google Cloud sigue mostrando condiciones iniciales pendientes en la cuenta principal. Se solicitÃ³ confirmaciÃ³n antes de aceptarlas; ningÃºn proyecto estÃ¡ndar creado, API habilitada o script vinculado por este trabajo.
- La clave DeepSeek expuesta y el secreto del checkpoint deben rotarse privadamente antes de su uso. No se realizaron llamadas DeepSeek: consumo de esta etapa US$0. El presupuesto autorizado de US$1 se limita a asistencia sobre cÃ³digo pÃºblico, nunca inferencia de Zeruel.
- No se actualizÃ³ Apps Script ni Render. Ãšltimo despliegue verificado: `6f07373`; `cloud_gate_passed=false`. No se cargaron credenciales remotas ni se habilitÃ³ facturaciÃ³n.
- PrÃ³ximo paso: completar rotaciÃ³n privada y autorizaciÃ³n de condiciones; preparar proyecto Cloud comÃºn y presentar su identificador antes de confirmar la vinculaciÃ³n irreversible. La inferencia sigue bloqueada por incompatibilidad publicada de Gemini CLI/Google AI Pro. No hay procesos nuevos que deban mantenerse activos.

## RecuperaciÃ³n manual del propietario â€” Claude, DESKTOP-B6D864U, 29/09/2026

- Problema: `complete` rechaza con razÃ³n el primer guardado despuÃ©s de los 180 s aunque exista registro local, y una lease incierta bloquea todos los IDs futuros. No habÃ­a salida segura.
- SoluciÃ³n: acciÃ³n `recover` en Apps Script y comando local `scripts/recover_checkpoint.py`, fuera del servidor HTTP. Exige confirmaciÃ³n explÃ­cita del propietario (`--confirm-worker-finished`), la generaciÃ³n exacta y que la lease original haya vencido. Nunca llama al modelo ni concede otra inferencia.
  - Con informe local durable: guarda ese resultado canÃ³nico y su fingerprint, marcado `recovered`, y luego retira solo su bloqueo.
  - Sin informe: cierre terminal `terminal_unknown` (tombstone). Nunca Ã©xito; el mismo ID no puede reclamarse ni completarse despuÃ©s.
  - Repetir el mismo resultado es idempotente; otro resultado, otra generaciÃ³n o `--unknown` con informe existente se rechazan. No se borran registros ni se prolonga `expires`.
- **LÃ­mite:** sin informe ni resultado durable no se puede reconstruir un resultado y asegurar a la vez que no haya duplicados. Por eso ese caso se cierra como desconocido y no se reinfiere el mismo ID.
- Evidencia **simulada** (Node `vm` y mocks Python): pasan 39 pruebas Python y 22 Node. Cubren vencimiento exacto, confirmaciÃ³n y generaciÃ³n, informe durable, tombstone, trabajador antiguo frente a una lease nueva, segunda escritura del claim fallida, respuesta perdida tras escribir, recuperaciÃ³n parcial, renovaciÃ³n OAuth entre claim y complete, refresh revocado sin filtrar secretos, y ausencia de `recover` en el servidor. Tres mutaciones de las guardas de `recover` son derribadas. **No prueban permisos efectivos de Google ni persistencia real.**
- Puerta del proveedor revalidada hoy contra la fuente oficial: sin restauraciÃ³n de Gemini CLI para Google AI Pro. Inferencia bloqueada; `cloud_gate_passed=false`.
- Sin cambios en Apps Script remoto, Google Cloud ni Render: requieren confirmaciones del propietario. DeepSeek no se usÃ³ (clave pendiente de rotaciÃ³n privada): consumo US$0, sin reservas abiertas.

## Asistencia DeepSeek â€” 29/09/2026

- Clave nueva (rotada por el propietario) usada solo desde un script privado fuera del repositorio, con registro de gasto y reserva previa. Modelo `deepseek-flash` con esfuerzo `max`, sin herramientas, solo cÃ³digo pÃºblico.
- Dos llamadas: la primera agotÃ³ el tope en razonamiento sin respuesta. Coste mÃ¡ximo total US$0,092 del US$1 autorizado; sin reservas pendientes.
- Hallazgo aceptado: una respuesta JSON que no fuera objeto escapaba como `AttributeError` fuera de `persist`. Ahora falla cerrada como `ValueError`; prueba de regresiÃ³n derriba la versiÃ³n anterior.
- Rechazados: liberar automÃ¡ticamente registros `preparing` vencidos (contradice la recuperaciÃ³n exclusiva del propietario) y ACL de Windows para el journal (Render ejecuta Linux con permisos 0600).

## Cambio de motor a Antigravity CLI â€” 30/09/2026

- DecisiÃ³n del propietario: `agy` con Google AI Pro reemplaza a Gemini CLI; respaldo en capa gratuita de Gemini API tras cuota agotada.
- Evidencia **real** (contenedor local limitado a 512 MB y 0,1 CPU, como Render Free): el propietario iniciÃ³ sesiÃ³n con el enlace oficial; `agy` 1.2.14 respondiÃ³ `{"marker":"ZERUEL_OK","sum":42}` con Gemini 3.8 Flash (High). Imagen de Zeruel con usuario sin privilegios y `--sandbox`: `synthetic_success` en 20 s, pico 218 MB de RAM, 0,87 s de CPU.
- La sesiÃ³n de `agy` en Linux es un archivo (`.gemini/antigravity-cli/antigravity-oauth-token`), no el llavero: puede provisionarse como secreto de Render. Pide el Ã¡mbito `cloud-platform` ademÃ¡s de los de identidad.
- `--json-schema` se descartÃ³: `agy` lo implementa como herramienta interna y se atasca con 0,1 CPU (0 tokens tras 110 s). La respuesta se valida de forma estricta en Zeruel.
- Pendiente: vincular Apps Script al proyecto `zeruel-checkpoint-09292354`, cargar secretos en Render, desplegar y pruebas reales en nube. `cloud_gate_passed=false`.

## Relevo a otra computadora â€” 30/09/2026

- Relevo completo en `docs/HANDOFF.md`. Herramientas portables en `tools/` (asistente DeepSeek con registro de gasto; inicio de sesiÃ³n de `agy`). Revisiones en `docs/reviews/`.
- No viajan con el repositorio: la sesiÃ³n de `agy`, la clave DeepSeek y los secretos de la fase 2. Gasto DeepSeek acumulado â‰¤ US$0,2143.

## Fase 2 â€” 30/09/2026 ~11:40, DESKTOP-NLTEF6C (Claude Opus 5.5)
- **Real:** Apps Script vinculado por el propietario al proyecto estÃ¡ndar 1096719789550 (irreversible). Sin facturaciÃ³n. Las 24 APIs se conservan (sin facturaciÃ³n no generan coste; Analytics Hub no se toca).
- **Real:** cÃ³digo remoto = `apps-script/SyntheticCheckpoint.gs` de `main` (8 756 bytes LF); manifiesto con `oauthScopes: [userinfo.email]` y `executionApi.access: MYSELF`.
- **Real:** implementaciÃ³n Â«Ejecutable de API, Solo yoÂ» creada por el propietario. El ID se guardarÃ¡ solo como secreto de Render (`ZERUEL_CHECKPOINT_DEPLOYMENT_ID`), no en el repositorio.
- Pendiente: cliente OAuth + refresh token (paso 4), secretos en Render y despliegue manual (paso 5), matriz real (paso 6). `cloud_gate_passed=false`.

## Fase 2, pasos 4â€“5 â€” 30/09/2026 ~13:35, DESKTOP-NLTEF6C (Claude Opus 5.5)
- **Real:** pantalla de consentimiento Â«ZeruelÂ» en producciÃ³n (externa, solo `userinfo.email`; polÃ­tica en `docs/PRIVACY.md`). Cliente OAuth de escritorio creado; refresh token obtenido con `tools/get_checkpoint_oauth.py` y guardado fuera del repo (`~/.zeruel-private`). Google aÃ±adiÃ³ `openid`.
- **Real:** Render tiene `ZERUEL_CHECKPOINT_DEPLOYMENT_ID`, `ZERUEL_CHECKPOINT_OAUTH_JSON` y `ZERUEL_CHECKPOINT_SECRET` (valores pegados por el propietario; no leÃ­dos). Despliegue manual de `c1a1c92` **Live**; log Â«Zeruel synthetic probe readyÂ»; `/healthz` responde `cloud_gate_passed:false`.
- Pendiente: tarea sintÃ©tica real (requiere `ZERUEL_ACCESS_TOKEN` del propietario en la web) para confirmar que ya no devuelve `blocked_persistence`; sesiÃ³n `agy` y `ZERUEL_AGY_OAUTH_TOKEN`; resto de la matriz.
- Nota operativa: el panel de navegador integrado no acepta pegar desde el portapapeles de Windows; los secretos se pegan en Edge.

## Motor `agy` â€” 30/09/2026 ~14:20
- **Real:** sesiÃ³n `agy` creada por el propietario en un Codespace (`tools/agy-login-codespace.ps1`, sin Docker local): prueba sintÃ©tica `"status":"SUCCESS"` con `ZERUEL_OK`. SesiÃ³n copiada por el propietario a Render (`ZERUEL_AGY_OAUTH_TOKEN`); codespace borrado.
- **Real:** redespliegue manual de `dc7eced` Live, arranque sin errores.
- Pendiente: tarea sintÃ©tica ejecutada **en Render** (el propietario introduce `ZERUEL_ACCESS_TOKEN` en la web) y el resto de la matriz. `cloud_gate_passed=false`.

## Primera tarea completa en la nube â€” 30/09/2026 ~14:57
- **Real:** acceso a la web con Google solo para el propietario (PR #14, #15: redirecciÃ³n OpenID Connect con `state`/`nonce`; el servidor verifica `aud`, correo verificado del propietario y caducidad). El botÃ³n GIS/FedCM fallaba (Â«NetworkErrorÂ») y se sustituyÃ³.
- **Real (Render, `abâ€¦`â†’ commit de PR #15):** tarea `b59b8efdâ€¦` â†’ `synthetic_success`, motor `antigravity-cli`, modelo `gemini-3.8-flash-high`, `{"marker":"ZERUEL_OK","sum":42}`, 6,21 s, pico 211 956 KiB, 0,527 s CPU.
- **Real:** Â«Consultar punto de controlÂ» devuelve el mismo registro desde Apps Script (persistencia privada operativa).
- Pendiente de la matriz: otra identidad rechazada (en vivo), HMAC/replay, renovaciÃ³n de token, reinicio y suspensiÃ³n de Render, idempotencia, `recover` real, cuota agotada + respaldo, tarea desde el mÃ³vil con ambos Windows apagados. `cloud_gate_passed=false`.
