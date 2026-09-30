# Protocolo del primer hito

## Condiciones que no se negocian

No a帽adir tarjeta, usar cr茅ditos promocionales con vencimiento, contratar servicios ni habilitar facturaci贸n de Gemini API/Vertex. No extraer tokens de Antigravity. No cargar expedientes, pantallas ni datos personales en esta prueba. No generar tr谩fico artificial para impedir la suspensi贸n de Render.

## Configuraci贸n externa necesaria

1. Iniciar sesi贸n en el dashboard de Render accesible al operador. Crear un **Web Service**, con repositorio `zero-phoenix/zeruel`, Docker y plan **Free**. Si el servicio o la cuenta exige tarjeta, detenerse. El coste aprobado es cero.
2. Autenticar Gemini CLI oficial con la cuenta de Google AI Pro en un perfil aislado. Comprobar en la interfaz oficial que corresponde a la suscripci贸n del propietario. No inferir el nivel Pro 煤nicamente porque una solicitud devuelve respuesta.
3. Provisionar el perfil OAuth para el entorno remoto 煤nicamente mediante los secretos de Render y tras autorizaci贸n espec铆fica de ese almacenamiento. `ZERUEL_GEMINI_OAUTH_JSON` contiene credenciales sensibles: no compartirlo en chat, GitHub, logs ni archivos p煤blicos. La renovaci贸n y el soporte remoto deben verificarse, no asumirse.
4. Para el punto de control sint茅tico, crear un proyecto Apps Script con `apps-script/SyntheticCheckpoint.gs`. Configurar una clave aleatoria de al menos 32 caracteres como propiedad `ZERUEL_CHECKPOINT_SECRET`. El script utiliza 煤nicamente almacenamiento de propiedades, sin acceso a expedientes, Drive o Gmail. El endpoint requiere HMAC y rechaza repeticiones.
5. Acceso exclusivo del propietario mediante su cuenta de Google: no desplegar con acceso 芦Cualquiera禄 ni 芦Cualquier persona que tenga una Cuenta de Google禄. La firma HMAC no sustituye el inicio de sesi贸n del propietario. El adaptador Apps Script actual no autentica la identidad Google; por ello queda bloqueado para uso remoto hasta implementar y validar una conexi贸n OAuth privada. No configurar el endpoint en Render mientras no cumpla esta condici贸n. Las cuentas secundarias quedan pendientes.
6. Configurar `ZERUEL_ACCESS_TOKEN` aleatorio de al menos 32 caracteres. La web lo recibe en un campo de contrase帽a y lo env铆a como cabecera; no se almacena ni se coloca en URLs.

## Matriz de aceptaci贸n

| Prueba | Evidencia necesaria |
|---|---|
| Instalaci贸n | Versi贸n fijada y SHA-512 del paquete oficial comprobada |
| Autenticaci贸n | Perfil aislado OAuth y comprobaci贸n oficial del nivel de suscripci贸n |
| Inferencia | Respuesta sint茅tica `ZERUEL_OK`, suma 42; sin herramientas |
| Cuota | Pausa expl铆cita; ninguna alternativa facturable ni reintento autom谩tico |
| Concurrencia | Segunda ejecuci贸n rechazada mientras haya otra activa |
| Idempotencia | Recuperar el identificador completado no repite la llamada |
| Persistencia | Mismo resultado recuperado desde Apps Script tras reiniciar y suspender Render |
| Renovaci贸n | Ejecuci贸n correcta tras vencer el token de acceso; secretos y logs sin filtraciones |
| M贸vil y equipos apagados | Tarea lanzada desde m贸vil con ambos Windows apagados y resultado recuperable |
| Recursos | Tiempo, pico de RAM y CPU del CLI en Render; sin reinicios por recursos insuficientes |

No modificar `cloud_gate_passed` para convertir una prueba parcial en aprobaci贸n. La versi贸n actual siempre informa `false`: es una prueba de viabilidad, no certificaci贸n del agente.

## Paso siguiente, condicionado

Solo despu茅s de documentar 茅xito de toda la matriz: cola real, SQLite + sincronizaci贸n privada con Drive OAuth, memoria anonimizada despu茅s del an谩lisis, observaci贸n diaria de Windows con indicador permanente, y adaptadores jur铆dicos que trabajan en copias. La observaci贸n registrar谩 aplicaciones autorizadas, omitir谩 contrase帽as/campos protegidos y ajustar谩 frecuencia si perjudica la fluidez. Las normas jur铆dicas del repositorio requieren verificaci贸n independiente antes de generar resoluciones reales.

Render Free se suspende por inactividad y pierde archivos locales. No ofrece garant铆a de actividad permanente. Fuente: https://render.com/docs/free

Gemini CLI puede reutilizar autenticaci贸n existente en modo program谩tico; la ejecuci贸n remota con esta cuenta sigue pendiente de verificaci贸n. Fuente: https://geminicli.com/docs/get-started/authentication/


## Configuraci髇 privada del punto de control

1. Guardar la versi髇 actual de `SyntheticCheckpoint.gs` y el manifiesto. `doPost` rechaza todas las llamadas web, incluso con firma v醠ida. Configurar `ZERUEL_OWNER_EMAIL` con la cuenta principal, solo en propiedades privadas. No a馻dir cuentas secundarias.
2. Usar un proyecto Google Cloud est醤dar com鷑 al script y al cliente OAuth, sin vincular facturaci髇 ni activar pruebas de pago. Habilitar 鷑icamente Apps Script API. La vinculaci髇 desde un proyecto predeterminado revoca autorizaciones anteriores y no permite volver a ese proyecto predeterminado: revisar antes de confirmar.
3. Configurar el cliente OAuth del propietario y el alcance m韓imo `userinfo.email` solicitado por el manifiesto. No utilizar las credenciales del cliente Gemini CLI para acceder a Apps Script. Si Google exige 醡bitos m醩 amplios, detenerse y documentar el requisito.
4. Implementar como **Ejecutable de API**, acceso **Solo yo**. No implementar como aplicaci髇 web p鷅lica. El transporte llama `runCheckpoint` con `devMode:false` y usa el ID de implementaci髇, conforme a la documentaci髇 actual.
5. Tras autorizaci髇 del almacenamiento remoto, introducir `ZERUEL_CHECKPOINT_DEPLOYMENT_ID`, `ZERUEL_CHECKPOINT_SECRET` y `ZERUEL_CHECKPOINT_OAUTH_JSON` 鷑icamente en secretos Render. El JSON contiene `client_id`, `client_secret`, `refresh_token`. No pegarlo en chats ni repositorios. El transporte renueva tokens y rechaza redirecciones para no reenviar credenciales.
6. Probar acceso real del propietario, rechazo de otras identidades, renovaci髇, reinicios e idempotencia antes de declarar persistencia lista. Los tests locales usan identidades simuladas, no demuestran permisos efectivos de Google.

Fuentes oficiales: https://developers.google.com/apps-script/api/how-tos/execute y https://developers.google.com/identity/protocols/oauth2 . El consentimiento OAuth en modo Testing puede limitar la duraci髇 de los refresh tokens a siete d韆s dependiendo de los 醡bitos; verificar el comportamiento real y conservar pausa ante expiraci髇.
