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
- El dashboard de Render solicitó iniciar sesión. La opción GitHub requirió conceder acceso nuevo a la aplicación Render; no se concedió. Por ello no se verificó de nuevo el commit Live. Última versión **documentada**, no reconfirmada hoy: `6f07373`, `blocked_persistence`.
- Este relevo actualiza documentación y corrige la codificación mixta previa de `STATUS.md` y `first-milestone.md`; no toca código de ejecución, credenciales, expedientes ni servicios. Pasaron 22 pruebas Python y 9 Node locales; no se hicieron pruebas de integración real ni de inferencia. `cloud_gate_passed` sigue `false`.
- Próximo paso externo: aceptar personalmente las condiciones de Google Cloud si se desean usar sus servicios; después revisar el proyecto estándar concreto y confirmar la vinculación irreversible del script. Para inspeccionar Render se necesitará iniciar sesión sin ampliar permisos inesperados. Ningún proceso nuevo debe permanecer activo.
