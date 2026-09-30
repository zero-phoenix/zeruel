# Zeruel

Agente personal para aprender procedimientos y preparar borradores entre dispositivos, sin tarjeta ni pagos adicionales. Nombre aprobado: **Zeruel**.

## Estado real

Este repositorio implementa **el primer hito: prueba sintética de viabilidad**. No es todavía un agente operativo, no observa el escritorio y no procesa expedientes. La ejecución en Render, el acceso a Google AI Pro y la recuperación tras suspensión requieren pruebas con las cuentas del propietario. No se afirma que estén superadas.

- Python sin dependencias para el servidor y las pruebas.
- Gemini CLI oficial fijado en `0.62.0`, autenticación `oauth-personal` obligatoria.
- Rechazo de variables de API, Vertex y credenciales de servicio; sin alternativa facturable.
- Una inferencia a la vez; prueba fija, sin archivos ni herramientas.
- Interfaz móvil con estados desconectado/pausado/activo, autenticación y resultados sanitizados.
- Punto de control sintético externo opcional en Apps Script, firmado y persistente.

## Prueba local

Python 3.12 y Node.js 20 o superior:

```powershell
python -m unittest discover -s tests -v
python scripts/install_cli.py --destination work/gemini-cli
python -m zeruel.probe --prepare
```

El instalador descarga exclusivamente el paquete oficial del registro npm y comprueba su integridad SHA-512. No modifica la instalación de Antigravity ni la configuración personal de Gemini.

El informe de preparación indica la carpeta privada para Gemini. Para autenticar, establece `GEMINI_CLI_HOME` en esa carpeta e inicia el CLI instalado con Node de forma interactiva. Elige **Sign in with Google** y la cuenta asociada a tu suscripción. No selecciones API Key ni Vertex. No copies credenciales en el repositorio, chat o logs.

```powershell
$env:GEMINI_CLI_HOME = (Join-Path (Get-Location) 'work/private/gemini-home')
node work/gemini-cli/package/bundle/gemini.js
python -m zeruel.probe
```

La prueba devuelve únicamente estados, versión, resultado sintético y métricas. `blocked_auth` exige completar el acceso de Google; `paused_quota` conserva la pausa y no reintenta automáticamente.

## Prueba en nube

Consulta [el protocolo](docs/first-milestone.md). `Dockerfile` prepara un servicio de prueba para Render Free. No incluye credenciales ni activa pagos. La memoria real, la captura de Windows y los adaptadores jurídicos quedan condicionados al éxito del primer hito.

## Proyectos prioritarios

1. `zero-phoenix/SystemHope-ResAdmis`: admisión a trámite.
2. `zero-phoenix/elaboracion-de-resoluciones-de-requerimiento`.
3. Familia de improcedencias liminares; uno de sus subtipos está en `zero-phoenix/elaboracion-de-resoluciones-de-improcedencia-a-susalud`. No asumir que cubre toda la familia.
4. `zero-phoenix/elaboracion-de-r1-de-expedientes-de-apelaciones-en-la-cc1-de-indecopi`.

No se han verificado ni cambiado sus reglas jurídicas. La implementación posterior deberá leer sus instrucciones y comprobar generadores, plantillas y verificadores en copias.
