"""Generador oficial y determinista de la Resolución de Improcedencia a SUSALUD
para el Expediente 2846-2026/CC1.
Reproduce con exactitud milimétrica la estructura, maquetación, notas al pie OpenXML
y distribución de 9 páginas del modelo oficial 0146-2026-CC1 (IAFAS - SOAT gastos médicos).
"""

import os
import sys
import shutil
import zipfile
import re
from pathlib import Path
import docx
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
import win32com.client
import fitz

BASE_TEMPLATE = Path(r"C:\Users\D\Code\repos\SystemHope-ResAdmis\Modelos al 30-06-26\MODELOS IMPROCEDENCIAS (incluye adm mas impro y otros)\MODELOS IMPROS SUSALUD CON FUNDAMENTO MEJORADO\2685-2025 RXX IMPRO SUSALUD okOK .docx")
OUTPUT_DIR = Path(r"C:\Users\D\Desktop\2846-2026 impro susalud")
OUTPUT_DOCX = OUTPUT_DIR / "RESOLUCION_2846-2026_CC1_IMPRO_SUSALUD.docx"
OUTPUT_PDF = OUTPUT_DIR / "RESOLUCION_2846-2026_CC1_IMPRO_SUSALUD.pdf"
PAGES_DIR = OUTPUT_DIR / "paginas_resolucion"

