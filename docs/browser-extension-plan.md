# Extensión de Zeruel para aprender el trabajo en navegador

## Revisión vigente — 30/09/2026

El propietario autorizó trabajo local paralelo sin esperar la puerta de nube. **Anonimizar antes de cualquier almacenamiento o envío**, incluido el texto de documentos. Esta instrucción sustituye las partes del diseño histórico inferior sobre registros brutos y anonimización después del análisis.

`extension/` implementa Edge Manifest V3 desempaquetado con permisos opcionales por origen, activación diaria, indicador y pausa con generaciones para descartar acciones tardías, categorías estructurales y exportación local validada. No se instaló ni se activó en Edge. La captura automática es una reconstrucción sin texto/píxeles originales; el remoto queda opaco, con exclusiones por coordenadas. **El propietario rechazó esta captura como suficiente:** la extensión completa debe conservar texto anonimizado, extraer imágenes/manuscrito localmente y copiar formato íntegro. La versión actual es parcial y no acepta todavía esos requisitos como completados.

### Texto local: componente concreto, no detección universal

- Página `review.html` accesible desde el popup: texto pegado o extraído por OCR solo en memoria, selección explícita de spans tipados y vista previa local. Nunca guarda el original, la imagen, el mapa reversible ni selecciones en storage, red, chat o repositorio. Vacía la página al cerrarse. Los originales no deben introducirse en modelos ni en DeepSeek.
- Marcadores: NOMBRE_HOMBRE, NOMBRE_MUJER, NOMBRE_DESCONOCIDO, APELLIDO, DNI, RUC, DIRECCION, CORREO, TELEFONO, EXPEDIENTE, POLIZA, CUENTA, TARJETA, CREDITO, EMPRESA, MONTO y DOCUMENTO. Género solo por confirmación explícita, nunca adivinado desde el nombre. Alias consistentes solo dentro de cada revisión.
- Sugerencias limitadas de correos/números contextuales no son aprobación. **Todo fragmento con letras o números sin span explícito bloquea exportación**, aunque coincida con el vocabulario. `TEXTO_OPERATIVO` conserva únicamente palabras cerradas que el propietario seleccionó y verificó que no son identidad. Un simple botón «ya revisado» no habilita texto libre. La exportación vuelve a ejecutar anonimización desde original+spans antes de producir JSON de texto (`schema:2`); el registro automático estructural sigue en `schema:1` y rechaza texto adicional.
- Falsador aplicado: «Ella» puede ser un nombre y «La Vista» una empresa aunque parezcan palabras corrientes. Ambos sin spans bloquean; se corrige la causa eliminando aprobación automática por vocabulario y se añade regresión. El juicio manual puede equivocarse al clasificar un nombre como texto operativo: no se afirma garantía universal. No activar todavía sobre expedientes reales ni declarar preservación semántica completa.

### OCR y formato

- OCR piloto con Tesseract.js empaquetado localmente por herramienta del repositorio, versiones/integridad fijadas, sin CDN ni cache de resultados. Worker destruido al terminar. El módulo OCR devuelve texto/confianza solo en memoria; **confianza OCR no equivale a texto anonimizado**. Toda salida pasa por revisión local y bloquea exportación de fragmentos no clasificados. Evidencia real de OCR de texto impreso en navegador de prueba es distinta de prueba real en Edge.
- Manuscrito exige prueba propia y puede fallar. La fixture usa tipografía cursiva simulada: no constituye manuscrito real ni prueba de lectura fiable. No se promete OCR seguro de todo documento, ni procesamiento en tiempo real en el Celeron.
- Formato íntegro pendiente: extracción local DOM de estilos computados con lista cerrada de fuentes, tamaños, pesos, color, interlineado, márgenes, alineación, páginas y pie; los nombres de fuentes privadas y CSS arbitrario no se exportan. Texto anonimizado con spans debe conservar sus bloques y geometría. El modelo de layout preparado no está integrado con captura/revisión y no es prueba de reproducción fiel.
- En imágenes/escritorio remoto, reconstruir desde OCR anonimizado y cajas; cualquier región desconocida se vuelve totalmente opaca. Un desenfoque parcial u OCR incierto no garantiza ocultar toda información. No guardar imagen original ni declararla copia exacta. Comparar impresión/manuscrito, estilos y pies con fixtures locales antes de habilitarlo.

### Pruebas y siguiente aceptación

39 pruebas Node simuladas de la base completa (estructura, worker/carreras/reinicio, DOM/exclusiones/login, spans, OCR mock y layout mock) pasan al 30/09/2026. Incluyen nombres, DNI/RUC, correo, teléfono, tarjetas, cuenta/póliza, montos y documento ficticios; claves extra, imágenes originales y texto no revisado se rechazan. Las zonas excluidas eliminan geometría del JSON además de tapar la representación. No prueban permisos reales de Edge, manuscritos ni consumo de CPU/RAM.

Pendiente: instalación Edge por el propietario; permiso negado/concedido; indicador y pausa durante evento/OCR; navegación/pestañas/formularios; login ficticio; exclusiones remoto; revisión/exportación texto; inspección de almacenamiento/salida sin originales; medición Celeron; comparación de formato y OCR real con manuscritos ficticios. Fixture en `extension/tests/fixture.html`; se abre sin servidor para revisar/reproducir manualmente. La observación con permisos por sitio necesita servirla por localhost de forma temporal (no se habilitan file:// ni sitios globales).

Con exportaciones revisadas y correcciones se redactan procedimientos en `docs/procedimientos/`, citando alias y eventos. No inventar decisiones jurídicas ni detalles no observados. No se ha elaborado procedimiento aprendido de datos reales.

## Diseño histórico (29/09/2026), sustituido donde contradiga la revisión vigente

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
