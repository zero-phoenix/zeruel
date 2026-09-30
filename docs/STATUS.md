# Estado del primer hito — 29 de septiembre de 2026, Lima

## Comprobado

- Repositorio creado por Antigravity; código del primer hito publicado por Codex.
- Gemini CLI oficial `0.62.0` instalado en el directorio de trabajo aislado. Integridad SHA-512 verificada; archivo descargado: 20.787.241 bytes.
- El CLI instalado informa versión `0.62.0`.
- 22 pruebas Python y 9 pruebas Node pasan localmente. Cubren autenticación del servicio, exclusión de secretos, bloqueo de rutas facturables, cuota, concurrencia, HMAC, replay, persistencia simulada e idempotencia.
- La prueba real local se detiene con `blocked_auth`, sin llamar al modelo.
- Acceso a Render recuperado; workspace visible: My Workspace. Servicio `zeruel-synthetic-probe` creado con Docker, rama main, Free (US$0/mes, 0.1 CPU, 512 MB) y despliegue automático desactivado. No se conectó un proveedor Git adicional: se usó el repositorio público.
- Render informa `Deploy succeeded|Live` para el commit `6f07373`. Instalación del CLI oficial y SHA-512 comprobadas también durante la construcción en nube.
- Aplicación disponible en https://zeruel-synthetic-probe.onrender.com. Acceso autenticado probado en la interfaz; la prueba real se detiene con `blocked_persistence` antes de ejecutar Gemini, porque el punto de control externo aún no está configurado.
- Clave de acceso configurada como secreto de Render. Ninguna credencial de Gemini se ha cargado en Render.
- Plan de extensión para Edge, Chrome, Brave y Firefox registrado en `docs/browser-extension-plan.md`; no se ha implementado ni activado captura.
- No se añadió tarjeta, no se habilitó facturación, no se cargaron expedientes y no se activó observación del escritorio. No queda un proceso de Gemini esperando el acceso.

## Pendiente y bloqueante

- Autenticación oficial de Gemini CLI con la cuenta del propietario y verificación del nivel de suscripción.
- Autorización y configuración segura de las credenciales remotas y del punto de control Apps Script.
- Prueba real de inferencia, renovación, suspensión, reinicio, persistencia externa y uso móvil con equipos apagados.
- Mediciones de CPU/RAM en Render. Las pruebas sintéticas no son una medición del rendimiento del agente completo.

**El primer hito NO está superado. El resto de la implementación permanece condicionado a su validación, según el plan aprobado.**

El archivo `docs/ci-template.yml` es una plantilla y no está activo. Las pruebas anteriores se ejecutaron localmente; el primer hito aún carece de validación real de Google.

## Acceso privado: avance posterior

- Propietario exclusivo requerido; cuentas secundarias pendientes. No se publicó la configuración web con acceso Cualquiera.
- Código actualizado guardado en Apps Script: entrada web deshabilitada, función privada con comprobación de identidad y manifiesto limitado a userinfo.email. Propiedad privada del propietario configurada.
- Transporte Python para API OAuth preparado y probado con respuestas simuladas. Deshabilitado el antiguo transporte web.
- Pendientes: proyecto Cloud estándar común, cliente OAuth, implementación API Solo yo, permisos reales, almacenamiento autorizado de credenciales y despliegue actualizado en Render. La versión Live anterior sigue en blocked_persistence.

## Relevo desde DESKTOP-B6D864U — 29 de septiembre de 2026, Lima

- Checkout nuevo y limpio en `C:\Users\D\Documents\Codex\zeruel`, basado en `main` `63e77959eb5f805ac5caa17cba73586dfd51f59d`. La modificación local de `README.md` en la PC original no se tocó y debe inspeccionarse mañana antes de sincronizar.
- Google anunció oficialmente que Gemini CLI dejó de servir solicitudes de Google AI Pro el 18/06/2026: https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/ . La inferencia de Zeruel permanece bloqueada bajo el fundamento actual. No se autorizaron otros CLI, Gemini API ni Vertex.
- La consola de Google Cloud, abierta con `david.chavez.nge@gmail.com`, muestra una aceptación inicial de Condiciones del Servicio. No se aceptaron, no se creó proyecto ni se habilitó facturación. Apps Script sigue visible bajo la cuenta principal; no se vinculó un proyecto estándar ni se desplegó el ejecutable de API.
- Se inició sesión en Render con `david.chavez.nge@gmail.com` sin conceder acceso nuevo a la aplicación GitHub. El dashboard reconfirmó **Live** en `6f073737d81057fcdc7f77b5941e535ea4e6feaf`, plan **Free**, Docker y rama `main`. El estado funcional `blocked_persistence` es el último resultado de la prueba previa; no se repitió hoy la llamada a la aplicación.
- Este relevo actualiza documentación y corrige la codificación mixta previa de `STATUS.md` y `first-milestone.md`; no toca código de ejecución, credenciales, expedientes ni servicios. Pasaron 22 pruebas Python y 9 Node locales; no se hicieron pruebas de integración real ni de inferencia. `cloud_gate_passed` sigue `false`.
- Próximo paso externo: aceptar personalmente las condiciones de Google Cloud si se desean usar sus servicios; después revisar el proyecto estándar concreto y confirmar la vinculación irreversible del script. El commit desplegado en Render permanecerá en `6f07373` hasta decidir un despliegue manual; el despliegue automático está desactivado. Ningún proceso nuevo debe permanecer activo.

