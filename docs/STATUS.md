# Estado del primer hito — 29 de septiembre de 2026, Lima

## Comprobado

- Repositorio creado por Antigravity; código del primer hito publicado por Codex.
- Gemini CLI oficial `0.62.0` instalado en el directorio de trabajo aislado. Integridad SHA-512 verificada; archivo descargado: 20.787.241 bytes.
- El CLI instalado informa versión `0.62.0`.
- 18 pruebas Python y 6 pruebas Node pasan localmente. Cubren autenticación del servicio, exclusión de secretos, bloqueo de rutas facturables, cuota, concurrencia, HMAC, replay, persistencia simulada e idempotencia.
- La prueba real local se detiene con `blocked_auth`, sin llamar al modelo.
- El usuario indicó haber iniciado sesión en Render. La pestaña accesible cambió de `/login` a `/`, pero la herramienta no consiguió leer el dashboard por repetidos tiempos de espera. La cuenta y el plan no se han confirmado.
- No se añadió tarjeta, no se habilitó facturación, no se cargaron expedientes y no se activó observación del escritorio. No queda un proceso de Gemini esperando el acceso.

## Pendiente y bloqueante

- Acceso operativo al dashboard de Render y creación del servicio Free.
- Autenticación oficial de Gemini CLI con la cuenta del propietario y verificación del nivel de suscripción.
- Autorización y configuración segura de las credenciales remotas y del punto de control Apps Script.
- Prueba real de inferencia, renovación, suspensión, reinicio, persistencia externa y uso móvil con equipos apagados.
- Mediciones de CPU/RAM en Render. Las pruebas sintéticas no son una medición del rendimiento del agente completo.

**El primer hito NO está superado. El resto de la implementación permanece condicionado a su validación, según el plan aprobado.**

El acceso GitHub disponible no permite publicar workflows de Actions (`workflow` scope ausente). El archivo `docs/ci-template.yml` es una plantilla y no está activo. Las pruebas se ejecutaron localmente, sin ampliar permisos de GitHub.
