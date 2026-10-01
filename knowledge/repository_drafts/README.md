# Trabajo local preservado, sin activar
Origen: checkout zeruel, rama codex/extension-capture-ocr, HEAD 1ad02a76.
El parche conserva el cambio comprometido desde main 79e1bcd; los cuatro archivos del manifiesto estaban sin seguimiento. Aplicar únicamente en una rama de revisión, nunca de forma automática.
SIMULADA: 61 pruebas Python aprobadas. La suite Node detectó un fallo del detector PII para el nombre «Ella Pumayalli Soncco». No se corrigió ni se declaró listo. El detector y la extracción de geometría OCR no estaban conectados a review.js; el adaptador devolvía texto/confianza sin bboxes. Estas copias son archivo, no implementación activa.
El checkout original no se modificó. Para reconstruir, partir de main 79e1bcd, revisar/aplicar el parche y copiar los cuatro archivos. Verificar dependencias y ejecutar las pruebas antes de integrar.
