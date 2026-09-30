# Zeruel

Agente personal para aprender procedimientos y preparar borradores entre dispositivos, sin tarjeta ni pagos adicionales. Nombre aprobado: **Zeruel**.

## Estado real

Este repositorio implementa **el primer hito: prueba sintética de viabilidad**. No es todavía un agente operativo, no observa el escritorio y no procesa expedientes. La ejecución en Render, el acceso a Google AI Pro y la recuperación tras suspensión requieren pruebas con las cuentas del propietario. No se afirma que estén superadas.

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
docker build -t zeruel .
```

La sesión de `agy` la crea el propietario iniciando sesión con su cuenta (enlace oficial + código). Su archivo se provisiona a Render solo como secreto `ZERUEL_AGY_OAUTH_TOKEN`; nunca en el repositorio, chat ni logs. Sin sesión, la prueba devuelve `blocked_auth` sin llamar al modelo; cuota agotada devuelve `paused_quota` o usa el respaldo gratuito si `ZERUEL_GEMINI_FREE_KEY` existe.

## Prueba en nube

Consulta [el protocolo](docs/first-milestone.md). `Dockerfile` prepara un servicio de prueba para Render Free. No incluye credenciales ni activa pagos. La memoria real, la captura de Windows y los adaptadores jurídicos quedan condicionados al éxito del primer hito.

## Proyectos prioritarios

1. `zero-phoenix/SystemHope-ResAdmis`: admisión a trámite.
2. `zero-phoenix/elaboracion-de-resoluciones-de-requerimiento`.
3. Familia de improcedencias liminares; uno de sus subtipos está en `zero-phoenix/elaboracion-de-resoluciones-de-improcedencia-a-susalud`. No asumir que cubre toda la familia.
4. `zero-phoenix/elaboracion-de-r1-de-expedientes-de-apelaciones-en-la-cc1-de-indecopi`.

No se han verificado ni cambiado sus reglas jurídicas. La implementación posterior deberá leer sus instrucciones y comprobar generadores, plantillas y verificadores en copias.
