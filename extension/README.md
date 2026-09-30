# Zeruel para Edge: observación estructural local

Manifest V3, sin tiendas, pagos, servidor ni conexión con modelos. Carga esta carpeta en **Edge → `edge://extensions` → Modo de desarrollador → Cargar desempaquetada**. Fija el botón de Zeruel en la barra del navegador para conservar visible su indicador. No se declara compatibilidad real con otros navegadores hasta probarlos.

**Entrega parcial:** el propietario exige texto anonimizado, OCR local de imágenes/manuscrito y formato íntegro. La base estructural no satisface todos esos requisitos. La página **Revisión local de texto / OCR** conserva originales solo en memoria, permite marcar entidades y bloquea exportación de todo fragmento con letras/números sin selección explícita; nombres/género no se detectan automáticamente. TEXTO_OPERATIVO conserva solo vocabulario cerrado que el propietario verificó que no es identidad. OCR impreso piloto está preparado con recursos offline; manuscrito y formato íntegro están pendientes. No activar aún sobre expedientes reales. Consulta la revisión vigente en `docs/browser-extension-plan.md`.

## Uso

1. Abre un sitio de trabajo y pulsa **Autorizar únicamente este sitio**. Edge pide permiso solo para ese origen. No se conceden permisos globales por defecto. No autorices bancos, correo, login ni otros sitios sensibles.
2. Selecciona página DOM o escritorio remoto. En remoto, confirma que ya terminaste el acceso; su superficie se conserva completamente opaca. Puedes excluir zonas con X, Y, ancho y alto en porcentajes; las acciones dentro de ellas se omiten. Las zonas se configuran antes de activar y no se conservan tras cerrar el popup.
3. Pulsa **Activar hoy**. Hay indicador ACT/PAU/OFF en la barra y activo/pausado/desconectado en las páginas autorizadas. **Pausar ahora** y el botón flotante detienen la observación. El día siguiente o el reinicio del worker/navegador requiere nueva activación. No hay reactivación automática.
4. La extensión registra estructura de clics, envío de formulario, navegación y cambio de pestaña activa. Para decisiones usa las categorías del popup; no se infieren decisiones desde texto privado. Exporta manualmente el JSON. **Ver última captura estructural** reconstruye la imagen sin datos originales.
5. Después de exportar, puedes eliminar los registros. A los 1000 eventos se pausa; no borra registros antiguos silenciosamente.

## Anonimización antes de guardar

No intenta adivinar nombres con expresiones regulares ni preservar texto como marcadores a partir de un original. **No lee texto, nombres, etiquetas, valores, números de documento, URLs completas ni títulos para registrar.** Conserva únicamente categorías cerradas, posiciones cuantizadas y alias numéricos de sitio/pestaña/pantalla/sesión. PERSONA/EMPRESA/EXPEDIENTE/MONTO no se extraen porque implicaría interpretar el documento; el contenido completo se descarta. Los permisos de origen residen en el gestor de permisos de Edge, no en exportaciones.

La captura es una **reconstrucción estructural**, no una captura original difuminada: rectángulos de controles y superficies con colores fijos, sin texto ni píxeles de la página. Canvas, imágenes, iframes y el escritorio remoto no se leen; el modo remoto es completamente opaco. Un desenfoque u OCR incierto no garantiza ocultar toda información personal, por eso la versión inicial falla cerrada y pierde detalle visual. El usuario debe pausar antes de acceder a una pantalla remota de inicio de sesión: su DOM interno no es inspeccionable. No hay teclas, passwords ni tokens registrados. Las páginas DOM con campos de contraseña/OTP y rutas de autenticación se pausan automáticamente; esto no demuestra detección universal de todos los accesos.

Antes de persistir y antes de exportar se aplica un esquema recursivo estricto: solo claves exactas y valores de listas cerradas/números limitados. Se rechazan campos extra, texto arbitrario, HTML y cadenas de imágenes. Ningún registro se envía automáticamente. No subir exportaciones al repo sin revisar su validación y la política del teletrabajo.

## Pruebas y límites

Sin dependencias: `node --test extension/tests/*.test.js` desde la raíz. Las pruebas unitarias son **simuladas**; no prueban el permiso real de Edge ni el consumo de CPU/RAM. Validación real pendiente: carga, permiso denegado/concedido, indicador, pausa durante evento, navegación, pestañas, DOM de login ficticio, remoto opaco y exportación manual. No usar expedientes reales hasta completar esa validación. La extensión no automatiza acciones ni entrena modelos; procedimientos se redactan a partir de exportaciones estructurales y correcciones del propietario.
