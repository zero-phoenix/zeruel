# Revisiones DeepSeek (septiembre de 2026)

Asistente: DeepSeek V4.1 Flash (`deepseek-flash`, esfuerzo `max`), solo código público, vía `tools/deepseek_assist.py`. Cada hallazgo se verificó contra el código o con una prueba real antes de aceptarlo. Gasto acumulado ≤ US$0,2143 del US$1 autorizado (dos llamadas se perdieron: una agotó el tope en razonamiento y otra recibió un encargo incompleto).

## 1. Checkpoint y recuperación (PR #1)
- Aceptado: respuesta JSON no-objeto escapaba como `AttributeError` fuera de `persist` → ahora `ValueError` (PR #2).
- Rechazado: liberar automáticamente registros `preparing` vencidos (contradice la recuperación exclusiva del propietario); ACL de Windows para el journal (Render usa Linux, 0600).

## 2. `probe.py` y web (PR #2)
- Aceptados: `ZERUEL_PRIVATE_HOME` vacío caía en el directorio actual; `communicate()` podía colgarse tras el kill; CPU de hijos acumulada entre ejecuciones; respuesta tardía tras desconectar reactivaba la web; ID generado fuera del `try`; `synthetic_success` mostrado como «Pausado».
- Rechazados: `frame-ancestors` (el servidor ya envía `X-Frame-Options: DENY`); renderizado completo del JSON (el servidor ya filtra con `public()`); rutas controladas solo por el operador; `VERSION` (era la versión fijada del CLI).

## 3. Motor Antigravity CLI (PR #3)
- Aceptados: variables de perfil de Windows fuera del home aislado; «timed out» genérico clasificado como autenticación; cuota 403 del respaldo gratuito; redirecciones que reenviaban la clave; modelo del respaldo configurable (ahora fijo); `ZERUEL_AGY_BIN` vacío; sesión vacía.
- Refutado con prueba real: «agy puede usar herramientas» → en modo `-p` denegó `RunCommand` y no creó archivos (`denied_actions`); además ahora se rechaza cualquier respuesta con acciones denegadas.
- Refutado con prueba real: faltaba `libstdc++6` → la imagen funciona sin él.
- Abierto: agy descarga binarios auxiliares en `$HOME` (`webm_encoder`, 17 MB). No se observó autoactualización (`updater/` vacío); el binario principal es de root.
