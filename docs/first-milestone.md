# Protocolo del primer hito

## Condiciones que no se negocian

No añadir tarjeta, usar créditos promocionales con vencimiento, contratar servicios ni habilitar facturación de Gemini API/Vertex. No extraer tokens de Antigravity. No cargar expedientes, pantallas ni datos personales en esta prueba. No generar tráfico artificial para impedir la suspensión de Render.

**Motor:** Antigravity CLI (`agy`) con Google AI Pro, por decisión del propietario del 30/09/2026 tras el cese de Gemini CLI para AI Pro (18/06/2026). Respaldo: Gemini API en capa gratuita, sin facturación, solo tras `paused_quota` y solo para la prueba sintética (Google puede usar esos datos para mejorar sus modelos). Una respuesta simulada no sustituye la prueba real.

## Configuración externa necesaria

1. Iniciar sesión en el dashboard de Render accesible al operador. Crear un **Web Service**, con repositorio `zero-phoenix/zeruel`, Docker y plan **Free**. Si el servicio o la cuenta exige tarjeta, detenerse. El coste aprobado es cero.
2. Solo tras levantar la puerta del proveedor, autenticar Gemini CLI oficial con la cuenta de Google AI Pro en un perfil aislado. Comprobar en la interfaz oficial que corresponde a la suscripción del propietario. No inferir el nivel Pro únicamente porque una solicitud devuelve respuesta.
3. Provisionar el perfil OAuth para el entorno remoto únicamente mediante los secretos de Render y tras autorización específica de ese almacenamiento. `ZERUEL_AGY_OAUTH_TOKEN` (sesión de `agy` creada por el propietario) contiene credenciales sensibles: no compartirlo en chat, GitHub, logs ni archivos públicos. La renovación y el soporte remoto deben verificarse, no asumirse.
4. Para el punto de control sintético, crear un proyecto Apps Script con `apps-script/SyntheticCheckpoint.gs`. Configurar una clave aleatoria de al menos 32 caracteres como propiedad `ZERUEL_CHECKPOINT_SECRET`. El script utiliza únicamente almacenamiento de propiedades, sin acceso a expedientes, Drive o Gmail. El endpoint requiere HMAC y rechaza repeticiones.
5. Acceso exclusivo del propietario mediante su cuenta de Google: no desplegar con acceso «Cualquiera» ni «Cualquier persona que tenga una Cuenta de Google». La firma HMAC no sustituye el inicio de sesión del propietario. El transporte OAuth privado mediante `scripts.run` ya está implementado; `runCheckpoint` comprueba la identidad efectiva. Sus permisos e identidad reales siguen sin validarse con Google. No configurar el transporte en Render hasta completar esa validación. Las cuentas secundarias quedan pendientes.
6. Configurar `ZERUEL_ACCESS_TOKEN` aleatorio de al menos 32 caracteres. La web lo recibe en un campo de contraseña y lo envía como cabecera; no se almacena ni se coloca en URLs.

## Matriz de aceptación

