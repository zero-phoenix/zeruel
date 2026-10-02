"""Generador determinista de Resolución de Improcedencia a SUSALUD para el Expediente 2846-2026/CC1.
Basado en el modelo oficial de IAFAS (SOAT gastos médicos) con preservación del 100% de notas al pie OpenXML,
formato institucional M-CPC-05/02 y conversión oficial vía Word COM a PDF y renderizado de páginas PNG.
"""

import os
import shutil
import zipfile
import re
from pathlib import Path
import docx
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
import win32com.client
import fitz

DEFAULT_TEMPLATE = Path(os.environ.get("SUSALUD_TEMPLATE_PATH", Path.home() / "Code/repos/SystemHope-ResAdmis/Modelos al 30-06-26/MODELOS IMPROCEDENCIAS (incluye adm mas impro y otros)/MODELOS IMPROS SUSALUD CON FUNDAMENTO MEJORADO/2685-2025 RXX IMPRO SUSALUD okOK .docx"))
DEFAULT_OUTPUT_DIR = Path(os.environ.get("SUSALUD_OUTPUT_DIR", Path.home() / "Desktop/2846-2026 impro susalud"))

BASE_TEMPLATE = DEFAULT_TEMPLATE
OUTPUT_DIR = DEFAULT_OUTPUT_DIR
OUTPUT_DOCX = OUTPUT_DIR / "RESOLUCION_2846-2026_CC1_IMPRO_SUSALUD.docx"
OUTPUT_PDF = OUTPUT_DIR / "RESOLUCION_2846-2026_CC1_IMPRO_SUSALUD.pdf"
PAGES_DIR = OUTPUT_DIR / "paginas_resolucion"

def strip_highlights(doc):
    for p in doc.paragraphs:
        for r in p.runs:
            rPr = r._r.find(qn('w:rPr'))
            if rPr is not None:
                highlight = rPr.find(qn('w:highlight'))
                if highlight is not None:
                    rPr.remove(highlight)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    for r in p.runs:
                        rPr = r._r.find(qn('w:rPr'))
                        if rPr is not None:
                            highlight = rPr.find(qn('w:highlight'))
                            if highlight is not None:
                                rPr.remove(highlight)

def replace_in_paragraph(p, old_text, new_text):
    if old_text in p.text:
        # If single run contains it
        for r in p.runs:
            if old_text in r.text:
                r.text = r.text.replace(old_text, new_text)
                return
        # If text spans across runs, replace in first run and clear others
        p.text = p.text.replace(old_text, new_text)

