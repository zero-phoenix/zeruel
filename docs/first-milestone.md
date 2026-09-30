# Protocolo del primer hito

## Condiciones que no se negocian

No añadir tarjeta, usar créditos promocionales con vencimiento, contratar servicios ni habilitar facturación de Gemini API/Vertex. No extraer tokens de Antigravity. No cargar expedientes, pantallas ni datos personales en esta prueba. No generar tráfico artificial para impedir la suspensión de Render.

## Configuración externa necesaria

1. Iniciar sesión en el dashboard de Render accesible al operador. Crear un **Web Service**, con repositorio `zero-phoenix/zeruel`, Docker y plan **Free**. Si el servicio o la cuenta exige tarjeta, detenerse. El coste aprobado es cero.
2. Autenticar Gemini CLI oficial con la cuenta de Google AI Pro en un perfil aislado. Comprobar en la interfaz oficial que corresponde a la suscripción del propietario. No inferir el nivel Pro únicamente porque una solicitud devuelve respuesta.
3. Provisionar el perfil OAuth para el entorno remoto únicamente mediante los secretos de Render y tras autorización específica de ese almacenamiento. `ZERUEL_GEMINI_OAUTH_JSON` contiene credenciales sensibles: no compartirlo en chat, GitHub, logs ni archivos públicos. La renovación y el soporte remoto deben verificarse, no asumirse.
4. Para el punto de control sintético, crear un proyecto Apps Script con `apps-script/SyntheticCheckpoint.gs`. Configurar una clave aleatoria de al menos 32 caracteres como propiedad `ZERUEL_CHECKPOINT_SECRET`. El script utiliza únicamente almacenamiento de propiedades, sin acceso a expedientes, Drive o Gmail. El endpoint requiere HMAC y rechaza repeticiones.
5. Acceso exclusivo del propietario mediante su cuenta de Google: no desplegar con acceso «Cualquiera» ni «Cualquier persona que tenga una Cuenta de Google». La firma HMAC no sustituye el inicio de sesión del propietario. El adaptador Apps Script actual no autentica la identidad Google; por ello queda bloqueado para uso remoto hasta implementar y validar una conexión OAuth privada. No configurar el endpoint en Render mientras no cumpla esta condición. Las cuentas secundarias quedan pendientes.
6. Configurar `ZERUEL_ACCESS_TOKEN` aleatorio de al menos 32 caracteres. La web lo recibe en un campo de contraseña y lo envía como cabecera; no se almacena ni se coloca en URLs.

## Matriz de aceptación

| Prueba | Evidencia necesaria |
|---|---|
| Instalación | Versión fijada y SHA-512 del paquete oficial comprobada |
| Autenticación | Perfil aislado OAuth y comprobación oficial del nivel de suscripción |
| Inferencia | Respuesta sintética `ZERUEL_OK`, suma 42; sin herramientas |
| Cuota | Pausa explícita; ninguna alternativa facturable ni reintento automático |
| Concurrencia | Segunda ejecución rechazada mientras haya otra activa |
| Idempotencia | Recuperar el identificador completado no repite la llamada |
| Persistencia | Mismo resultado recuperado desde Apps Script tras reiniciar y suspender Render |
| Renovación | Ejecución correcta tras vencer el token de acceso; secretos y logs sin filtraciones |
| Móvil y equipos apagados | Tarea lanzada desde móvil con ambos Windows apagados y resultado recuperable |
| Recursos | Tiempo, pico de RAM y CPU del CLI en Render; sin reinicios por recursos insuficientes |

No modificar `cloud_gate_passed` para convertir una prueba parcial en aprobación. La versión actual siempre informa `false`: es una prueba de viabilidad, no certificación del agente.

## Paso siguiente, condicionado

Solo después de documentar éxito de toda la matriz: cola real, SQLite + sincronización privada con Drive OAuth, memoria anonimizada después del análisis, observación diaria de Windows con indicador permanente, y adaptadores jurídicos que trabajan en copias. La observación registrará aplicaciones autorizadas, omitirá contraseñas/campos protegidos y ajustará frecuencia si perjudica la fluidez. Las normas jurídicas del repositorio requieren verificación independiente antes de generar resoluciones reales.

Render Free se suspende por inactividad y pierde archivos locales. No ofrece garantía de actividad permanente. Fuente: https://render.com/docs/free

Gemini CLI puede reutilizar autenticación existente en modo programático; la ejecución remota con esta cuenta sigue pendiente de verificación. Fuente: https://geminicli.com/docs/get-started/authentication/