| Prueba | Evidencia necesaria | Estado (30/09/2026) |
|---|---|---|
| Instalación | Versión fijada y SHA-512 del paquete oficial comprobada | **Real** (`agy` 1.2.14, PR #3) |
| Autenticación | Perfil aislado OAuth y comprobación oficial del nivel de suscripción | **Real**: sesión `agy` del propietario (Google AI Pro) responde; nivel no comprobado por vía oficial |
| Inferencia | Respuesta sintética `ZERUEL_OK`, suma 42; sin herramientas | **Real** en Render (5–8 s) |
| Cuota | Pausa explícita; ninguna alternativa facturable ni reintento automático | Simulada |
| Concurrencia | Segunda ejecución rechazada mientras haya otra activa | Simulada |
| Idempotencia | Recuperar el identificador completado no repite la llamada | **Real** (también tras reinicio) |
| Bloqueo expirado | La operación incierta queda pausada; no se vuelve a inferir | Simulada |
| Trabajador antiguo | Una generación anterior no puede completar otra operación | Simulada |
| Escritura parcial | El fallo de almacenamiento bloquea nuevas inferencias y conserva la incertidumbre | Simulada |
| Recuperación manual | Lease vencida cerrada por el propietario sin llamar al modelo: informe durable idempotente o `terminal_unknown`, nunca éxito | Simulada |
| Respuesta perdida | Repetir persistencia del mismo resultado es idempotente; uno diferente se rechaza | Simulada |
| Persistencia | Mismo resultado recuperado desde Apps Script tras reiniciar y suspender Render | **Real** tras reinicio; tras suspensión: arranque en frío real (28,3 s), recuperación de un resultado anterior pendiente |
| Renovación | Ejecución correcta tras vencer el token de acceso; secretos y logs sin filtraciones | Pendiente REAL (proceso vivo > 1 h); no se ejecutó la prueba en el entorno cloud del 30/09 |
| Móvil y equipos apagados | Tarea lanzada desde móvil con ambos Windows apagados y resultado recuperable | Pendiente REAL; autorun verificado solo con evidencia SIMULADA (17 pruebas web, rama `feat/mobile-autorun`). ADB en Windows y despliegue pendientes |
| Recursos | Tiempo, pico de RAM y CPU del CLI en Render; sin reinicios por recursos insuficientes | **Real**: ~210 MB pico, 0,5–0,6 s CPU; sin reinicios observados |

No modificar `cloud_gate_passed` para convertir una prueba parcial en aprobación. La versión actual siempre informa `false`: es una prueba de viabilidad, no certificación del agente.

## Paso siguiente, condicionado

Solo después de documentar éxito de toda la matriz: cola real, SQLite + sincronización privada con Drive OAuth, memoria anonimizada después del análisis, observación diaria de Windows con indicador permanente, y adaptadores jurídicos que trabajan en copias. La observación registrará aplicaciones autorizadas, omitirá contraseñas/campos protegidos y ajustará frecuencia si perjudica la fluidez. Las normas jurídicas del repositorio requieren verificación independiente antes de generar resoluciones reales.

Render Free se suspende por inactividad y pierde archivos locales. No ofrece garantía de actividad permanente. Fuente: https://render.com/docs/free

Gemini CLI puede reutilizar autenticación existente en modo programático; la ejecución remota con esta cuenta sigue pendiente de verificación. Fuente: https://geminicli.com/docs/get-started/authentication/


## Configuración privada del punto de control

1. Guardar la versión actual de `SyntheticCheckpoint.gs` y el manifiesto. `doPost` rechaza todas las llamadas web, incluso con firma válida. Configurar `ZERUEL_OWNER_EMAIL` con la cuenta principal, solo en propiedades privadas. No añadir cuentas secundarias.
2. Usar un proyecto Google Cloud estándar común al script y al cliente OAuth, sin vincular facturación ni activar pruebas de pago. Habilitar únicamente Apps Script API. La vinculación desde un proyecto predeterminado revoca autorizaciones anteriores y no permite volver a ese proyecto predeterminado: presentar el proyecto concreto y obtener confirmación del propietario inmediatamente antes de vincularlo.
3. Configurar el cliente OAuth del propietario y el alcance mínimo `userinfo.email` solicitado por el manifiesto. No utilizar las credenciales del cliente Gemini CLI para acceder a Apps Script. Si Google exige ámbitos más amplios, detenerse y documentar el requisito.
4. Implementar como **Ejecutable de API**, acceso **Solo yo**. No implementar como aplicación web pública. El transporte llama `runCheckpoint` con `devMode:false` y usa el ID de implementación, conforme a la documentación actual.
5. Tras autorización del almacenamiento remoto, introducir `ZERUEL_CHECKPOINT_DEPLOYMENT_ID`, `ZERUEL_CHECKPOINT_SECRET` y `ZERUEL_CHECKPOINT_OAUTH_JSON` únicamente en secretos Render. El JSON contiene `client_id`, `client_secret`, `refresh_token`. No pegarlo en chats ni repositorios. El transporte renueva tokens y rechaza redirecciones para no reenviar credenciales.
6. Probar acceso real del propietario, rechazo de otras identidades, renovación, reinicios e idempotencia antes de declarar persistencia lista. Los tests locales usan identidades simuladas, no demuestran permisos efectivos de Google.

Fuentes oficiales: https://developers.google.com/apps-script/api/how-tos/execute y https://developers.google.com/identity/protocols/oauth2 . El consentimiento OAuth en modo Testing puede limitar la duración de los refresh tokens a siete días dependiendo de los ámbitos; verificar el comportamiento real y conservar pausa ante expiración.

## Asistencia externa del desarrollo

DeepSeek puede revisar únicamente código público y diffs como asistente de Codex, con el presupuesto específico autorizado de US$1 del saldo existente y sin recargas. No forma parte de la inferencia de Zeruel. Antes de cada llamada se reserva su coste máximo; una respuesta perdida conserva la reserva y no se reintenta automáticamente. Las credenciales expuestas deben rotarse mediante interfaces privadas antes de cualquier uso. No transmitir capturas, expedientes, memoria personal ni secretos. La autorización no levanta la puerta de Gemini CLI/Google AI Pro ni cambia `cloud_gate_passed`.

## Recuperación manual de una lease incierta

Solo el propietario, tras confirmar que el trabajador original terminó (proceso detenido o instancia reiniciada) y con la lease vencida:

```powershell
python scripts/recover_checkpoint.py <id> --confirm-worker-finished            # con informe local durable
python scripts/recover_checkpoint.py <id> --confirm-worker-finished --unknown  # sin informe: terminal_unknown
```

Si falta el registro local, el comando pide la generación de forma privada (léela en las propiedades del script; no la pases como argumento). Sin informe ni resultado durable no se puede reconstruir un resultado y asegurar a la vez que no haya duplicados: el ID se cierra como desconocido y nunca se reinfiere. El servidor HTTP no expone esta acción.