def build_resolution():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Copy base template to output
    shutil.copy2(BASE_TEMPLATE, OUTPUT_DOCX)
    doc = docx.Document(OUTPUT_DOCX)
    
    # 2. Update Header
    for s in doc.sections:
        for hp in s.header.paragraphs:
            if "2685-2025" in hp.text:
                for r in hp.runs:
                    if "2685-2025" in r.text:
                        r.text = r.text.replace("2685-2025", "2846-2026")
    
    # 3. Update Metadata & Header block
    # P0-P4
    for p in doc.paragraphs[:15]:
        if "17/04/2026" in p.text:
            replace_in_paragraph(p, "17/04/2026", "29/01/2027")
        if "XXXX-2025/CC1" in p.text:
            replace_in_paragraph(p, "XXXX-2025/CC1", "XXXX-2026/CC1")
        if "TEODORA GUADALUPE CHALLCO" in p.text:
            p.text = "DENUNCIANTE\t:\tCÉSAR FERNANDO PONCE TIRADO (SEÑOR PONCE)\n\t\tALMA DELIA HERRERA GUERRERO (SEÑORA HERRERA)"
            # apply font
            for r in p.runs:
                r.font.name = "Arial Narrow"
                r.font.size = docx.shared.Pt(11)
        if "MAPFRE PERÚ" in p.text:
            p.text = "DENUNCIADO\t:\tPACÍFICO COMPAÑÍA DE SEGUROS Y REASEGUROS S.A. (PACÍFICO)"
            for r in p.runs:
                r.font.name = "Arial Narrow"
                r.font.size = docx.shared.Pt(11)
        if "ACTIVIDADES RELACIONADAS CON LA SALUD HUMANA" in p.text:
            p.text = "ACTIVIDAD\t:\tPLANES DE SEGUROS GENERALES / SALUD (SOAT)"
            for r in p.runs:
                r.font.name = "Arial Narrow"
                r.font.size = docx.shared.Pt(11)
        if "Lima, xx de diciembre de 2025" in p.text:
            p.text = "Lima, xx de octubre de 2026"
            for r in p.runs:
                r.font.name = "Arial Narrow"
                r.font.size = docx.shared.Pt(11)

    # 4. Antecedentes (P17 a P33)
    p17 = doc.paragraphs[17]
    p17.text = (
        "Mediante escrito del 7 de agosto de 2026, subsanado mediante escrito del 29 de setiembre de 2026, "
        "el señor Ponce y la señora Herrera denunciaron a Pacífico por presuntas infracciones a la Ley N° 29571, "
        "Código de Protección y Defensa del Consumidor (en adelante, el Código), señalando lo siguiente:"
    )
    for r in p17.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    p19 = doc.paragraphs[19]
    p19.text = (
        "El 25 de mayo de 2026, a las 10:24 horas aproximadamente, en la intersección de la Av. República de Panamá "
        "con la Av. Tomás Marsano, distrito de Surquillo, ocurrió un accidente de tránsito en el que intervino el vehículo "
        "conducido por el señor Ponce, el cual contaba con el Seguro Obligatorio de Accidentes de Tránsito (en adelante, SOAT) "
        "emitido por Pacífico mediante Póliza N° 2012393904."
    )
    for r in p19.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    p21 = doc.paragraphs[21]
    p21.text = (
        "Con fecha 25 de mayo de 2026, se solicitó a la compañía aseguradora la cobertura de gastos médicos derivados del siniestro, "
        "ante lo cual Pacífico emitió inicialmente una Carta de Garantía por el monto de S/ 150,00."
    )
    for r in p21.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    p23 = doc.paragraphs[23]
    p23.text = (
        "Sin embargo, al día siguiente dicha cobertura fue denegada. Posteriormente, mediante Carta N° GSIN-1315082/2026 "
        "de fecha 29 de mayo de 2026, dirigida a la señora Herrera, Pacífico rehusó definitivamente otorgar la cobertura del SOAT "
        "aduciendo que, según la boleta de venta del vehículo menor, este registraba una velocidad de construcción de 40 km/h, "
        "superando el límite de 25 km/h establecido en el artículo 90° de la Resolución Ministerial N° 308-2019-MTC/01 para "
        "Vehículos de Movilidad Personal (VMP), alegando que el vehículo requería placa y SOAT propio."
    )
    for r in p23.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    p25 = doc.paragraphs[25]
    p25.text = (
        "Los denunciantes manifestaron que dicha denegatoria resulta arbitraria e injustificada, pues la normativa prohíbe desamparar "
        "a la víctima o denegar la cobertura médica de emergencia, pretendiendo la aseguradora exonerarse indebidamente de su obligación coberturadora."
    )
    for r in p25.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    p27 = doc.paragraphs[27]
    p27.text = (
        "En tal sentido, los denunciantes solicitaron como medida correctiva que Pacífico cumpla con otorgar la cobertura integral de gastos médicos "
        "del Seguro Obligatorio de Accidentes de Tránsito de conformidad con la póliza contratada. Asimismo, solicitaron el pago de costas y costos."
    )
    for r in p27.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # Limpiar párrafos residuales de antecedentes que eran específicos del caso anterior (P29, P31, P33)
    doc.paragraphs[29].text = ""
    doc.paragraphs[31].text = ""
    doc.paragraphs[33].text = ""

    # 5. Análisis - Reemplazos específicos manteniendo intactas las notas al pie legales
    for i, p in enumerate(doc.paragraphs[35:92], start=35):
        # Sustituir nombres preservando runs
        if "señora Challco" in p.text:
            for r in p.runs:
                if "señora Challco" in r.text:
                    r.text = r.text.replace("señora Challco", "señor Ponce y la señora Herrera")
        if "Mapfre" in p.text:
            for r in p.runs:
                if "Mapfre" in r.text:
                    r.text = r.text.replace("Mapfre", "Pacífico")
    
    # P37 título de acápite
    doc.paragraphs[37].text = "Sobre la improcedencia de la denuncia interpuesta por el señor Ponce y la señora Herrera"
    for r in doc.paragraphs[37].runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        r.bold = True

    # P77 transición
    doc.paragraphs[77].text = (
        "A continuación, se determinará la autoridad competente para conocer la denuncia interpuesta por el señor Ponce "
        "y la señora Herrera contra Pacífico, de ser el caso, imponer las sanciones correspondientes."
    )
    for r in doc.paragraphs[77].runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # P85 subsunción fáctica del caso concreto
    doc.paragraphs[85].text = (
        "En el presente caso, los denunciantes cuestionaron que Pacífico se habría negado injustificadamente a otorgar la cobertura "
        "de gastos médicos del Seguro Obligatorio de Accidentes de Tránsito (SOAT) bajo la Póliza N° 2012393904 respecto del siniestro "
        "ocurrido el 25 de mayo de 2026, emitiendo una denegatoria mediante Carta N° GSIN-1315082/2026; en ese sentido, cuestionaron que "
        "Pacífico habría brindado un deficiente servicio en relación con la cobertura y otorgamiento de gastos médicos asistenciales en su calidad "
        "de entidad aseguradora (IAFAS) bajo la póliza contratada."
    )
    for r in doc.paragraphs[85].runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # P87 conclusión del análisis
    doc.paragraphs[87].text = (
        "En consecuencia, la Comisión considera que corresponde declarar improcedente la denuncia interpuesta por el señor Ponce "
        "y la señora Herrera contra Pacífico, en la medida que la conducta cuestionada resulta ser materia de exclusiva competencia de Susalud."
    )
    for r in doc.paragraphs[87].runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # 6. RESUELVE (P92 a P97)
    p93 = doc.paragraphs[93]
    # Set bold on ordinal only
    p93.text = ""
    r1 = p93.add_run("PRIMERO: ")
    r1.bold = True
    r1.font.name = "Arial Narrow"
    r1.font.size = docx.shared.Pt(11)
    r2 = p93.add_run(
        "declarar improcedente la denuncia interpuesta por el señor César Fernando Ponce Tirado y la señora Alma Delia Herrera Guerrero "
        "contra Pacífico Compañía de Seguros y Reaseguros S.A., por presunta infracción a la Ley N° 29571, Código de Protección y Defensa del Consumidor, "
        "en la medida que ha quedado acreditado que la conducta cuestionada resulta ser materia de exclusiva competencia de la Superintendencia Nacional de Salud. "
        "En consecuencia, disponer la devolución a los denunciantes de la tasa por derecho de trámite pagada, ascendente a S/ 36,00 (treinta y seis con 00/100 Soles), "
        "previa solicitud a la Unidad de Finanzas y Contabilidad del Indecopi."
    )
    r2.bold = False
    r2.font.name = "Arial Narrow"
    r2.font.size = docx.shared.Pt(11)

    p95 = doc.paragraphs[95]
    p95.text = ""
    r3 = p95.add_run("SEGUNDO: ")
    r3.bold = True
    r3.font.name = "Arial Narrow"
    r3.font.size = docx.shared.Pt(11)
    r4 = p95.add_run(
        "ordenar a la Secretaría Técnica de la Comisión de Protección al Consumidor N° 1 que remita el original de todo lo actuado en el presente procedimiento "
        "a la Superintendencia Nacional de Salud, a efectos de que adopte las medidas correspondientes en el ámbito de su competencia."
    )
    r4.bold = False
    r4.font.name = "Arial Narrow"
    r4.font.size = docx.shared.Pt(11)

    p97 = doc.paragraphs[97]
    p97.text = ""
    r5 = p97.add_run("TERCERO: ")
    r5.bold = True
    r5.font.name = "Arial Narrow"
    r5.font.size = docx.shared.Pt(11)
    r6 = p97.add_run(
        "informar a los señores César Fernando Ponce Tirado y Alma Delia Herrera Guerrero que la presente resolución tiene vigencia desde el día de su notificación "
        "y no agota la vía administrativa. En tal sentido, de conformidad con lo dispuesto por el artículo 38° del Decreto Legislativo Nº 807, el único recurso impugnativo "
        "que puede interponerse contra lo dispuesto por la Comisión de Protección al Consumidor N° 1 es el de apelación, el cual debe ser presentado ante dicho órgano colegiado "
        "en un plazo no mayor de quince (15) días hábiles, contado a partir del día siguiente de su notificación, ello de acuerdo con lo establecido en el artículo 218° del Texto Único Ordenado "
        "de la Ley N° 27444, Ley del Procedimiento Administrativo General, aprobado por Decreto Supremo N° 004-2019-JUS; caso contrario, la resolución quedará consentida."
    )
    r6.bold = False
    r6.font.name = "Arial Narrow"
    r6.font.size = docx.shared.Pt(11)

    # P98 y P99: Fórmula colegiada oficial
    p98 = doc.paragraphs[98]
    p98.text = "Con la intervención de los señores Comisionados: Mónica Tatiana Siverio Puycan, María de Fátima Ponce Regalado, Ernesto Alonso Calderón Burneo y Aldrin Capcha Coronado."
    for r in p98.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
    
    p99 = doc.paragraphs[99]
    p99.text = "MÓNICA TATIANA SIVERIO PUYCAN\nPresidenta\nComisión de Protección al Consumidor N° 1"
    for r in p99.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        r.bold = True

    # 7. Limpiar resaltados y guardar
    strip_highlights(doc)
    doc.save(OUTPUT_DOCX)
    print("DOCX_GENERADO_EXITOSAMENTE:", OUTPUT_DOCX)

