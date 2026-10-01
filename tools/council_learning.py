#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Ejecuta en paralelo el análisis de DeepSeek y GLM-5.3 sobre las diferencias de los 8 casos de aprendizaje."""

import os
import sys
import json
import concurrent.futures
from pathlib import Path

sys.path.append(str(Path(__file__).parent))
import council

def run_analysis():
    diff_file = Path("knowledge/diff_summary.md")
    diff_text = diff_file.read_text(encoding="utf-8")

    prompt_ds = (
        "Como DeepSeek V4.1 Flash (Max), subagente analítico y falsacionista del Consejo de Zeruel:\n"
        "Analiza las diferencias entre los 8 borradores de admisorios del usuario y las versiones corregidas por su jefa (LSQ).\n\n"
        f"RESUMEN DE DIFERENCIAS:\n{diff_text}\n\n"
        "Tu tarea:\n"
        "1. Identifica qué vulnerabilidades procesales y 'puntos ciegos' eliminó la jefa en cada caso (ej. imputación genérica vs circunstanciada en reclamos Art. 88.1, tipificación de deber de información Art. 2, delimitación de falta vs negativa de cobertura, erratas graves de número de expediente heredadas de plantillas).\n"
        "2. Detecta riesgos procesales fatales si el borrador se hubiera notificado tal como estaba (ej. defensas de la aseguradora por incongruencia fáctica, afectación al derecho de defensa, nulidades según TUO Ley 27444).\n"
        "3. Sintetiza tus lecciones aprendidas desde la óptica del falsacionismo popperiano y el blindaje probatorio del acto administrativo.\n"
        "Sé incisivo, técnico, estructurado y exhaustivo."
    )

    prompt_glm = (
        "Como GLM-5.3 (Max), subagente de diseño estructural, semántica y tipificación del Consejo de Zeruel:\n"
        "Analiza las diferencias entre los 8 borradores de admisorios del usuario y las versiones corregidas por su jefa (LSQ).\n\n"
        f"RESUMEN DE DIFERENCIAS:\n{diff_text}\n\n"
        "Tu tarea:\n"
        "1. Analiza el patrón estructural y de lenguaje administrativo que impone la jefa (terminología exacta del Código de Consumo como 'de manera veraz y suficiente', conectores de contraste como 'sin embargo' en vez de reiterar 'posteriormente', puntuación de incisos y comas incidentales).\n"
        "2. Modela las reglas heurísticas de tipificación e imputación (desglose de hechos denunciados, especificación del contenido de la infracción al Art. 88.1, requerimientos de información dirigidos a la aseguradora con el estándar de la CC1).\n"
        "3. Formula la arquitectura de corrección y las invariantes de datos que Zeruel debe aplicar de forma sistemática.\n"
        "Sé técnico, estructurado y propositivo."
    )

    print("Iniciando llamadas concurrentes a DeepSeek y GLM-5.3...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        f_ds = executor.submit(council.call_api, 
                               "https://api.deepseek.com/chat/completions", 
                               council.load_keys()["DEEPSEEK_API_KEY"], 
                               "deepseek-chat", 
                               [
                                   {"role": "system", "content": "Eres DeepSeek V4.1 Flash (Max), subagente analítico y dialéctico de Zeruel."},
                                   {"role": "user", "content": prompt_ds}
                               ], 
                               max_tokens=3000)
        
        or_key = council.load_keys().get("OPENROUTER_API_KEY", "")
        f_glm = executor.submit(council.call_api,
                                "https://openrouter.ai/api/v1/chat/completions",
                                or_key,
                                "z-ai/glm-5.3",
                                [
                                    {"role": "system", "content": "Eres GLM-5.3 (Max), subagente de diseño estructural y semántica de Zeruel."},
                                    {"role": "user", "content": prompt_glm}
                                ],
                                max_tokens=3000)

        res_ds = f_ds.result()
        res_glm = f_glm.result()

    out_ds = Path("knowledge/aprendizaje_deepseek.md")
    out_glm = Path("knowledge/aprendizaje_glm53.md")

    ds_content = res_ds.get("content", f"[Error: {res_ds.get('error')}]")
    glm_content = res_glm.get("content", f"[Error: {res_glm.get('error')}]")

    out_ds.write_text(ds_content, encoding="utf-8")
    out_glm.write_text(glm_content, encoding="utf-8")

    print(f"DeepSeek finalizado. Guardado en {out_ds}")
    print(f"GLM-5.3 finalizado. Guardado en {out_glm}")

if __name__ == "__main__":
    run_analysis()
