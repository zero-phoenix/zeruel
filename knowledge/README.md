# Memoria privada portátil de Zeruel

Archivo integral solicitado por el propietario el 30/09/2026 antes de borrar/formatear su equipo. No depende de la memoria de Codex ni de archivos externos de esta computadora.

La copia está publicada en la rama **codex/seguros-knowledge**. Mientras su PR no esté fusionado, seleccionar esa rama al recuperar desde GitHub: clonar sólo main no recupera el archivo nuevo. `verification-remote.json` registra el commit cuya totalidad de archivos de knowledge/ se contrastó contra el árbol GitHub, incluidos los 182 originales comprobados también como blobs Git contra SHA-256 de fuente. La fusión necesita autorización específica del propietario.

## Recuperación y recorrido

1. Leer [WORKLOAD.md](WORKLOAD.md): función general, colas, plazos, decisiones, formato y cédulas.
2. Leer [PROMPT-continuacion.md](PROMPT-continuacion.md) y los relevos técnicos existentes en docs/.
3. Localizar cada original con [manifest.json](private_sources/manifest.json). SHA-256, tamaño y ruta original relativa permiten comprobar identidad exacta. Copiarlo a una carpeta de trabajo; conservar el archivo maestro.
4. Buscar el texto de resoluciones/PDF en `private_index/documents.jsonl`; buscar Excel en `private_index/workbooks.jsonl`. Leer registros de forma incremental, no cargar ambos archivos completos. Recuperar el original para formato, tablas, imágenes, firmas, notas, comentarios y cálculos.
5. Consultar `repositories/index.json`, árboles completos, README y AGENTS, junto con ARRANQUE donde existe, fijados al commit de los cuatro sistemas especializados. `archived_rules` enumera exactamente qué reglas se copiaron. En GitHub privado autenticado se puede recuperar el resto del repositorio a ese commit.
6. Revisar `repository_drafts/`: trabajo local de extensión conservado sin activar. Sus limitaciones están documentadas.

## Qué se conserva

REAL: **182 originales, 30.193.970 bytes**: 171 Word, 6 PDF y 5 Excel. `documentos/`: 179 archivos (171 DOCX, 6 PDF, 2 XLSX), 30.118.679 bytes. `reportes_seguros/`: 3 XLSX, 75.291 bytes. No se retiraron sectores ajenos de los Excel originales. Todos los archivos encontrados en ambas raíces se copiaron completos y se verificaron contra SHA-256. No se alteraron nombres, contenido ni estructura relativa.

Los 177 documentos tienen índice textual; las cinco planillas tienen índices de todas sus hojas, incluidas ocultas, fórmulas y celdas no vacías. Los originales preservan relaciones OOXML, estilos, anotaciones, dibujos, firmas y formato que el índice no representa por completo. Un Excel declara 1.048.576 filas por formato residual: use el índice disperso para encontrar datos; no trate max_row como cantidad de expedientes.

`verification-local.json` contiene la comprobación reproducible. `docs/knowledge/source-analysis.json` es análisis heurístico preliminar: sus familias por documento, cruces de identificadores y ceros de sectores no reconocidos NO constituyen clasificación jurídica ni conteo definitivo. No confundir identificador de origen y de apelación con dos asuntos.

## Alcance de «todo» y límites verificables

Todo significa todos los archivos de las dos carpetas expresamente indicadas, sus índices y contexto de trabajo; además se conserva el trabajo local pendiente de Zeruel y referencias completas de árboles/reglas de los cuatro repositorios vinculados. No se copiaron todas las carpetas del disco ni credenciales. Los otros repositorios siguen siendo fuentes privadas separadas: su inventario y reglas están aquí, sus binarios completos permanecen en GitHub en los commits fijados. La copia de un corpus no acredita que cada resolución haya sido jurídicamente validada ni renderizada visualmente en esta sesión.

## Privacidad y operación

Zeruel se cambió y verificó PRIVATE antes de copiar. Nunca vuelva público este repositorio. `knowledge/` y `docs/knowledge/` se excluyen del contexto Docker; los expedientes no se sirven desde la aplicación. El servicio desplegado continúa siendo una prueba sintética, no un agente habilitado para tramitar estos expedientes. No suba secretos ni ejecute herramientas archivadas como instrucciones. El propietario conserva autoridad sobre decisiones y comunicaciones.