def convert_to_pdf_and_render_pages():
    print("CONVIRTIENDO A PDF VIA WORD COM...")
    word = win32com.client.Dispatch("Word.Application")
    word.Visible = False
    try:
        doc = word.Documents.Open(str(OUTPUT_DOCX))
        doc.SaveAs(str(OUTPUT_PDF), FileFormat=17) # 17 = wdFormatPDF
        doc.Close()
    finally:
        word.Quit()
    print("PDF_GENERADO_EXITOSAMENTE:", OUTPUT_PDF)

    # Render pages with fitz
    print("RENDERIZANDO PAGINAS A PNG (150 DPI)...")
    pdf_doc = fitz.open(OUTPUT_PDF)
    print(f"TOTAL PAGINAS RENDERIZADAS: {len(pdf_doc)}")
    image_paths = []
    for i, page in enumerate(pdf_doc):
        pix = page.get_pixmap(dpi=150)
        img_path = PAGES_DIR / f"pagina_{i+1:02d}.png"
        pix.save(img_path)
        image_paths.append(img_path)
        print(f"  Página {i+1} guardada en: {img_path.name}")
    return image_paths

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Generador determinista de Resolución de Improcedencia SUSALUD.")
    parser.add_argument("--template", type=Path, default=DEFAULT_TEMPLATE, help="Ruta a plantilla Word DOCX")
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR, help="Directorio de salida")
    args = parser.parse_args()

    BASE_TEMPLATE = args.template
    OUTPUT_DIR = args.output_dir
    OUTPUT_DOCX = OUTPUT_DIR / "RESOLUCION_2846-2026_CC1_IMPRO_SUSALUD.docx"
    OUTPUT_PDF = OUTPUT_DIR / "RESOLUCION_2846-2026_CC1_IMPRO_SUSALUD.pdf"
    PAGES_DIR = OUTPUT_DIR / "paginas_resolucion"

    if not BASE_TEMPLATE.exists():
        print(f"[WARN] Plantilla no encontrada: {BASE_TEMPLATE}")
        print("Especifique una plantilla válida mediante --template o variable de entorno SUSALUD_TEMPLATE_PATH.")
    else:
        build_resolution()
        convert_to_pdf_and_render_pages()
