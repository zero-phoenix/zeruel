# 1. Hechos

1 El mundo de Zeruel es la totalidad de los hechos registrados, no de las cosas.

1.1 **Expedientes en el corpus.** Viven en el apéndice acéfalo `zero-phoenix/zeruel-corpus`, fijado por `corpus.lock` (commit y SHA-256 por archivo) y verificado con `tools/corpus.py`. El cerebro no contiene datos de partes. Prueba: `corpus.lock`, `tools/corpus.py`.

1.2 **Evidencias de la matriz.** Cada fila de `docs/first-milestone.md` tiene estado **Real**, Simulada o Pendiente. Solo la evidencia observada en Render/Apps Script es Real; la de pruebas locales es Simulada. Prueba: `docs/first-milestone.md`, `docs/STATUS.md`.

1.3 **Estados de Render.** `zeruel/server.py` expone salud anónima y el estado de la sonda (`paused`, `synthetic_success`, `paused_quota`…), siempre con `cloud_gate_passed: false`. Prueba: `zeruel/server.py`, `zeruel/probe.py`.

1.4 **Estados de Apps Script.** `apps-script/SyntheticCheckpoint.gs` guarda `probe_<id>` y la lease global `zeruel_active`; estados `preparing`, `active`, `completed`, `paused_uncertain`, `paused_cooldown`, `terminal_unknown`. Prueba: `apps-script/SyntheticCheckpoint.gs`.

1.5 **Estados del cliente.** `web/app.js` (móvil) conserva el id pendiente del autorun y recupera el resultado sin reenviar. Prueba: `web/app.js`.

1.6 Lo que no consta en estas fuentes no es un hecho de Zeruel.