# Textos canónicos de las 21 notas al pie del modelo 0146-2026-CC1
FOOTNOTES_DATA = {
    1: "Publicado el 2 de setiembre del 2010 en el Diario Oficial El Peruano y vigente desde el 2 de octubre del 2010.",
    2: ("LEY 29751, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicada el 2 de setiembre de 2010\n"
        "Artículo 105.- Autoridad competente\n"
        "El Instituto Nacional de Defensa de la Competencia y de la Protección de la Propiedad Intelectual (Indecopi) es la autoridad con competencia primaria y de alcance nacional para conocer las presuntas infracciones a las disposiciones contenidas en el presente capítulo, conforme al Decreto legislativo núm. 1033, Ley de Organización y Funciones del Indecopi. Dicha competencia solo puede ser negada cuando ella haya sido asignada o se asigne a favor de otro organismo por norma expresa con rango de ley.\n(…)"),
    3: "Ver Resolución 277-1999/TDC-INDECOPI del 18 de agosto de 1999, seguido por Shirley Sánchez Cama contra José Cantuarias Pacheco y Corporación José R. Lindley S.A.",
    4: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
        "Artículo 1.- Objeto de la norma\n"
        "El presente Decreto Legislativo tiene por objeto disponer las medidas destinadas al fortalecimiento de las funciones que actualmente desarrolla la Superintendencia Nacional de Aseguramiento en Salud, con la finalidad de promover, proteger y defender los derechos de las personas al acceso a los servicios de salud, supervisando que las prestaciones sean otorgadas con calidad, oportunidad, disponibilidad y aceptabilidad, con independencia de quien la financie."),
    5: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
        "Artículo 5.- Ámbito de competencia\n"
        "La Superintendencia Nacional de Salud es una entidad desconcentrada y sus competencias son de alcance nacional. Se encuentran bajo el ámbito de competencia de la Superintendencia todas las Instituciones Administradoras de Fondos de Aseguramiento en Salud (IAFAS), así como todas las Instituciones Prestadoras de Servicios de Salud (IPRESS), Asimismo, se encuentran bajo el ámbito de competencia de la Superintendencia las Unidades de Gestión de IPRESS, definidas como aquellas entidades o empresas públicas, privadas o mixtas, creadas o por crearse, diferentes de las IPRESS, encargadas de la administración y gestión de los recursos destinados al funcionamiento idóneo de las IPRESS.\n(…)"),
    6: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
        "Artículo 6.- De las Instituciones Administradoras de Fondos de Aseguramiento en Salud – IAFAS\n"
        "Las Instituciones Administradoras de Fondos de Aseguramiento en Salud (IAFAS) son aquellas entidades o empresas públicas, privadas o mixtas, creadas o por crearse, que reciban, capten y/o gestionen fondos para la cobertura de las atenciones de salud o que oferten cobertura de riesgos de salud, bajo cualquier modalidad. El registro en la Superintendencia Nacional de Salud es requisito indispensable para la oferta de las coberturas antes señaladas.\n\n"
        "Son IAFAS las siguientes:\n"
        "1.  Seguro Integral de Salud.\n"
        "2.  Seguro Social de Salud (EsSalud), excluyendo la cobertura de prestaciones económicas y sociales.\n"
        "3.  Fondo Intangible Solidario de Salud (FISSAL).\n"
        "4.  Fondos de Aseguramiento en Salud de las Fuerzas Armadas y de la Policía Nacional del Perú.\n"
        "5.  Entidades Prestadoras de Salud (EPS).\n"
        "6.  Empresas de Seguros contempladas en los numerales 1, 2 y 3 del inciso d) del artículo 16° de la Ley 26702, que oferten cobertura de riesgos de salud de modo exclusivo o en adición a otro tipo de coberturas.\n"
        "7.  Asociaciones de Fondos Regionales y Provinciales Contra Accidentes de Tránsito (AFOCAT).\n"
        "8.  Entidades de Salud que ofrecen servicios de salud prepagadas.\n"
        "9.  Autoseguros y fondos de salud, que gestionen fondos para la cobertura de salud de modo exclusivo o en adición a otro tipo de coberturas.\n"
        "10.  Otras modalidades de aseguramiento público, privado o mixto distintas a las señaladas anteriormente.\n\n"
        "Artículo 7.-De las Instituciones Prestadoras de Servicios de Salud – IPRESS\n"
        "Las Instituciones Prestadoras de Servicios de Salud (IPRESS) son aquellos establecimientos de salud y servicios médicos de apoyo, públicos, privados o mixtos, creados o por crearse, que realizan atención de salud con fines de prevención, promoción, diagnóstico, tratamiento y/o rehabilitación; así como aquellos servicios complementarios o auxiliares de la atención médica, que tienen por finalidad coadyuvar en la prevención, promoción, diagnóstico, tratamiento y/o rehabilitación de la salud. En adición al cumplimiento de las normas de carácter general del Ministerio de Salud, para brindar servicios de salud deberán encontrarse registradas en la Superintendencia Nacional de Salud."),
    7: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
        "Artículo 10.- Potestad sancionadora de la Superintendencia\n"
        "Para el ejercicio de las funciones establecidas en los artículos 8 y 9 del presente Decreto Legislativo, la Superintendencia Nacional de Salud cuenta con potestad sancionadora sobre toda acción u omisión que afecte: i) el derecho a la vida, la salud, la información de las personas usuarias de los servicios de salud y la cobertura para su aseguramiento, y; ii) los estándares de acceso, calidad, oportunidad, disponibilidad y aceptabilidad con que dichas prestaciones sean otorgadas.\n(…)"),
    8: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
        "Artículo 11.- Tipos de Sanciones\n"
        "La Superintendencia Nacional de Salud, de acuerdo a la gravedad de la infracción cometida, puede imponer a las IAFAS, IPRESS y Unidades de Gestión de IPRESS, vinculadas al Sistema Nacional de Salud, los siguientes tipos de sanción:\n"
        "a.  Amonestación escrita;\n"
        "b.  Multa hasta un monto máximo de quinientas (500) UIT;\n"
        "c.  Suspensión de la Autorización de Funcionamiento para IAFAS, hasta por un plazo máximo de seis (6) meses, cuyo efecto consiste en el impedimento para realizar nuevas afiliaciones;\n"
        "d.  Restricción de uno o más servicios de IPRESS, hasta por un plazo máximo de seis (6) meses;\n"
        "e.  Cierre temporal para IPRESS, hasta por un plazo máximo de seis (6) meses;\n"
        "f.  Revocación de la Autorización de Funcionamiento para IAFAS;\n"
        "g.  Cierre definitivo para IPRESS.\n(…)"),
    9: ("ANEXO I INFRACCIONES APLICABLES A LAS IAFAS\n"
        "ANEXO I - C INFRACCIONES APLICABLES A LAS IAFAS DE SEGUROS CONTEMPLADAS EN EL NUMERAL 6 DEL ARTÍCULO 6° DEL DL 1158\n"
        "INFRACCIONES GRAVES\n"
        "1. No brindar cobertura oportuna a los afiliados o sus beneficiarios de acuerdo a las condiciones pactadas y la normatividad vigente emitida por la SBS."),
    10: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
         "Artículo 10.- Potestad sancionadora de la Superintendencia\n(…)\n"
         "Sin perjuicio de las sanciones que en el marco de su competencia imponga la Superintendencia Nacional de Salud, podrá ordenar la implementación de una o más medidas correctivas, con el objetivo de corregir o revertir los efectos que la conducta infractora hubiere ocasionado o evitar que esta se produzca nuevamente.\n(…)"),
    11: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
         "Artículo 14.- Medidas correctivas\n"
         "Las medidas correctivas se dictan conjuntamente con la resolución que impone la sanción, y tienen por finalidad corregir o revertir los efectos que la conducta infractora hubiere ocasionado o evitar que ésta se produzca nuevamente en el futuro. Sin perjuicio de las sanciones administrativas a que hubiere lugar, la Superintendencia podrá ordenar la implementación de una o más de las siguientes medidas correctivas:\n"
         "1.   Devolver los cobros indebidos o en exceso, según la cobertura de los planes de salud correspondientes.\n"
         "2.  Cumplir con atender la solicitud de información requerida por el asegurado, siempre que dicho requerimiento guarde relación con su cobertura de salud y/o afecte el ejercicio de sus derechos;\n"
         "3.  Declarar inexigibles las cláusulas de sus contratos o convenios que han sido identificadas como abusivas;\n"
         "4. Publicar avisos rectificatorios o informativos en la forma que determine la Superintendencia Nacional de Salud tomando en consideración los medios que resulten idóneos para revertir los efectos que el acto materia de sanción hubiere ocasionado;\n"
         "5.  Someter a la IAFAS al Régimen de Vigilancia, entendido como el proceso de supervisión continua a la IAFAS previa presentación de su Plan de Recuperación, el cual será aprobado por la Superintendencia Nacional de Salud.\n(..)"),
    12: ("DECRETO LEGISLATIVO QUE DISPONE MEDIDAS DESTINADAS AL FORTALECIMIENTO Y CAMBIO DE DENOMINACIÓN DE LA SUPERINTENDENCIA NACIONAL DE ASEGURAMIENTO EN SALUD, aprobada por DECRETO LEGISLATIVO 1158 y publicado 6 de diciembre de 2013\n"
         "Artículo 15.- Multas coercitivas\n"
         "Si los infractores sancionados son renuentes al cumplimiento de la sanción, o de las medidas correctivas ordenadas, dentro del plazo otorgado, se les impondrá una multa coercitiva no menor de tres (3) UIT. Si el administrado persistiese en el incumplimiento, se podrá imponer una nueva multa coercitiva, la cual podrá ser reiterada en forma trimestral, duplicando sucesivamente el monto de la última multa impuesta, hasta el límite de cincuenta (50) UIT. La multa que corresponda debe ser pagada dentro del plazo de quince (15) días hábiles de notificada."),
    13: ("REGLAMENTO DEL PROCEDIMIENTO DE TRANSFERENCIA DE FUNCIONES DEL INSTITUTO NACIONAL DE DEFENSA DE LA COMPETENCIA Y DE LA PROTECCIÓN DE LA PROPIEDAD INTELECTUAL - INDECOPI A LA SUPERINTENDENCIA NACIONAL DE SALUD - SUSALUD EN EL MARCO DE LO DISPUESTO POR EL DECRETO LEGISLATIVO 1158, aprobado por DECRETO SUPREMO N° 026-2015-SA  y publicado el 13 de agosto de 2015\n"
         "Artículo 5.- Competencias Generales de la Superintendencia Nacional de Salud\n"
         "5.1.  SUSALUD es la autoridad competente para promover, proteger y defender los derechos de las personas al acceso a los servicios de salud, supervisando que las prestaciones sean otorgadas con calidad, oportunidad, disponibilidad y aceptabilidad, con independencia de quien las financie, así como los que correspondan en su relación de consumo con las IAFAS e IPRESS, incluyendo aquellas previas y derivadas de dicha relación; así como para conocer con competencia primaria y alcance nacional, las presuntas infracciones a las disposiciones relativas a la protección de los derechos de los usuarios en su relación de consumo con la IPRESS y/o IAFAS.\n"
         "5.2.  SUSALUD es competente también para identificar las cláusulas abusivas en los contratos o convenios que suscriben las IAFAS con los asegurados o entidades que los representen, según las disposiciones aplicables de la Ley N° 29571, Código de Protección y Defensa del Consumidor, con excepción de las pólizas de seguros de las Empresas de Seguros bajo el control de la Superintendencia de Banca, Seguros y Administradoras Privadas de Fondos de Pensiones, sin perjuicio de la protección al consumidor o usuario directamente afectado respecto de la aplicación de la referida cláusula en el caso en concreto.\n"
         "5.3.  SUSALUD velará por el cumplimiento de la Ley N° 29571, Código de Protección y Defensa del Consumidor y sus normas complementarias y conexas, en materia de protección de los derechos de los usuarios de los servicios de salud, por la falta de idoneidad de los servicios ofrecidos por las IAFAS, IPRESS y UGIPRESS, ejerciendo su potestad sancionadora en el marco de lo establecido en el Decreto Legislativo N° 1158."),
    14: ("REGLAMENTO DEL PROCEDIMIENTO DE TRANSFERENCIA DE FUNCIONES DEL INSTITUTO NACIONAL DE DEFENSA DE LA COMPETENCIA Y DE LA PROTECCIÓN DE LA PROPIEDAD INTELECTUAL - INDECOPI A LA SUPERINTENDENCIA NACIONAL DE SALUD - SUSALUD EN EL MARCO DE LO DISPUESTO POR EL DECRETO LEGISLATIVO 1158, aprobado por DECRETO SUPREMO N° 026-2015-SA  y publicado el 13 de agosto de 2015\n"
         "Artículo 9.- Procedimientos asumidos por SUSALUD\n"
         "SUSALUD asume competencia sobre todos aquellos actos u omisiones ocurridos a partir de la vigencia de la presente norma, que constituyan presuntas infracciones a las disposiciones relativas a la protección de los derechos de los usuarios en su relación de consumo con las instituciones bajo su ámbito de competencia, así como aquellas previas o derivadas de ésta.\n\n"
         "INDECOPI mantiene competencia sobre todos aquellos actos u omisiones ocurridos antes de la vigencia de la presente norma, en las materias señaladas en el párrafo precedente, hasta su conclusión en la vía administrativa, arbitral y/o sede judicial."),
    15: ("REGLAMENTO PARA LA ATENCIÓN DE RECLAMOS Y QUEJAS DE LOS USUARIOS DE LAS INSTITUCIONS ADMINISTRADORAS DE FONDOS DE ASEGURAMIENTO EN SALUD – IAFAS, INSTITUCIONES PRESTADORAS DE SERVICIOS DE SALUD – IPRESS Y UNIDAD DE GESTIÓN DE INSTITUCIONES PRESTADORAS DE SERVICIOS DE SALUD – UGIPRESS, PÚBLICAS, PRIVADAS Y MIXTAS, aprobado por DECRETO SUPREMO 030-2016-SA y publicado el 27 de julio de 2016\n"
         "Artículo 1.- Del objeto\n"
         "1.1. Establecer el procedimiento para la atención de las quejas y reclamos presentados por los usuarios o terceros legitimados ante la insatisfacción respecto de los servicios, prestaciones o coberturas solicitadas a, o recibidas de, las Instituciones Administradoras de Fondos de Aseguramiento en Salud – IAFAS o Instituciones Prestadoras de Servicios de Salud -IPRESS, o que dependan de las Unidades de Gestión de Instituciones Prestadoras de Servicios de Salud – UGIPRESS, públicas, privadas o mixtas.\n(…).\n"
         "Artículo 4.- Del ámbito de aplicación\n"
         "4.1. El presente Reglamento es aplicable a las IAFAS, IPRESS y UGIPRESS, públicas, privadas o mixtas a nivel nacional; a los usuarios o terceros legitimados en su relación con dichas instituciones, así como a SUSALUD.\n(…).\n"
         "Artículo 6.- De las instancias competentes\n(...)\n"
         "6.2. SUSALUD a través de IPROT o las Intendencias Macro Regionales de SUSALUD en caso de encargo de funciones, son competentes para la recepción, procesamiento, atención y absolución de las consultas, peticiones de intervención y quejas presentadas por los usuarios o terceros legitimados.\n(…).\n"
         "Artículo 12 .- De la canalización de reclamos\n"
         "Los reclamos presentados a las IAFAS, IPRESS O UGIPRESS por cualquier medio deberán ser canalizados por éstas al Libro de Reclamaciones en Salud Virtual o Físico, según corresponda."),
    16: ("REGLAMENTO DEL PROCEDIMIENTO DE TRANSFERENCIA DE FUNCIONES DEL INSTITUTO NACIONAL DE DEFENSA DE LA COMPETENCIA Y DE LA PROTECCIÓN DE LA PROPIEDAD INTELECTUAL - INDECOPI A LA SUPERINTENDENCIA NACIONAL DE SALUD - SUSALUD EN EL MARCO DE LO DISPUESTO POR EL DECRETO LEGISLATIVO 1158, APROBADO POR DECRETO SUPREMO N° 026-2015-SA Y PUBLICADO EL 13 DE AGOSTO DE 2015\n"
         "Artículo 5.- Competencias Generales de la Superintendencia Nacional de Salud\n(…)\n"
         "5.3.   SUSALUD velara por el cumplimiento de la Ley N° 29571, Código de Protección y Defensa del Consumidor y sus normas complementarias y conexas, en materia de protección de los derechos de los usuarios de los servicios de salud, por la falta de idoneidad de los servicios ofrecidos por las IAFAS, IPRESS y UGIPRESS, ejerciendo su potestad sancionadora en el marco de lo establecido en el Decreto Legislativo 1158."),
    17: ("REGLAMENTO DEL PROCEDIMIENTO DE TRANSFERENCIA DE FUNCIONES DEL INSTITUTO NACIONAL DE DEFENSA DE LA COMPETENCIA Y DE LA PROTECCIÓN DE LA PROPIEDAD INTELECTUAL - INDECOPI A LA SUPERINTENDENCIA NACIONAL DE SALUD - SUSALUD EN EL MARCO DE LO DISPUESTO POR EL DECRETO LEGISLATIVO N° 1158, APROBADO POR DECRETO SUPREMO N° 026-2015-SA Y PUBLICADO EL 13 DE AGOSTO DE 2015\n"
         "Artículo 8.- Competencias sobre Empresas de Seguros, SOAT y AFOCAT\n"
         "SUSALUD es competente para supervisar el cumplimiento de las normas que protegen a los consumidores en las IAFAS – Empresas de Seguros, incluidas las que oferten la cobertura del Seguro Obligatorio de Accidentes de Tránsito (SOAT), así como a las Asociaciones de Fondos Regionales y Provinciales Contra Accidentes de Tránsito (AFOCAT), ejerciendo su potestad sancionadora de acuerdo a lo establecido en el Decreto Legislativo N° 1158.\n"
         "La Superintendencia de Banca, Seguros y Administradoras Privadas de Fondos de Pensiones – SBS e INDECOPI, mantienen las facultades para actuar en la vía administrativa, en materias referidas a las coberturas para los casos de muerte, invalidez permanente, incapacidad temporal y gastos de sepelio, dentro de sus ámbitos de competencia, de acuerdo a la normativa vigente."),
    18: ("Directiva N° 001-2021-COD-INDECOPI, Directiva Única que regula los procedimientos de Protección al Consumidor previstos en el Código de Protección al Consumidor\n"
         "Artículo 13.- Improcedencia de la denuncia\n"
         "13.1 En los supuestos en que el órgano resolutivo determine que los hechos materia de denuncia deben ser conocidos por una Junta Arbitral de Consumo o Centro de Arbitraje, o un órgano regulador o supervisor distinto al INDECOPI, la resolución que declara la improcedencia de la denuncia dispone la remisión de los actuados a la entidad que corresponda y la devolución de la tasa pagada por el denunciante.\n(…)"),
    19: ("LEY 29571, CÓDIGO DE PROTECCIÓN Y DEFENSA DEL CONSUMIDOR, publicada el 2 de setiembre de 2010 y modificada por el Decreto Legislativo 1308, publicado el 30 de diciembre de 2016\n"
         "DISPOSICIONES COMPLEMENTARIAS MODIFICATORIAS.\n"
         "PRIMERA. - Modificación del artículo 38° del Decreto Legislativo núm. 807\n"
         "Modifícase el artículo 38° del Decreto Legislativo núm. 807, Ley sobre Facultades, Normas y Organización del Indecopi, con el siguiente texto:\n"
         "“Artículo 38º.- El único recurso impugnativo que puede interponerse durante la tramitación del procedimiento es el de apelación, que procede únicamente contra la resolución que pone fin a la instancia, contra la resolución que impone multas y contra la resolución que dicta una medida cautelar (…)”."),
    20: ("DECRETO SUPREMO N° 004-2019-JUS, TEXTO ÚNICO ORDENADO DE LA LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL, publicado el 25 de enero de 2019\n"
         "Artículo 218.- Recursos administrativos\n"
         "218.1  Los recursos administrativos son:\n(…)\n"
         "b)  Recurso de apelación\n (…)\n"
         "218.2  El término para la interposición de los recursos es de quince (15) días perentorios (…)."),
    21: ("DECRETO SUPREMO N° 004-2019-JUS, TEXTO ÚNICO ORDENADO DE LA LEY DEL PROCEDIMIENTO ADMINISTRATIVO GENERAL, publicado el 25 de enero de 2019\n\n"
         "Artículo 222.- Acto firme\n\n"
         "Una vez vencidos los plazos para interponer los recursos administrativos se perderá el derecho a articularlos quedando firme el acto.")
}