## Recuperación segura — DESKTOP-B6D864U, 29/09/2026

- Trabajo en rama `fix/checkpoint-recovery`, basado en `main` `a295068`. Se conserva intacta la modificación pendiente del README de la PC original.
- Cada bloqueo lleva una generación privada. Una respuesta antigua no puede cerrar otro bloqueo; repetir el mismo resultado solo reintenta persistencia. Cambiar el resultado se rechaza.
- La intención se registra antes de inferir y el reporte se conserva localmente con escritura atómica. Una escritura parcial, reinicio sin reporte o bloqueo vencido queda incierto y no vuelve a invocar el modelo. Render Free puede perder el registro local; el bloqueo remoto conserva la pausa. Recuperar una operación vencida exige diagnóstico del propietario; no existe reinicio automático de inferencia.
- Corrección de la auditoría: las 30 pruebas Python y 14 Node de esta etapa no cubrían renovación entre claim y complete, trabajador antiguo frente a otra lease, respuesta HTTP perdida explícita ni fallo en la segunda escritura del claim. Esas brechas se cubren en la etapa siguiente.
- Corregida la contradicción del protocolo: OAuth ya está implementado; falta validar su identidad y permisos reales.
- Google Cloud sigue mostrando condiciones iniciales pendientes en la cuenta principal. Se solicitó confirmación antes de aceptarlas; ningún proyecto estándar creado, API habilitada o script vinculado por este trabajo.
- La clave DeepSeek expuesta y el secreto del checkpoint deben rotarse privadamente antes de su uso. No se realizaron llamadas DeepSeek: consumo de esta etapa US$0. El presupuesto autorizado de US$1 se limita a asistencia sobre código público, nunca inferencia de Zeruel.
- No se actualizó Apps Script ni Render. Último despliegue verificado: `6f07373`; `cloud_gate_passed=false`. No se cargaron credenciales remotas ni se habilitó facturación.
- Próximo paso: completar rotación privada y autorización de condiciones; preparar proyecto Cloud común y presentar su identificador antes de confirmar la vinculación irreversible. La inferencia sigue bloqueada por incompatibilidad publicada de Gemini CLI/Google AI Pro. No hay procesos nuevos que deban mantenerse activos.

## Recuperación manual del propietario — Claude, DESKTOP-B6D864U, 29/09/2026

- Problema: `complete` rechaza con razón el primer guardado después de los 180 s aunque exista registro local, y una lease incierta bloquea todos los IDs futuros. No había salida segura.
- Solución: acción `recover` en Apps Script y comando local `scripts/recover_checkpoint.py`, fuera del servidor HTTP. Exige confirmación explícita del propietario (`--confirm-worker-finished`), la generación exacta y que la lease original haya vencido. Nunca llama al modelo ni concede otra inferencia.
  - Con informe local durable: guarda ese resultado canónico y su fingerprint, marcado `recovered`, y luego retira solo su bloqueo.
  - Sin informe: cierre terminal `terminal_unknown` (tombstone). Nunca éxito; el mismo ID no puede reclamarse ni completarse después.
  - Repetir el mismo resultado es idempotente; otro resultado, otra generación o `--unknown` con informe existente se rechazan. No se borran registros ni se prolonga `expires`.
- **Límite:** sin informe ni resultado durable no se puede reconstruir un resultado y asegurar a la vez que no haya duplicados. Por eso ese caso se cierra como desconocido y no se reinfiere el mismo ID.
- Evidencia **simulada** (Node `vm` y mocks Python): pasan 39 pruebas Python y 22 Node. Cubren vencimiento exacto, confirmación y generación, informe durable, tombstone, trabajador antiguo frente a una lease nueva, segunda escritura del claim fallida, respuesta perdida tras escribir, recuperación parcial, renovación OAuth entre claim y complete, refresh revocado sin filtrar secretos, y ausencia de `recover` en el servidor. Tres mutaciones de las guardas de `recover` son derribadas. **No prueban permisos efectivos de Google ni persistencia real.**
- Puerta del proveedor revalidada hoy contra la fuente oficial: sin restauración de Gemini CLI para Google AI Pro. Inferencia bloqueada; `cloud_gate_passed=false`.
- Sin cambios en Apps Script remoto, Google Cloud ni Render: requieren confirmaciones del propietario. DeepSeek no se usó (clave pendiente de rotación privada): consumo US$0, sin reservas abiertas.
