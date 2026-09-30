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

El acceso GitHub disponible no permite publicar workflows de Actions (`workflow` scope ausente). El archivo `docs/ci-template.yml` es una plantilla y no está activo. Las pruebas se ejecutaron localmente, sin ampliar permisos de GitHub.

## Acceso privado: avance posterior

- Propietario exclusivo requerido; cuentas secundarias pendientes. No se public� la configuraci�n web con acceso Cualquiera.
- C�digo actualizado guardado en Apps Script: entrada web deshabilitada, funci�n privada con comprobaci�n de identidad y manifiesto limitado a userinfo.email. Propiedad privada del propietario configurada.
- Transporte Python para API OAuth preparado y probado con respuestas simuladas. Deshabilitado el antiguo transporte web.
- Pendientes: proyecto Cloud est�ndar com�n, cliente OAuth, implementaci�n API Solo yo, permisos reales, almacenamiento autorizado de credenciales y despliegue actualizado en Render. La versi�n Live anterior sigue en blocked_persistence.