def build_footnotes_xml():
    """Genera el XML completo de word/footnotes.xml con las 21 notas al pie del modelo 0146-2026."""
    ns = (
        'xmlns:wpc="http://schemas.microsoft.com/office/word/2010/wordprocessingCanvas" '
        'xmlns:cx="http://schemas.microsoft.com/office/drawing/2014/chartex" '
        'xmlns:mc="http://schemas.openxmlformats.org/markup-compatibility/2006" '
        'xmlns:o="urn:schemas-microsoft-com:office:office" '
        'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
        'xmlns:m="http://schemas.openxmlformats.org/officeDocument/2006/math" '
        'xmlns:v="urn:schemas-microsoft-com:vml" '
        'xmlns:wp="http://schemas.openxmlformats.org/drawingml/2006/wordprocessingDrawing" '
        'xmlns:w10="urn:schemas-microsoft-com:office:word" '
        'xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main" '
        'xmlns:w14="http://schemas.microsoft.com/office/word/2010/wordml" '
        'xmlns:w15="http://schemas.microsoft.com/office/word/2012/wordml" '
        'xmlns:w16se="http://schemas.microsoft.com/office/word/2015/wordml/symex" '
        'mc:Ignorable="w14 w15 w16se"'
    )
    xml_parts = [f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<w:footnotes {ns}>']
    # Separador (-1)
    xml_parts.append(
        '<w:footnote w:type="separator" w:id="-1">'
        '<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
        '<w:r><w:separator/></w:r></w:p></w:footnote>'
    )
    # Separador de continuación (0)
    xml_parts.append(
        '<w:footnote w:type="continuationSeparator" w:id="0">'
        '<w:p><w:pPr><w:spacing w:after="0" w:line="240" w:lineRule="auto"/></w:pPr>'
        '<w:r><w:continuationSeparator/></w:r></w:p></w:footnote>'
    )
    
    for fid in range(1, 22):
        text = FOOTNOTES_DATA[fid]
        paragraphs = text.split("\n")
        xml_parts.append(f'<w:footnote w:id="{fid}">')
        for p_idx, p_txt in enumerate(paragraphs):
            xml_parts.append(
                '<w:p>'
                '<w:pPr>'
                '<w:pStyle w:val="FootnoteText"/>'
                '<w:jc w:val="both"/>'
                '</w:pPr>'
            )
            if p_idx == 0:
                xml_parts.append(
                    f'<w:r><w:rPr><w:rStyle w:val="FootnoteReference"/></w:rPr>'
                    f'<w:footnoteRef/></w:r>'
                    f'<w:r><w:rPr><w:rFonts w:ascii="Arial Narrow" w:hAnsi="Arial Narrow"/><w:sz w:val="16"/></w:rPr>'
                    f'<w:t xml:space="preserve">  {p_txt}</w:t></w:r>'
                )
            else:
                xml_parts.append(
                    f'<w:r><w:rPr><w:rFonts w:ascii="Arial Narrow" w:hAnsi="Arial Narrow"/><w:sz w:val="16"/></w:rPr>'
                    f'<w:t xml:space="preserve">{p_txt}</w:t></w:r>'
                )
            xml_parts.append('</w:p>')
        xml_parts.append('</w:footnote>')
        
    xml_parts.append('</w:footnotes>')
    return "".join(xml_parts)

def update_docx_package():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    PAGES_DIR.mkdir(parents=True, exist_ok=True)
    
    # 1. Copiar base docx
    shutil.copy2(BASE_TEMPLATE, OUTPUT_DOCX)
    
    # 2. Modificar document.xml y header1.xml directamente en el zip
    # Extraer el zip a una carpeta temporal
    temp_dir = OUTPUT_DIR / "_temp_docx"
    if temp_dir.exists():
        shutil.rmtree(temp_dir)
    temp_dir.mkdir()
    
    with zipfile.ZipFile(OUTPUT_DOCX, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
        
    # A. Actualizar header1.xml: cambiar expediente
    header1_path = temp_dir / "word" / "header1.xml"
    if header1_path.exists():
        h_text = header1_path.read_text(encoding="utf-8")
        h_text = h_text.replace("2685-2025", "2846-2026")
        header1_path.write_text(h_text, encoding="utf-8")
        
    # B. Escribir footnotes.xml con las 21 notas completas
    footnotes_path = temp_dir / "word" / "footnotes.xml"
    footnotes_path.write_text(build_footnotes_xml(), encoding="utf-8")
    
    # Re-empaquetar temporalmente para que docx.Document pueda manipular el document.xml
    with zipfile.ZipFile(OUTPUT_DOCX, 'w', zipfile.ZIP_DEFLATED) as zip_out:
        for root, dirs, files in os.walk(temp_dir):
            for file in files:
                p = Path(root) / file
                arcname = p.relative_to(temp_dir)
                zip_out.write(p, arcname)
                
    shutil.rmtree(temp_dir)
    print("Footnotes y Header actualizados en el paquete ZIP.")

def format_document_paragraphs():
    """Formatea document.xml para que coincida exactamente con la distribución del modelo 0146-2026."""
    doc = docx.Document(OUTPUT_DOCX)
    
    # Remover los metadatos P0..P4 (Elaborado por, etc.) para que la Página 1 empiece directamente con RESOLUCIÓN FINAL
    # como en modelo 0146-2026
    # Primero verifiquemos los primeros 5 párrafos:
    for i in range(4, -1, -1):
        p = doc.paragraphs[i]
        if any(k in p.text for k in ["Elaborado por", "Supervisado por", "Equipo:", "Vencimiento:"]) or p.text.strip() == "":
            p._p.getparent().remove(p._p)
            
    # Ahora el primer párrafo es RESOLUCIÓN FINAL
    p0 = doc.paragraphs[0]
    p0.text = "RESOLUCIÓN FINAL N° 0146-2026/CC1"
    p0.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.CENTER
    for r in p0.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(16)
        r.bold = True
        
    # Párrafo en blanco
    # doc.paragraphs[1] es blanco
    
    # Partes procesales
    # P2: DENUNCIANTE
    p_den = doc.paragraphs[2]
    p_den.text = "DENUNCIANTE\t:\tCÉSAR FERNANDO PONCE TIRADO (SEÑOR PONCE)\n\t\tALMA DELIA HERRERA GUERRERO (SEÑORA HERRERA)"
    p_den.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p_den.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        r.bold = False
        
    # P3: DENUNCIADO
    p_dendo = doc.paragraphs[3]
    p_dendo.text = "DENUNCIADO\t:\tPACÍFICO COMPAÑÍA DE SEGUROS Y REASEGUROS S.A. (PACÍFICO)"
    p_dendo.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p_dendo.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        
    # P4: MATERIA
    p_mat = doc.paragraphs[4]
    p_mat.text = "MATERIA\t:\tIMPROCEDENCIA DE LA DENUNCIA\n\t\tDECLINACIÓN DE COMPETENCIA"
    p_mat.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p_mat.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        
    # P5: ACTIVIDAD
    p_act = doc.paragraphs[5]
    p_act.text = "ACTIVIDAD\t:\tACTIVIDADES RELACIONADAS CON LA SALUD HUMANA"
    p_act.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p_act.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        
    # P7: Fecha
    p_fec = doc.paragraphs[7]
    p_fec.text = "Lima, 16 de enero de 2026"
    for r in p_fec.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        
    # P9: ANTECEDENTES
    p_ant = doc.paragraphs[9]
    p_ant.text = "ANTECEDENTES"
    for r in p_ant.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        r.bold = True
        
    # Helper to insert footnote reference run
    def create_fn_run(p, fid):
        r = p.add_run()
        rPr = r._r.get_or_add_rPr()
        rStyle = OxmlElement('w:rStyle')
        rStyle.set(qn('w:val'), 'FootnoteReference')
        rPr.append(rStyle)
        fnRef = OxmlElement('w:footnoteReference')
        fnRef.set(qn('w:id'), str(fid))
        r._r.append(fnRef)
        return r

    # P11: Párrafo 1 de Antecedentes con Nota 1
    p11 = doc.paragraphs[11]
    p11.text = ""
    r = p11.add_run("1.\tMediante escrito del 7 de agosto de 2026, subsanado mediante escrito del 29 de setiembre de 2026, el señor Ponce y la señora Herrera denunciaron a Pacífico, por presuntas infracciones a la Ley N° 29571, Código de Protección y Defensa del Consumidor")
    r.font.name = "Arial Narrow"
    r.font.size = docx.shared.Pt(11)
    create_fn_run(p11, 1)
    r2 = p11.add_run(" (en adelante, el Código), señalando lo siguiente:")
    r2.font.name = "Arial Narrow"
    r2.font.size = docx.shared.Pt(11)
    p11.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY

    # P13: Inciso (i)
    p13 = doc.paragraphs[13]
    p13.text = (
        "(i)\tSufrió un accidente de tránsito en el que estuvo involucrado el vehículo conducido "
        "por el señor Ponce, el cual contaba con el Seguro Obligatorio de Accidentes de Tránsito - Póliza N° 2012393904 "
        "emitido por Pacífico (en adelante, SOAT), en cuyo contexto solicitó la cobertura de gastos médicos derivados "
        "del siniestro, ante lo cual la compañía aseguradora emitió una Carta de Garantía por S/ 150,00 que al día siguiente fue denegada."
    )
    p13.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p13.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # P15: Inciso (ii)
    p15 = doc.paragraphs[15]
    p15.text = (
        "(ii)\tPosteriormente, presentó una solicitud ante Pacífico para el otorgamiento de la cobertura de gastos médicos. "
        "Mediante Carta N° GSIN-1315082/2026 de fecha 29 de mayo de 2026, dirigida a la señora Herrera, la compañía aseguradora "
        "denegó su solicitud al señalar que el vehículo menor superaba los 25 km/h del artículo 90° de la R.M. N° 308-2019-MTC/01 para VMP."
    )
    p15.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p15.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # P17: Párrafo 2 (Medida correctiva)
    p17 = doc.paragraphs[17]
    p17.text = (
        "2.\tEl señor Ponce y la señora Herrera solicitaron, en calidad de medida correctiva, que Pacífico cumpla con: "
        "(i) otorgar la cobertura integral de gastos médicos del SOAT; y, (ii) mantener activa la referida póliza. "
        "Asimismo, requirieron el reembolso de costos y costas del presente procedimiento."
    )
    p17.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p17.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # P19: Título ANÁLISIS
    p19 = doc.paragraphs[19]
    p19.text = "ANÁLISIS"
    p19.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p19.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        r.bold = True

    # P21: Subtítulo
    p21 = doc.paragraphs[21]
    p21.text = "Sobre la improcedencia de la denuncia interpuesta por el señor Ponce y la señora Herrera"
    p21.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p21.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)
        r.bold = True

    # P23: Párrafo 3 (empieza en pág 1 y termina en pág 2)
    # En el modelo 0146, P3 se divide en:
    # "3.\tEl artículo 105° del Código establece que el Indecopi es la autoridad con competencia primaria y de alcance nacional para conocer las presuntas infracciones a las disposiciones contenidas en el Código, así como para imponer las sanciones y medidas correctivas establecidas, conforme a la Ley de Organización y Funciones del Indecopi, aprobada por el Decreto Legislativo 1033. Asimismo, en la referida norma se señala que"
    # y continúa en la página 2 con:
    # "dicha competencia solo puede ser negada cuando ella haya sido asignada o se asigne a favor de otro organismo por norma expresa con rango de ley.[Nota 2]"
    p23 = doc.paragraphs[23]
    p23.text = (
        "3.\tEl artículo 105° del Código establece que el Indecopi es la autoridad con competencia "
        "primaria y de alcance nacional para conocer las presuntas infracciones a las disposiciones "
        "contenidas en el Código, así como para imponer las sanciones y medidas correctivas establecidas, "
        "conforme a la Ley de Organización y Funciones del Indecopi, aprobada por el Decreto Legislativo 1033. "
        "Asimismo, en la referida norma se señala que"
    )
    p23.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.JUSTIFY
    for r in p23.runs:
        r.font.name = "Arial Narrow"
        r.font.size = docx.shared.Pt(11)

    # Eliminar párrafos redundantes que quedaron de la plantilla original entre P24 y P30 si los hubiera
    # Guardar y retornar
    doc.save(OUTPUT_DOCX)
    print("Página 1 configurada exactamente según el modelo 0146-2026.")

if __name__ == "__main__":
    update_docx_package()
    format_document_paragraphs()
