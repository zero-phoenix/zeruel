#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Genera las 3 resoluciones corregidas definitivas de C:\Users\D\Desktop\Nuevas correcciones
aplicando el estándar superior Zeruel:
1. Basado en plantilla/borrador sin alterar maquetación ni fuentes XML.
2. Corrección fáctica e imputativa absoluta.
3. Eliminación total de marcas w:highlight.
4. Espejo exacto considerando <-> resuelve.
"""

import os
import re
import shutil
import zipfile
from xml.etree import ElementTree as ET

W = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'

def strip_all_highlights_and_clean(docx_path):
    """Limpia todo rastro de resaltado en el docx."""
    temp_zip = docx_path + ".clean.zip"
    with zipfile.ZipFile(docx_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename.endswith('.xml'):
                    text = data.decode('utf-8', 'replace')
                    # Quitar highlight
                    text = re.sub(r'<w:highlight\b[^>]*/>', '', text)
                    text = re.sub(r'<w:highlight\b[^>]*>.*?</w:highlight>', '', text)
                    zout.writestr(item, text.encode('utf-8'))
                else:
                    zout.writestr(item, data)
    os.replace(temp_zip, docx_path)

def build_case_3017():
    print("Construyendo corrección superior para CASO 3017-2026...")
    folder = r"C:\Users\D\Desktop\Nuevas correcciones\3017-2026"
    borrador_path = os.path.join(folder, "ADM 3017-2026 R2 borrador.docx")
    out_path = os.path.join(folder, "ADM 3017-2026 R2.docx")
    out_corregido = os.path.join(folder, "ADM 3017-2026 R2 corregido.docx")
    
    # Copiar borrador base como punto de partida que ya tiene los estilos y márgenes del caso
    shutil.copy2(borrador_path, out_path)
    
    # Abrir document.xml y hacer los reemplazos quirúrgicos precisos
    temp_zip = out_path + ".tmp.zip"
    with zipfile.ZipFile(out_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'word/document.xml':
                    text = data.decode('utf-8', 'replace')
                    
                    # 1. Corregir fecha al estándar con punto
                    text = text.replace("Lima, 25 de setiembre de 2026", "Lima, 25 de setiembre de 2026.")
                    
                    # 2. Corregir el petitorio de medidas correctivas del hecho (eliminar la mezcla de hipotecario/desgravamen)
                    old_petitorio = (
                        "La señora Martínez solicitó, en calidad de medida correctiva, que Pacífico cumpla con: "
                        "(i) otorgar la devolución del monto pagado en exceso por las primas del Seguro de vida, "
                        "excluyendo el costo correspondiente al Seguro de desgravamen efectivamente exigido por el crédito hipotecario; "
                        "(ii) realizar la anulación inmediata del Seguro de vida contratado sin penalidad alguna, "
                        "garantizando que no se afecte el endoso de su crédito hipotecario; "
                        "(iii) realizar las coordinaciones para garantizar que la anulación del Seguro de vida no afecte "
                        "la cobertura del Seguro de desgravamen de su crédito hipotecario; y, "
                        "(iv) adoptar las medidas necesarias para evitar que continúe ofreciendo inadecuadamente beneficios a futuros consumidores, "
                        "en virtud de los hechos materia de denuncia. Asimismo, no solicitó el pago de costas y costos del procedimiento."
                    )
                    new_petitorio = (
                        "La señora Martínez solicitó, en calidad de medida correctiva, que Pacífico cumpla con: "
                        "(i) otorgar la devolución del monto pagado en exceso por las primas del Seguro de Vida; "
                        "(ii) realizar la anulación y liquidación del Seguro de Vida contratado sin penalidad o cargos indebidos; y, "
                        "(iii) entregar copia íntegra del registro o grabación de la llamada de comercialización. "
                        "Asimismo, solicitó el pago de costas y costos del procedimiento."
                    )
                    # Reemplazo tolerante
                    if "excluyendo el costo correspondiente al Seguro de desgravamen efectivamente exigido por el crédito hipotecario" in text:
                        text = re.sub(r"La señora Martínez solicitó, en calidad de medida correctiva, que Pacífico cumpla con:.*?Asimismo, no solicitó el pago de costas y costos del procedimiento\.", new_petitorio, text, flags=re.S)
                    
                    # 3. Reemplazar la imputación residual de "remolque vehicular" y "transferencia a Rímac" en CONSIDERANDOS
                    # Cargo 1 en Considerando: Información
                    cargo1_cons = (
                        "La Secretaría Técnica de la Comisión de Protección al Consumidor 1 (en adelante, la Secretaría Técnica), "
                        "en ejercicio de sus facultades, considera que el hecho denunciado, consistente en que la compañía aseguradora "
                        "no habría cumplido con informar a la denunciante de manera veraz y suficiente durante la comercialización telefónica "
                        "del Seguro de Vida – Póliza 170469038, respecto a la naturaleza del producto, los costos, gastos y deducciones aplicables "
                        "al seguro, y la forma en que estos afectarían el saldo acumulado de la cuenta y el eventual valor de rescate; "
                        "involucraría una presunta afectación al derecho de información de los consumidores. Por consiguiente, corresponde "
                        "calificar el hecho materia de denuncia como una presunta infracción al artículo 1, numeral 1, literal b) y al artículo 2 del Código."
                    )
                    
                    # Cargo 2 en Considerando: Reclamo Art. 88.1
                    cargo2_cons = (
                        "Asimismo, la Secretaría Técnica, en ejercicio de sus facultades, considera que el hecho denunciado, "
                        "consistente en que la compañía aseguradora habría brindado una respuesta inadecuada al reclamo presentado por "
                        "la denunciante, mediante comunicación del 24 de junio de 2026, en tanto omitió pronunciarse de manera específica "
                        "sobre la entrega del registro o grabación de la llamada telefónica en la cual se efectuó la comercialización y "
                        "contratación de la Póliza 170469038 del Seguro de Vida; involucraría una presunta afectación a su derecho de "
                        "recibir respuestas adecuadas a los reclamos formulados. Por consiguiente, corresponde calificar el hecho materia "
                        "de denuncia como una presunta infracción al numeral 88.1 del artículo 88 del Código."
                    )
                    
                    # Encontrar y reemplazar el bloque considerativo de remolque y transferencia a Rímac
                    pat_cons = r"La Secretaría Técnica de la Comisión de Protección al Consumidor 1.*?beneficio de servicio de remolque vehicular.*?En tanto la denuncia reúne los requisitos"
                    nuevo_bloque_cons = cargo1_cons + "</w:t></w:r></w:p><w:p><w:r><w:t>" + cargo2_cons + "</w:t></w:r></w:p><w:p><w:r><w:t>En tanto la denuncia reúne los requisitos"
                    text = re.sub(pat_cons, nuevo_bloque_cons, text, flags=re.S)
                    
                    # 4. Reemplazar la imputación de remolque vehicular en PRIMERO del RESUELVE
                    cargo1_res = (
                        "Presunta infracción al artículo 1, numeral 1, literal b) y al artículo 2 de la Ley 29571, Código de Protección "
                        "y Defensa del Consumidor, en tanto la compañía aseguradora no habría cumplido con informar adecuadamente a la denunciante, "
                        "de manera veraz y suficiente, durante la comercialización telefónica de la Póliza 170469038 del Seguro de Vida, "
                        "la naturaleza del producto, los costos, gastos y deducciones asociadas y la forma en que estos afectarían el saldo "
                        "acumulado y el eventual valor de rescate del referido seguro."
                    )
                    cargo2_res = (
                        "Presunta infracción al numeral 88.1 del artículo 88 de la Ley 29571, Código de Protección y Defensa del Consumidor, "
                        "en tanto la compañía aseguradora habría brindado una respuesta inadecuada al reclamo presentado por la denunciante, "
                        "mediante comunicación del 24 de junio de 2026, en tanto omitió pronunciarse sobre la entrega del registro o grabación "
                        "de la llamada telefónica en la cual se efectuó la comercialización y contratación de la Póliza 170469038 del Seguro de Vida."
                    )
                    
                    pat_res = r"Presunta infracción a los artículos 18 y 19 de la Ley 29571.*?remolque vehicular.*?del referido seguro\."
                    nuevo_bloque_res = cargo1_res + "</w:t></w:r></w:p><w:p><w:r><w:t>" + cargo2_res
                    text = re.sub(pat_res, nuevo_bloque_res, text, flags=re.S)
                    
                    # 5. Requerimiento QUINTO (espejo y precisión de grabación)
                    req_quinto = (
                        "(i) presentar una copia completa, legible y debidamente suscrita de la Póliza 170469038 del Seguro de Vida, "
                        "así como sus condiciones generales, particulares y el cargo de remisión de la misma; "
                        "(ii) presentar los medios probatorios que acrediten la información efectivamente brindada durante la comercialización "
                        "telefónica de la Póliza 170469038 del Seguro de Vida, incluyendo el audio o grabación íntegra de la llamada telefónica "
                        "en virtud de la cual se contrató el seguro; y, "
                        "(iii) presentar copia del reclamo interpuesto por la denunciante y la constancia de notificación de la respuesta brindada "
                        "el 24 de junio de 2026."
                    )
                    text = re.sub(r"\(i\) presentar una copia completa, legible y debidamente suscrita de la Póliza 170469038.*?en virtud de los hechos materia de denuncia\.", req_quinto, text, flags=re.S)
                    
                    zout.writestr(item, text.encode('utf-8'))
                else:
                    zout.writestr(item, data)
    os.replace(temp_zip, out_path)
    strip_all_highlights_and_clean(out_path)
    shutil.copy2(out_path, out_corregido)
    print(f"Caso 3017 generado en: {out_path} y {out_corregido}")

def build_case_3057():
    print("Construyendo corrección superior para CASO 3057-2026...")
    folder = r"C:\Users\D\Desktop\Nuevas correcciones\3057-2026"
    borrador_path = os.path.join(folder, "ADM 3057-2026 R2 borrador.docx")
    out_path = os.path.join(folder, "ADM 3057-2026 R2.docx")
    out_corregido = os.path.join(folder, "ADM 3057-2026 R2 corregido.docx")
    
    shutil.copy2(borrador_path, out_path)
    
    temp_zip = out_path + ".tmp.zip"
    with zipfile.ZipFile(out_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'word/document.xml':
                    text = data.decode('utf-8', 'replace')
                    
                    # 1. Fecha estándar con punto final
                    text = text.replace("Lima, 25 de setiembre de 2026", "Lima, 25 de setiembre de 2026.")
                    
                    # 2. Corregir "habría denegado de manera injustificada" -> "habría denegado indebidamente" y precisar hecho
                    # Conectar con la regla aprendida de LSQ:
                    old_imp = "habría denegado de manera injustificada a la denunciante la cobertura del Seguro de Desgravamen - Póliza 1016201425800 ante el fallecimiento de su cónyuge Juan Pablo Bustamante Talavera, invocando una preexistencia médica al haber modificado presuntamente la fecha de inicio de vigencia del referido seguro"
                    new_imp = "habría denegado indebidamente a la denunciante la cobertura por fallecimiento del Seguro de Desgravamen – Póliza 1016201425800 ante el deceso de su cónyuge Juan Pablo Bustamante Talavera, invocando una presunta preexistencia médica al haber computado como fecha de inicio de vigencia de la póliza el 1 de diciembre de 2020 en lugar de la fecha de suscripción del 23 de setiembre de 2020"
                    text = text.replace(old_imp, new_imp)
                    
                    # 3. Saneamiento del requerimiento probatorio QUINTO: alinear "falta de otorgamiento de cobertura"
                    text = text.replace("la denegatoria de cobertura se encuentra contractualmente justificada", "la falta de otorgamiento de cobertura se encuentra contractualmente justificada")
                    
                    zout.writestr(item, text.encode('utf-8'))
                else:
                    zout.writestr(item, data)
    os.replace(temp_zip, out_path)
    strip_all_highlights_and_clean(out_path)
    shutil.copy2(out_path, out_corregido)
    print(f"Caso 3057 generado en: {out_path} y {out_corregido}")

def build_case_3075():
    print("Construyendo corrección superior para CASO 3075-2026...")
    folder = r"C:\Users\D\Desktop\Nuevas correcciones\3075-2026"
    borrador_path = os.path.join(folder, "ADM 3075-2026 R2 borrador.docx")
    out_path = os.path.join(folder, "ADM 3075-2026 R2.docx")
    out_corregido = os.path.join(folder, "ADM 3075-2026 R2 corregido.docx")
    
    shutil.copy2(borrador_path, out_path)
    
    temp_zip = out_path + ".tmp.zip"
    with zipfile.ZipFile(out_path, 'r') as zin:
        with zipfile.ZipFile(temp_zip, 'w', compression=zipfile.ZIP_DEFLATED) as zout:
            for item in zin.infolist():
                data = zin.read(item.filename)
                if item.filename == 'word/document.xml':
                    text = data.decode('utf-8', 'replace')
                    
                    # 1. Fecha estándar con punto final
                    text = text.replace("Lima, 25 de setiembre de 2026", "Lima, 25 de setiembre de 2026.")
                    
                    # 2. Hechos: pulir redacción y medidas correctivas
                    text = text.replace("El 25 de setiembre de 2025, presentó una solicitud indemnizatoria ante la EPS, a fin de que esta tramite la atención del siniestro ante la compañía aseguradora.", 
                                        "El 25 de setiembre de 2025, presentó una solicitud de indemnización y cobertura del siniestro ante la EPS, a fin de que esta tramite la atención correspondiente ante la compañía aseguradora.")
                    text = text.replace("No obstante, la compañía aseguradora se habría negado de manera injustificada a indemnizar los referidos daños y el lucro cesante.",
                                        "Sin embargo, la compañía aseguradora habría denegado la atención y cobertura solicitada.")
                    
                    text = text.replace("El señor Escate solicitó, en calidad de medida correctiva, el pago de S/ 43 597,00, S/ 78 000,00 y S/ 16 500,00. Asimismo, solicitó el pago de costas y costos del procedimiento.",
                                        "El señor Escate solicitó, en calidad de medida correctiva, la cobertura e indemnización de los daños materiales derivados del siniestro amparados en la póliza. Asimismo, solicitó el pago de costas y costos del procedimiento.")

                    # 3. ELIMINACIÓN DEL VICIOSO CARGO DE LUCRO CESANTE EN CONSIDERANDO Y SUSTITUCIÓN POR DESCARTE COMPETENCIAL
                    # Imputación precisa de daños materiales:
                    cargo_danos_cons = (
                        "La Secretaría Técnica de la Comisión de Protección al Consumidor 1 (en adelante, la Secretaría Técnica), "
                        "en ejercicio de sus facultades, considera que el hecho denunciado, consistente en que la compañía aseguradora "
                        "habría denegado indebidamente la cobertura del siniestro derivado de la ruptura de tubería de agua ocurrida el 30 de enero de 2025, "
                        "respecto a los daños materiales producidos en el inmueble y taller del denunciante amparados en el Contrato de Seguro 01-2025; "
                        "involucraría una presunta afectación a sus expectativas, quien no habría encontrado una correspondencia entre lo que esperaba "
                        "recibir de parte del proveedor y lo que realmente recibió. Por consiguiente, corresponde calificar el hecho materia de denuncia "
                        "como una presunta infracción al deber de idoneidad, tipificado en los artículos 18 y 19 del Código."
                    )
                    
                    descarte_lucro_cons = (
                        "De otro lado, respecto al extremo en el que el denunciante solicita la indemnización por lucro cesante y daños derivados, "
                        "corresponde precisar que de conformidad con los artículos 107 y 115 del Código, la Comisión no resulta competente para ordenar "
                        "el pago de indemnizaciones por daños y perjuicios o lucro cesante, correspondiendo dicho reclamo a la vía civil u ordinaria; "
                        "por lo que dicho extremo no forma parte de la presente imputación de cargos."
                    )
                    
                    pat_cons_3075 = r"La Secretaría Técnica de la Comisión de Protección al Consumidor 1.*?consistente en que la compañía aseguradora se habría negado de manera injustificada a indemnizar el lucro cesante derivado de la ruptura de una tubería.*?En tanto la denuncia reúne los requisitos"
                    nuevo_bloque_cons_3075 = cargo_danos_cons + "</w:t></w:r></w:p><w:p><w:r><w:t>" + descarte_lucro_cons + "</w:t></w:r></w:p><w:p><w:r><w:t>En tanto la denuncia reúne los requisitos"
                    text = re.sub(pat_cons_3075, nuevo_bloque_cons_3075, text, flags=re.S)
                    
                    # 4. En el RESUELVE PRIMERO: suprimir el cargo de lucro cesante y dejar únicamente la infracción a idoneidad por daños materiales
                    cargo_danos_res = (
                        "Presunta infracción a los artículos 18 y 19 de la Ley 29571, Código de Protección y Defensa del Consumidor, "
                        "en tanto la compañía aseguradora habría denegado indebidamente la cobertura del siniestro derivado de la ruptura "
                        "de tubería de agua ocurrida el 30 de enero de 2025, respecto a los daños materiales producidos en el inmueble y taller "
                        "del denunciante amparados en el Contrato de Seguro 01-2025."
                    )
                    pat_res_3075 = r"Presunta infracción a los artículos 18 y 19 de la Ley 29571.*?ruptura de una tubería\.\s*Presunta infracción a los artículos 18 y 19 de la Ley 29571.*?lucro cesante derivado de la ruptura de una tubería\."
                    text = re.sub(pat_res_3075, cargo_danos_res, text, flags=re.S)
                    
                    # 5. En el REQUERIMIENTO QUINTO: precisar y enriquecer la prueba de oficio
                    req_5_3075 = (
                        "(i) presentar copia completa y legible del Contrato de Seguro 01-2025 emitido a favor de la EPS Tacna, incluyendo "
                        "sus condiciones generales, particulares y cláusulas de cobertura; (ii) presentar los medios probatorios que sustenten "
                        "la atención y evaluación brindada al siniestro reportado por el denunciante, incluyendo informes de inspección y liquidación; y, "
                        "(iii) presentar copia de las comunicaciones cursadas con la EPS y con el denunciante respecto a la procedencia o rechazo de la cobertura."
                    )
                    text = re.sub(r"\(i\) presentar copia completa y legible de la póliza contratada; y, \(ii\) presentar los medios probatorios que sustenten la atención brindada al siniestro\.", req_5_3075, text, flags=re.S)
                    
                    zout.writestr(item, text.encode('utf-8'))
                else:
                    zout.writestr(item, data)
    os.replace(temp_zip, out_path)
    strip_all_highlights_and_clean(out_path)
    shutil.copy2(out_path, out_corregido)
    print(f"Caso 3075 generado en: {out_path} y {out_corregido}")

if __name__ == '__main__':
    build_case_3017()
    build_case_3057()
    build_case_3075()
    print("\n¡Los 3 casos fueron procesados y generados con éxito!")
