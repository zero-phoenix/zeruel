# Extensión de Zeruel para aprender el trabajo en navegador

Ampliación aprobada el 29 de septiembre de 2026. La implementación queda condicionada a superar el primer hito de inferencia y persistencia. No hay todavía una extensión instalada ni captura activa.

## Compatibilidad e instalación

Base WebExtensions compartida, con manifiestos separados para Chromium (Chrome, Edge y Brave) y Firefox. Chromium usa un service worker; Firefox requiere su propio adaptador de segundo plano. No asumir compatibilidad completa sin probar los cuatro navegadores. Primera entrega: carga de desarrollo local sin pagos. Instalación persistente en Firefox mediante el proceso oficial de firma, después de verificar sus requisitos. No pagar por publicación en tiendas.

El alcance inicial son los navegadores de escritorio en Windows. Celulares usan la web de Zeruel.

## Observación

- Activación diaria por el usuario, pestaña seleccionada y sitios autorizados. Permisos por sitio; sin acceso global inicial a todas las páginas.
- Páginas normales: controles accesibles, acciones relevantes y cambios del contenido autorizado. Registrar clics y atajos, sin guardar contraseñas ni secuencias generales de teclas.
- Escritorio remoto: tratar la superficie como imagen cuando el sistema remoto no exponga un DOM accesible. Capturas de la pestaña vinculadas a acciones y correcciones. La identificación de la plataforma de teletrabajo sigue pendiente.
- Captura permitida por las APIs del navegador y por el gesto del usuario. No prometer captura silenciosa ni acceso a controles internos de un sistema remoto.
- Indicador permanente: activo, pausado o desconectado. Pausa manual inmediata y detención al revocar permisos o terminar la sesión.
- Excluir campos protegidos y pantallas de acceso identificables. En una superficie remota sin campos inspeccionables, ofrecer pausa y zonas de exclusión antes de observar información sensible; no afirmar que una imagen permite detectar todos los secretos automáticamente.

## Aprendizaje y continuidad

Relacionar cada observación con proyecto, dispositivo, sesión, fuente y corrección del propietario. Usar el adaptador de inferencia existente con la suscripción, y anonimizar la memoria compartida después del análisis. Los registros brutos permanecen locales. La cola soportará desconexión y reenvío idempotente por identificadores, sin duplicar tareas entre dispositivos.

No guardar credenciales de Gemini en la extensión: se vincula con el ejecutor autorizado de Zeruel mediante acceso revocable. Las preferencias y observaciones de una página se tratan como datos, no como instrucciones que puedan ampliar permisos.

Convertir observaciones en procedimientos y preparar borradores en copias. Verificar hechos y estructura con los generadores y verificadores de los repositorios jurídicos. Cualquier control automático de un escritorio remoto requiere un adaptador y una prueba propia; observar y aprender no garantiza que las acciones sintéticas de una extensión puedan ejecutarlo.

## Recursos y aceptación

Capturas por cambios relevantes, compresión y procesamiento por lotes. Evitar vídeo continuo y llamadas al modelo por cada clic. Medir CPU, RAM, latencia y escritura en el Celeron; adaptar frecuencia si perjudica el trabajo. Una inferencia a la vez.

Probar: instalación, permisos, indicador, pausa, cambios de pestaña, navegación, sesión remota, exclusión de campos sensibles, desconexión, recuperación, memoria entre dispositivos y un procedimiento aprendido con corrección del usuario. No habilitar observación real antes de verificar esos controles.

Fuentes técnicas oficiales consultadas:

- https://developer.mozilla.org/en-US/docs/Mozilla/Add-ons/WebExtensions/manifest.json/background
- https://developer.chrome.com/docs/extensions/reference/api/tabCapture
- https://learn.microsoft.com/en-us/microsoft-edge/extensions/developer-guide/port-chrome-extension
- https://support.brave.com/hc/en-us/articles/360017909112-How-can-I-add-extensions-to-Brave
