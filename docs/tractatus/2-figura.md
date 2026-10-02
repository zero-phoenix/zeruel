# 2. Figura

2 La figura es el esquema que comparten el hecho y su registro.

2.1 **Registro del checkpoint** (`probe_<id>` en Apps Script; campos públicos):

```
{ id: <hex32>, state: preparing|active|completed|paused_uncertain|terminal_unknown,
  generation: <entero>, expires: <epoch s>, completed: <epoch s>?,
  result: { state: synthetic_success|paused_quota|..., ... }?, cloud_gate_passed: false }
```
Lease global: `zeruel_active = { id, generation, expires }`. Cooldown: `zeruel_last_run` (30 s).

2.2 **Caso de la sonda** (`zeruel/probe.py`): prompt fijo, sin herramientas, salida esperada exacta

```
{"marker":"ZERUEL_OK","sum":42}
```
Informe: `{ state, synthetic_only: true, subscription_verified: false, cloud_gate_passed: false, ... }`.

2.3 **`corpus.lock`**:

```
{ version: 1, repo: "zero-phoenix/zeruel-corpus", commit: <sha1>,
  file_count: <n>, files: { "<ruta>": "<sha256>" } }
```

2.4 Un registro que no encaja en estas figuras se rechaza (ver 3.2 y 3.4).
