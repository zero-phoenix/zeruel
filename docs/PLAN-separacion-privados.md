# Plan de Separación de Fuentes Privadas y Archivo Documental

**Fecha:** 01/10/2026  
**Autor:** Zeruel / Supervisión (Claude)  
**Estado:** Propuesta técnica (SOLO PLAN — sin ejecución destructiva ni alteraciones de historial).

---

## 1. Justificación y Diagnóstico

El repositorio `zero-phoenix/zeruel` cumple actualmente una doble función que genera un conflicto arquitectónico:
1. **Servicio en la Nube (Render):** El servicio `zeruel-synthetic-probe` clona este repositorio en un contenedor Docker con recursos limitados (512 MB RAM, 0.1 CPU).
2. **Repositorio de Conocimiento y Archivo Privado:** Contiene fuentes documentales (`knowledge/private_sources`), índices con metadatos reales (`knowledge/private_index`) y borradores de trabajo (`knowledge/borrador_*.txt`).

Aunque el repositorio fue configurado como **privado**, clonar fuentes documentales binarias y datos no anonimizados en el entorno de despliegue de Render genera:
- Sobrecarga de transferencia y tiempo de compilación Docker en Render Free.
- Riesgo de exposición accidental de datos de expedientes o PII en logs, imágenes o capas de contenedores en la nube.
- Mezcla de preocupaciones entre la sonda de ejecución sintética y el archivo de entrenamiento jurídico/técnico.

---

## 2. Destino de los Datos Privados

Se propone desacoplar completamente el almacenamiento documental del código operativo:

1. **Repositorio Satélite de Archivo (Opción Principal):**
   - Crear un repositorio privado independiente: `zero-phoenix/zeruel-private-corpus` (o `zero-phoenix/zeruel-archive`).
   - Alojar exclusivamente:
     - `knowledge/private_sources/` (los 182 originales verificados).
     - `knowledge/private_index/` (índices detallados).
     - Borradores brutos con datos no anonimizados (`borrador_3017.txt`, `borrador_3057.txt`, etc.).
     - Registros de verificación criptográfica (`verification-local.json`, `verification-main-pr24.json`).
2. **Almacenamiento Local Aislado:**
   - En la máquina de trabajo, ubicar las fuentes en una ruta externa al árbol de trabajo de Render: `%USERPROFILE%\.zeruel-private\corpus\`.
   - El código en `zeruel` solo referenciará rutas locales absolutas o variables de entorno, sin incluir los archivos en el árbol git que se despliega.

---

## 3. Reglas de Exclusión en `.gitignore`

En el repositorio `zero-phoenix/zeruel` (el que Render clona), se añadirán reglas estrictas para impedir cualquier adición futura de documentos o fuentes:

```gitignore
# Archivo documental y fuentes privadas
knowledge/private_sources/
knowledge/private_index/
knowledge/borrador_*.txt
knowledge/*.docx
knowledge/*.xlsx
knowledge/*.pdf

# Archivos binarios de expedientes o modelos
*.docx
*.xlsx
*.pdf
*.csv
!tests/fixtures/*.json

# Exclusiones de seguridad de PII y secrets
~/.zeruel-private/
.env*
keys.env
```

---

## 4. Prueba Automatizada de Guarda (Failsafe Guard Test)

Para garantizar de forma determinista y popperiana que ningún binario ni archivo con datos reales se filtre al repositorio de Render, se implementará una prueba de regresión automática en la suite de pruebas (`tests/test_no_private_blobs.py`):

### Especificación de la Prueba:
1. **Inspección de Archivos Rastreados (`git ls-files`):**
   - La prueba interrogará el índice de Git en busca de extensiones prohibidas: `.docx`, `.xlsx`, `.pdf`.
   - Si se encuentra al menos un archivo con estas extensiones en el índice, la prueba fallará con código de salida 1 y mensaje explícito de violación.
2. **Inspección de Rutas Críticas:**
   - Verificará que las carpetas `knowledge/private_sources/` y `knowledge/private_index/` no existan en el árbol rastreado de `main`.
3. **Escaneo de Patrones de PII / Nombres de Partes:**
   - Un validador sintáctico escaneará los archivos de texto commiteados bajo `knowledge/` para asegurar que todo nombre personal esté anonimizado bajo marcadores (`PERSONA_X`, `EXPEDIENTE_X`) salvo los modelos públicos expresamente autorizados.
4. **Integración:**
   - La prueba correrá tanto en la suite local (`pytest` / `python -m unittest`) como en el paso de validación pre-despliegue en Docker.

---

## 5. Propuesta sobre el Historial de Git

Dado que `knowledge/private_sources` y los borradores ya se encuentran registrados en commits históricos de `main` (ej. PR #24 `9af5fb4` y commits precedentes), se analizan tres estrategias:

| Estrategia | Ventajas | Riesgos / Inconvenientes | Decisión |
|---|---|---|---|
| **A. Corte limpio hacia adelante (Soft Cut)** | Cero disrupción. No altera hashes de commits históricos (PRs #1 a #26 intactos). Render sigue desplegando sin cambios. | El historial antiguo aún contiene los blobs en el histórico git (aunque el repo sea privado). | **Recomendada para fase inmediata.** |
| **B. Reescritura completa con `git-filter-repo` / BFG** | Purgado absoluto de blobs del árbol histórico; reduce el peso del repo al clonar en Render. | Altera todos los SHAs pasados; requiere `git push --force`; invalida enlaces de PRs pasados; requiere re-vincular Render y re-clonar en todas las PCs. | **Solo aplicable si David autoriza ventana de mantenimiento explícita.** |
| **C. Bifurcación en Repositorio Nuevo para la Sonda (`zeruel-probe`)** | Mantiene `zero-phoenix/zeruel` como el corpus completo e histórico, y crea un repo limpio y ultraligero (`zero-phoenix/zeruel-probe`) exclusivamente para Docker/Render. | Requiere conectar el nuevo repo en el panel de Render. | **Alternativa limpia y sin riesgo de reescritura.** |

### Propuesta Concreta:
1. **Fase 1 (Inmediata y Segura):** Implementar la Opción A. Mover los archivos a su nuevo destino fuera del repo, aplicar `git rm -r --cached` sobre `knowledge/private_sources`, `knowledge/private_index` y `knowledge/borrador_*.txt`, actualizar `.gitignore` y activar la prueba de guarda en `tests/`.
2. **Fase 2 (Diferida):** Cuando David lo decida (o al configurar la nueva máquina), evaluar la migración del servicio de Render al repo satélite limpio o la ejecución coordinada de `git-filter-repo`.

---

## 6. Próximos Pasos (Condicionados a Autorización de David)

1. Revisar este plan con la supervisión de Claude y David.
2. No ejecutar ningún borrado ni alteración hasta que David apruebe expresamente la estrategia elegida (A, B o C).
3. Mantener el PR abierto para auditoría.
