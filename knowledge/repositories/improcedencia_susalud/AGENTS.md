# AGENTS.md — Protocolo Operativo y Reglas Críticas del Sistema

Este repositorio alberga el sistema determinista de generación, verificación y auditoría de **Resoluciones de Improcedencia (Total o Parcial) a SUSALUD** emitidas por la **Comisión de Protección al Consumidor N° 1 (CC1)** del Indecopi.

Cualquier agente de IA o desarrollador que interactúe con este repositorio DEBE acatar estrictamente las siguientes reglas operativas:

---

## 1. REGLA FUNDAMENTAL DE COMPETENCIA Y FIRMA (CERO SECRETARÍA TÉCNICA)

> [!CRITICAL]
> **A diferencia de las resoluciones de admisibilidad o requerimiento de subsanación:**
> - Las resoluciones de improcedencia **NUNCA son emitidas ni suscritas por la Secretaría Técnica**.
> - Son actos resolutivos de fondo/calificación que deciden sobre la competencia material y ponen fin a la instancia (en improcedencias totales) o declaran inadmisible/improcedente determinados extremos (en parciales).
> - Son emitidas y suscritas exclusivamente por el **Órgano Colegiado de la Comisión de Protección al Consumidor N° 1 (CC1)**.
> - Al final del documento se inserta la fórmula de intervención colegiada: *"Con la intervención de los señores comisionados: [Nombres] / Miembros de la Comisión de Protección al Consumidor N° 1"*.

---

## 2. DIFERENCIACIÓN DOGMÁTICA Y NORMATIVA VINCULANTE: IAFAS vs. IPRESS

El agente debe categorizar con exactitud milimétrica a la entidad denunciada e invocar la norma legal correspondiente:

### A. Si la denunciada es una IAFAS (Aseguradoras, EPS, Medicina Prepagada, SIS, EsSalud):
- **Definición legal:** Citar expresamente el **artículo 3°, numeral 2 del Decreto Legislativo N° 1158**.
- **Normas sectoriales conexas:** **Ley N° 29344** (Ley Marco de Aseguramiento Universal en Salud) y su Reglamento aprobado por **Decreto Supremo N° 008-2010-SA**.
- **Materias bajo competencia SUSALUD:** Coberturas de planes de salud, exclusión por preexistencias, periodos de carencia o latencia, copagos, reembolsos de gastos médicos, desafiliación unilateral de seguros de salud.

### B. Si la denunciada es una IPRESS (Clínicas, Hospitales, Centros Médicos, Laboratorios):
- **Definición legal:** Citar expresamente el **artículo 3°, numeral 3 del Decreto Legislativo N° 1158**.
- **Normas sectoriales conexas:** **Ley N° 26842** (Ley General de Salud), Título I y II (derechos de los pacientes, acto médico).
- **Materias bajo competencia SUSALUD:** Calidad, idoneidad y oportunidad del acto médico asistencial, diagnóstico, cirugías, tratamientos, entrega y reserva de historia clínica, consentimiento informado, presunta mala praxis médica, facturación hospitalaria derivada directamente de la prestación médica asistencial.

### C. Si la denuncia es Mixta (Concurrencia IAFAS + IPRESS):
- Citar ambos numerales (2 y 3) del artículo 3° del D. Leg. 1158.
- Delimitar el ámbito de aseguramiento (IAFAS) y el ámbito de prestación médica (IPRESS), señalando que ambos convergen en la competencia material exclusiva de SUSALUD.

---

## 3. MODALIDADES: IMPROCEDENCIA TOTAL vs. IMPROCEDENCIA PARCIAL

### A. Improcedencia Total:
- Todos los hechos recaen en el ámbito de competencia de SUSALUD.
- Resuelve:
  - Art. 1°: Declarar IMPROCEDENTE la denuncia por incompetencia por razón de la materia.
  - Art. 2°: Remitir actuados a SUSALUD (o dejar a salvo el derecho).
  - Art. 3°: Disponer el archivo definitivo ante la CC1 tras quedar firme.

### B. Improcedencia Parcial:
- Concurrencia de hechos: unos de competencia SUSALUD (médico / cobertura) y otros de competencia Indecopi (ej. negativa de entrega de Libro de Reclamaciones, falta de respuesta al reclamo conforme al Código de Protección y Defensa del Consumidor).
- Resuelve:
  - Art. 1°: Declarar IMPROCEDENTE la denuncia respecto de los extremos médicos/cobertura a SUSALUD por incompetencia por razón de la materia.
  - Art. 2°: Disponer que continúe el trámite de la denuncia respecto de los extremos de competencia de la Comisión / Indecopi.
  - Art. 3°: Remitir copia de los actuados a SUSALUD respecto de los extremos improcedentes (o dejar a salvo el derecho).

---

## 4. ESTÁNDARES TIPOGRÁFICOS Y DE ARQUITECTURA OPENXML
1. NUNCA crear un `.docx` en blanco: se clona la plantilla institucional oficial con márgenes y membretes institucionales.
2. Tipografía: **Arial Narrow 11 pt** en todo el cuerpo, notas y cuadros.
3. Superíndices OpenXML: para `N°` y números ordinales (`1°`, `2°`), el símbolo `°` debe ir en `<w:vertAlign w:val="superscript"/>`.
4. Cero resaltados XML (`<w:highlight>`).
5. Cero variables residuales o corchetes (`[XXX]`).
