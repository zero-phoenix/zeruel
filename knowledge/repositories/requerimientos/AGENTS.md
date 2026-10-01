# DIRECTRICES MAESTRAS DEL SISTEMA (AGENTS.md)
# SISTEMA DE RESOLUCIONES DE REQUERIMIENTO — INDECOPI CC1

```
╔══════════════════════════════════════════════════════════════════════════════╗
║  ANCLAJE OBLIGATORIO — LÉELO ANTES DE CUALQUIER OTRA COSA                    ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  Este archivo solo gobierna si lo has cargado DESDE LA RAÍZ DE ESTE          ║
║  REPOSITORIO (`elaboracion-de-resoluciones-de-requerimiento`).               ║
║                                                                              ║
║  PRIMER COMANDO DE TODA SESIÓN, SIN EXCEPCIÓN:                               ║
║      python scripts/comprobar_anclaje.py                                     ║
╚══════════════════════════════════════════════════════════════════════════════╝
```

> **AUTORIDAD:** Secretaría Técnica de la Comisión de Protección al Consumidor N° 1 (CC1) — Indecopi Sede Central.  
> **NORMA MARCO ADJETIVA:** Texto Único Ordenado de la Ley N° 27444 — Ley del Procedimiento Administrativo General, aprobado por **Decreto Supremo N° 006-2026-JUS** (artículos 20.4, 124°, 136°, 140° y 146°).  
> **FORMATO OBLIGATORIO DEL ENTREGABLE:** **EXCLUSIVAMENTE EN WORD (`.docx`)**. Jamás entregar resoluciones en PDF. Nombre del archivo: `REQ <EXPEDIENTE> R<N>.docx` (Ejemplo: `REQ 3077-2026 R1.docx`).  
> **PROTOCOLO DE ENTREGA:** `python scripts/requerimiento.py entregar <archivo.docx> [--caso <num>]` debe arrojar `APTO / ENTREGABLE CERTIFICADO`.  
> **MODO DE INGESTA:** Directo por caso (CLI o JSON), **sin depender de cuadros manuales de Excel**.

---

## 1. REGLAS NO NEGOCIABLES (AXIOMAS POPPERIANOS)

1. **ENTREGABLE EXCLUSIVO EN WORD (.DOCX):**
   Queda terminantemente prohibido entregar resoluciones de requerimiento en formato PDF. Toda entrega debe ser un archivo `.docx` debidamente ensamblado, limpio y editable.
2. **PROHIBICIÓN ESTRICTA DE TRASLADO AL DENUNCIADO:**
   En etapa de calificación previa de requerimiento, **PROHIBIDO TERMINANTEMENTE correr traslado o notificar al proveedor denunciado**. La resolución se notifica **exclusivamente al denunciante**.
3. **CITA VINCULANTE AL TUO DE LA LPAG:**
   Citar siempre el **Decreto Supremo N° 006-2026-JUS**. PROHIBIDA cualquier cita al derogado D.S. 004-2019-JUS.
4. **MEDIDA CAUTELAR POR CUERDA SEPARADA:**
   Toda solicitud cautelar formulada conjuntamente en la denuncia debe requerirse para que se presente:
   - En **escrito independiente**.
   - Por **cuerda separada**.
   - Con sus **propios anexos y tasa administrativa**.
   - Ingresada por Mesa de Partes (MDPV o física) con **diferente cargo / código de ingreso independiente**.
   - Normas: Art. 146° TUO LPAG, Arts. 26° y 27° D.L. 807, Art. 109° Ley 29571 y **Arts. 608° y 637° del Código Procesal Civil** (aplicación supletoria: trámite *inaudita parte*).
5. **CONFIDENCIALIDAD SISTEMÁTICA:**
   - **Por MDPV (sin pedido formal en el escrito):** Directiva N° 001-2025-GEG/INDECOPI (inciso 7.1.3), plazo de **cuatro (4) días hábiles**, bajo apercibimiento de incorporar los documentos como **públicos**.
   - **Por solicitud formal:** Directiva N° 001-2008/TRI-INDECOPI, exigir justificación objetiva y **versión pública / resumen no confidencial**.
   - **De Oficio ante Salud Ultrasensible (VIH/SIDA, cáncer grave):** Disponer de oficio la reserva inmediata y cuaderno confidencial tutelar.
6. **DISTINCIÓN DESGRAVAMEN VS. VIDA (FALLECIMIENTO):**
   - **Desgravamen:** Quienes denuncian son los herederos forzosos a través de la **Sucesión Intestada** (SUNARP) + ratificación de **TODOS los coherederos**, pues extingue la deuda en beneficio de la masa.
   - **Vida:** El derecho corresponde a quien figure como **Beneficiario expreso en la póliza**. Solo en defecto de beneficiarios designados opera la Sucesión Intestada supletoria.
7. **FILTRO MYPE (PDT 150 UIT):**
   Si la denunciante o contratante es persona jurídica o adquiere con RUC 20 / comercial: exigir declaraciones juradas mensuales **PDT 621** de los 12 meses anteriores para verificar ventas < 150 UIT y asimetría informativa (Art. IV.1.b Ley 29571 y D.S. 013-2013-PRODUCE).
8. **FIRMAS OFICIALES:**
   - Titular: `EVELING ROA QUISPE / SECRETARIA TECNICA`.
   - Ad Hoc (solo para Rímac Seguros): `LUISA ANALI SILVA MALPARTIDA / SECRETARIA TECNICA AD HOC`.
   - Prohibido el sufijo `(e)`.
9. **MICRO-TIPOGRAFÍA DETERMINISTA:**
   - Arial Narrow 11 pt, interlineado 1.0, espaciado 0 pt.
   - Superíndices obligatorios para `N°`.
   - Ordinal canónico `SÉTIMO` (prohibido SÉPTIMO o SETIMO). Prohibido UNDÉCIMO y DUODÉCIMO (usar `DÉCIMO PRIMERO`, `DÉCIMO SEGUNDO`).
   - Cero etiquetas `<w:highlight>` o `<w:shd>` en el OpenXML.

---

## 2. COMANDOS DE EJECUCIÓN DIRECTA (SIN EXCEL)

```bash
# 1. Crear y certificar una resolución en Word directamente:
python scripts/requerimiento.py crear-caso \
  --expediente "3125-2026/CC1" \
  --denunciante "MIGUEL ANGEL CORDOVA LOPEZ" \
  --denunciado "INTERBANK - BANCO INTERNACIONAL DEL PERU" \
  --producto "desgravamen" \
  --cobertura "fallecimiento" \
  --cautelar "solicita cautelar en el escrito" \
  --confidencialidad "mdpv" \
  --salida "generados/REQ 3125-2026 R1.docx"

# 2. Procesar desde un archivo JSON estructurado de caso:
python scripts/requerimiento.py procesar-caso "caso_01.json" --salida "generados/REQ 0098-2026 R1.docx"

# 3. Certificar cualquier resolución Word existente:
python scripts/requerimiento.py entregar "generados/REQ 3125-2026 R1.docx"
```
