#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Construye versiones corregidas de casos sobre plantillas maestras exactas.
Reutiliza primitivas puras desde tools/docx_utils.py.
"""

import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parent))
from docx_utils import clean_highlights_zip, replace_paragraph_text

if __name__ == "__main__":
    print("Funciones de reemplazo limpias listas (cargadas desde tools/docx_utils.py).")
