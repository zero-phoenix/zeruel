# Zeruel

**Tractatus (hechos, proposiciones falsables y límites):** [docs/tractatus/](docs/tractatus/README.md).

**Para continuar con otra IA:** entregar el [megaprompt detallado](knowledge/MEGAPROMPT-continuacion.md), que contiene el recorrido de lectura, mapa del código, contexto jurídico y evidencia. El archivo integral del PR #24 ya está fusionado en main `9af5fb4` y verificado.

**Repositorio PRIVADO con archivo integral de trabajo:** [memoria y originales](knowledge/README.md), [seguros CC1](knowledge/WORKLOAD.md) y [prompt para otra IA](knowledge/PROMPT-continuacion.md). El archivo no se sirve desde la web ni se incluye en el contexto Docker.

Agente personal para aprender procedimientos y preparar borradores entre dispositivos, sin tarjeta ni pagos adicionales. Nombre aprobado: **Zeruel**.

## Estado real

**Continuidad:** el relevo completo para el siguiente agente está en [docs/HANDOFF.md](docs/HANDOFF.md).

Este repositorio implementa **el primer hito: prueba sintética de viabilidad**. No es todavía un agente operativo, no observa el escritorio y no procesa expedientes.

**Evidencia real (30/09/2026):** en Render Free, la prueba sintética responde `synthetic_success` con Antigravity CLI y Google AI Pro (5–8 s, ~210 MB); el resultado se guarda y recupera desde el punto de control privado de Apps Script; no se repite una tarea ya completada, ni siquiera tras reiniciar el servicio; tras suspensión, el servicio despierta en ~28 s. Detalle y límites en [docs/STATUS.md](docs/STATUS.md) y en la matriz de [docs/first-milestone.md](docs/first-milestone.md). **Pendiente:** tarea lanzada desde el celular con ambos Windows apagados, renovación del token con el servicio encendido más de 1 h y cuota agotada. `cloud_gate_passed` sigue en `false`.

**Uso:** https://zeruel-synthetic-probe.onrender.com → «Acceder con Google» (solo la cuenta del propietario) → «Ejecutar prueba sintética». Funciona igual desde el celular. Siguiente agente: [docs/PROMPT-continuacion-celular.md](docs/PROMPT-continuacion-celular.md).

**Motor de inferencia (decisión del propietario, 30/09/2026):** Gemini CLI dejó de atender a Google AI Pro el 18/06/2026 ([anuncio](https://developers.googleblog.com/an-important-update-transitioning-gemini-cli-to-antigravity-cli/)). El propietario autorizó su reemplazo oficial, **Antigravity CLI (`agy`)**, con su suscripción Google AI Pro y el modelo Gemini 3.8 Flash (High). Respaldo autorizado solo tras cuota agotada: Gemini API en capa gratuita, sin facturación y únicamente para la prueba sintética. Vertex y rutas facturables siguen prohibidas.

- Python sin dependencias para el servidor y las pruebas.
- Antigravity CLI oficial fijado en `1.2.14` (SHA-512), binario de solo lectura, `--sandbox`, sin comandos de barra ni herramientas aprobadas automáticamente.
- Rechazo de variables de API, Vertex y credenciales de servicio; sin alternativa facturable.
- Una inferencia a la vez; prueba fija, sin archivos ni herramientas.
- Interfaz móvil con estados desconectado/pausado/activo, autenticación y resultados sanitizados.
- Punto de control sintético externo opcional en Apps Script, firmado y persistente.
- Recuperación conservadora: generación privada por bloqueo, registro local previo y reintentos de persistencia sin repetir inferencia. Una operación incierta queda pausada; solo el propietario puede cerrarla con `scripts/recover_checkpoint.py`, sin volver a inferir.

## Prueba local

Python 3.12 y Node.js 20 o superior:

```powershell
python -m unittest discover -s tests -v
```

La imagen Docker se construye en Render o en un Codespace, no en la PC del propietario (equipo de bajos recursos). La sesión de `agy` la crea el propietario iniciando sesión con su cuenta (enlace oficial + código), sin Docker local, con `tools/agy-login-codespace.ps1`. Su archivo se provisiona a Render solo como secreto `ZERUEL_AGY_OAUTH_TOKEN`; nunca en el repositorio, chat ni logs. Sin sesión, la prueba devuelve `blocked_auth` sin llamar al modelo; cuota agotada devuelve `paused_quota` o usa el respaldo gratuito si `ZERUEL_GEMINI_FREE_KEY` existe.

## Prueba en nube

Consulta [el protocolo](docs/first-milestone.md). `Dockerfile` prepara un servicio de prueba para Render Free. No incluye credenciales ni activa pagos. La memoria real, la captura de Windows y los adaptadores jurídicos quedan condicionados al éxito del primer hito.

## Proyectos prioritarios

1. `zero-phoenix/SystemHope-ResAdmis`: admisión a trámite.
2. `zero-phoenix/elaboracion-de-resoluciones-de-requerimiento`.
3. Familia de improcedencias liminares; uno de sus subtipos está en `zero-phoenix/elaboracion-de-resoluciones-de-improcedencia-a-susalud`. No asumir que cubre toda la familia.
4. `zero-phoenix/elaboracion-de-r1-de-expedientes-de-apelaciones-en-la-cc1-de-indecopi`.

No se han verificado ni cambiado sus reglas jurídicas. La implementación posterior deberá leer sus instrucciones y comprobar generadores, plantillas y verificadores en copias.

## Extensión local de Edge (piloto)

Código e instrucciones en [extension/README.md](extension/README.md). Observación estructural con permiso por sitio, activación diaria, pausa y exportación manual. Texto anonimizado por categorías, OCR local y conservación íntegra de formato son requisitos adicionales; consultar los límites y pruebas del piloto antes de usarlo. La prueba OCR sintética en el navegador integrado no equivale a validación de la extensión en Edge. No se han observado expedientes reales.
