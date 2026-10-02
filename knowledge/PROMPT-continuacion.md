# Prompt de Continuación (Perfil: Base)

> **AVISO DE ARQUITECTURA (Patrón Core + Profiles):**  
> Este documento ha sido factorizado y consolidado bajo el estándar canónico **Core + Profiles**.
> La fuente única de verdad, memoria de aprendizaje, directrices epistemológicas e invariantes universales residen en el Core:
> 👉 [`knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md`](PROMPT-CONTINUIDAD-APRENDIZAJE.md).

## Perfil de Continuación General

1. **Núcleo Canónico:** Lee y aplica estrictamente `knowledge/PROMPT-CONTINUIDAD-APRENDIZAJE.md`.
2. **Gobernanza del Corpus Acéfalo:** Todo hecho, expediente o fuente documental reside en `zero-phoenix/zeruel-corpus`, gobernado criptográficamente por `corpus.lock` y gestionado mediante `python tools/corpus.py sync|verify|pin`.
3. **Orquestación Concurrente:** Para subagentes y ejecuciones en paralelo, consulta `knowledge/PROMPT-PARALELO.md`.
4. **Perfiles de Entorno Especializados:**
   - Para interacción móvil vía USB/ADB: [`docs/PROMPT-continuacion-celular.md`](../docs/PROMPT-continuacion-celular.md).
   - Para entornos con restricciones de cómputo (Claude Low-Resource / Celeron): [`docs/PROMPT-continuacion-claude-opus55-low.md`](../docs/PROMPT-continuacion-claude-opus55-low.md).
