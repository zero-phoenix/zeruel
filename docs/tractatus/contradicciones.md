# Contradicciones (auditoría popperiana, 02/10/2026)

Método: grep de valores y prohibiciones en `AGENTS.md`, `docs/HANDOFF.md`, `docs/first-milestone.md`, `docs/STATUS.md`, `docs/tractatus/3-proposiciones.md` y el código; cada choque se resuelve con evidencia y, si es comprobable, con una prueba que falla con la versión contradictoria (mutación ejecutada).

## C1. «Sin keepalive» frente a pings programados — RESUELTA
- Lado A: `docs/HANDOFF.md:50` «Render Free se suspende y pierde archivos: sin keepalive artificial.» (absoluta).
- Lado B: `docs/PROMPT-continuacion-celular.md:135` ordena un proceso que llama a `/healthz` cada 10 min hasta T1+70 min.
- Evidencia: `docs/PROMPT-continuacion-claude-opus55-low.md:25,90` lo define como «excepción temporal autorizada, nunca un keepalive permanente», limitada a la prueba de renovación. El código no hace pings: `web/app.js` solo sondea `/api` mientras `state=active`; `render.yaml:7` es el health check de la plataforma.
- Regla única: sin keepalive artificial; única excepción, el helper temporal de la Fase D, terminado al acabar.
- Corrección: `docs/HANDOFF.md:50` y `docs/PROMPT-continuacion-celular.md:135` enuncian la excepción.
- Prueba: `tests/test_contradicciones.py::test_c1_pings_only_as_temporary_exception`. Mutación (quitar «excepción temporal» de HANDOFF) → falla.

## C2. D1 «sin prueba» frente a pruebas existentes — RESUELTA
- Lado A: `docs/tractatus/3-proposiciones.md:61` (D1) decía que `cloud_gate_passed=false` no tenía prueba.
- Lado B: `tests/test_http.py:38`, `tests/test_probe.py:67`, `tests/test_recovery.py:45` ya lo afirman en rutas concretas; `zeruel/server.py:23-99` y `zeruel/probe.py:158` lo fijan.
- Regla única: `AGENTS.md:11`, `docs/first-milestone.md:40`: siempre `false` en este hito.
- Corrección: D1 pasa a proposición 3.47 con prueba estructural; conteo 36 con prueba / 5 deuda.
- Prueba: `test_c2_cloud_gate_never_true_in_source`. Mutación (`True` en `zeruel/server.py`) → falla.

## Comprobadas sin contradicción
- Renovación «unos 54 min»: `zeruel/checkpoint.py:65` renueva con margen de 360 s sobre `expires_in` (3600 s) = 54 min. Coherente con HANDOFF y prompts.
- Pendientes de matriz (renovación, móvil con ambos Windows apagados, cuota, suscripción): idénticos en `first-milestone.md:25-37`, `STATUS.md:11` y `HANDOFF.md:11`.
- Fusión de PR: HANDOFF:3 (solo #24 autorizado) es coherente con `AGENTS.md:11`.

## Pendientes
- Ninguna contradicción abierta. Deuda de falsación abierta: D4–D6 (D2–D3 pagadas con evidencia Real).

## Revisión del consejo DeepSeek + GLM (02/10/2026) — corregida
- Nombres cruzados: C1 (keepalive) ↔ `test_c1_pings_only_as_temporary_exception`; C2 (`cloud_gate_passed`) ↔ `test_c2_cloud_gate_never_true_in_source`.
- La prueba C1 ahora exige «excepción temporal» en la misma línea de HANDOFF que prohíbe el keepalive, recorre todo `docs/` (salvo este archivo histórico) y busca **llamadas** a `/healthz` (no la definición de la ruta) en `.py/.js/.gs/.ps1/.sh` de `zeruel/`, `web/`, `apps-script/`, `tools/` y `scripts/`.
- Mutaciones ejecutadas (cada una hace fallar exactamente una prueba): M1 quitar la excepción de `HANDOFF.md:50`; M2 añadir un `urlopen(".../healthz")` en `zeruel/`; M3 poner `"cloud_gate_passed": True` en `zeruel/server.py`.

## Recuento ejecutable (03/10/2026)
- **56** proposiciones 3.x, todas con falsador y pruebas existentes; **0** pruebas huérfanas (`tools/tractatus.py`, `test_tractatus.py`).
- **11/11** mutantes eliminados (`tools/mutate.py`); el de 3.11 sobrevivía y reveló una prueba tautológica, corregida.
- Corpus: `verify` refuta byte alterado, archivo sobrante, recuento falso y HEAD movido; 195/195 íntegros en `dbb4d1c`.
- Todo corre en `.github/workflows/ci.yml` (hoy bloqueado por facturación de GitHub; se ejecuta en local).
