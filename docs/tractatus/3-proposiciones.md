# 3. Proposiciones

3 Cada proposición indica su **falsador** (el hecho que la refutaría) y la **prueba** exacta en `tests/` que lo intenta. Las que no tienen prueba están en la Deuda de falsación.

## 3.1 Sonda sintética (`zeruel/probe.py`)

- **3.11** La sonda solo acepta `{"marker":"ZERUEL_OK","sum":42}`. Falsador: una salida distinta o no estructurada se acepta. Pruebas: `test_incorrect_or_unstructured_output_rejected`, `test_contract_is_literal_zeruel_ok_42`.
- **3.12** El comando es fijo, aislado y ligado a esquema. Falsador: el comando admite prompt o herramientas arbitrarias. Prueba: `test_command_is_fixed_sandboxed_and_schema_bound`.
- **3.13** Cuota agotada pausa sin filtrar errores. Falsador: un 429 provoca reintento o expone detalle. Prueba: `test_quota_is_paused_and_errors_do_not_leak`.
- **3.14** Ninguna ruta de autenticación facturable. Falsador: una ruta de pago llega al CLI. Prueba: `test_all_paid_auth_routes_blocked`.
- **3.15** El timeout no reintenta. Falsador: segunda invocación tras timeout. Prueba: `test_timeout_does_not_retry`.
- **3.16** El proceso hijo no hereda secretos. Falsador: una clave aparece en el entorno del CLI. Prueba: `test_child_environment_strips_secrets`.
- **3.17** Acciones de herramienta denegadas cierran en falso. Falsador: una acción denegada produce éxito. Prueba: `test_denied_tool_actions_fail_closed`.

## 3.2 Checkpoint (`apps-script/SyntheticCheckpoint.gs`, `zeruel/checkpoint.py`)

- **3.21** Firma inválida no muta el almacenamiento. Falsador: escritura con firma falsa. Prueba: `invalid signature cannot mutate storage`.
- **3.22** La repetición se rechaza. Falsador: la misma petición aceptada dos veces. Prueba: `replay is rejected`.
- **3.23** Una sola ejecución global. Falsador: dos trabajadores con ids distintos obtienen lease. Prueba: `global lease blocks simultaneous workers even with different IDs`.
- **3.24** Lo completado no se ejecuta otra vez, ni tras reinicio. Falsador: un id completado vuelve a inferir. Pruebas: `completed checkpoint survives fresh runtime and cannot execute twice`, `test_completed_checkpoint_does_not_run_again`.
- **3.25** La lease vence exactamente en su plazo. Falsador: completar o readquirir tras `expires`. Prueba: `lease expires exactly at deadline and cannot be reacquired or completed`.
- **3.26** Un trabajador antiguo no completa. Falsador: una generación anterior cierra la operación. Prueba: `stale worker cannot complete its closed ID or a newer lease`.
- **3.27** Un estado de resultado inesperado no se persiste. Falsador: se guarda un estado fuera de la figura 2.1. Prueba: `unexpected result state cannot be persisted`.
- **3.28** Solo la identidad Google del propietario escribe; sin configuración, cierre. Falsador: otra cuenta o ninguna escribe. Pruebas: `other Google identity and missing identity cannot write`, `missing owner configuration fails closed`, `public web entry rejects even a valid signature`.
- **3.29** Una escritura fallida conserva la incertidumbre. Falsador: tras el fallo se autoriza nueva inferencia. Pruebas: `failed completion write keeps original active record for persistence retry`, `second claim write failure never authorizes and owner recovery unblocks`.

## 3.3 Recuperación (`zeruel/checkpoint.py`, `tools/`)

- **3.31** La recuperación nunca llama al modelo. Falsador: invocación del CLI durante la recuperación. Prueba: `test_recovery_never_invokes_model`.
- **3.32** Sin informe durable no hay éxito: `terminal_unknown`. Falsador: recuperación sin informe marca éxito. Pruebas: `recovery without report is a terminal unknown tombstone, never success`, `test_missing_report_requires_explicit_unknown_and_never_success`.
- **3.33** La recuperación exige confirmación del propietario y generación exacta. Falsador: recuperación sin confirmación. Prueba: `recovery needs explicit owner confirmation and exact generation`.
- **3.34** No se recupera una lease aún viva. Falsador: recuperación con lease vigente. Prueba: `recovery refused while the original lease can still act`.
- **3.35** Diario corrupto o generación ausente cierran en falso. Falsador: ejecución con diario corrupto. Pruebas: `test_corrupt_journal_fails_closed`, `test_missing_generation_fails_closed`.
- **3.36** El servidor nunca llama a la recuperación. Falsador: una ruta HTTP que recupera. Prueba: `test_server_never_calls_recovery`.
- **3.37** Respuesta perdida: el reintento idéntico es idempotente; uno diferente se rechaza. Falsador: un segundo resultado distinto aceptado. Pruebas: `lost HTTP response after a stored completion is recovered by identical retry`, `completion retry is idempotent after partial deletion; conflicting or stale token rejected`.

## 3.4 Servidor HTTP (`zeruel/server.py`, `zeruel/google_auth.py`)

- **3.41** Salud anónima sin credenciales. Falsador: la salud expone secretos. Prueba: `test_anonymous_health_exposes_no_credentials`.
- **3.42** Sin autorización no hay sonda; prompts y documentos arbitrarios se rechazan. Falsador: sonda anónima o prompt libre. Pruebas: `test_no_unauthorized_probe`, `test_rejects_arbitrary_prompts_and_documents`.
- **3.43** Sin persistencia en nube no se invoca el modelo. Falsador: inferencia con Apps Script caído. Prueba: `test_cloud_without_persistence_never_invokes_model`.
- **3.44** Solo el propietario autoriza; Google es la autoridad. Falsador: otra cuenta autoriza. Pruebas: `test_other_google_account_rejected`, `test_google_reply_is_authoritative`.
- **3.45** Tokens ajenos o basura nunca llegan a Google. Falsador: llamada a tokeninfo con un token basura. Prueba: `test_junk_and_foreign_tokens_never_reach_google`.
- **3.46** Un token revocado cierra sin filtrar secretos. Falsador: secreto en el error. Prueba: `test_revoked_refresh_token_fails_closed_without_secrets`.
- **3.47** `cloud_gate_passed` es siempre `false` en este hito (`AGENTS.md`, `docs/first-milestone.md`). Falsador: una respuesta o un literal con `true`. Pruebas: `test_c2_cloud_gate_never_true_in_source`, aserciones en `test_http.py`, `test_probe.py`, `test_recovery.py`.
- **3.48** Sin keepalive artificial; los pings a `/healthz` solo como excepción temporal de la Fase D. Falsador: un cliente o documento que programe pings sin esa marca. Prueba: `test_c1_pings_only_as_temporary_exception`.

## 3.5 Cliente móvil (`web/app.js`)

- **3.51** Autorun estricto: captura el id, limpia el hash, usa `prompt=none`. Falsador: un fragmento inválido redirige o envía. Pruebas: `strict autorun captures id, removes hash and starts Google with prompt=none`, `invalid autorun fragments never redirect or submit`.
- **3.52** Una respuesta perdida no reenvía; recupera el resultado guardado. Falsador: reenvío automático. Pruebas: `lost probe response consumes autorun without an automatic resubmission`, `lost probe response recovers the saved result without submitting again`.
- **3.53** `state` o `nonce` incorrectos bloquean. Falsador: autenticación con nonce ajeno. Prueba: `wrong state or nonce blocks authentication and autorun`.

## 3.6 Corpus y privacidad (`tools/corpus.py`, `corpus.lock`)

- **3.61** Un byte alterado en el corpus hace fallar la verificación. Falsador: un corpus manipulado pasa. Pruebas: `test_corpus_verify_fails_on_single_byte_tamper`, `test_corpus_verify_passes_on_valid_data`.
- **3.62** El cerebro no versiona blobs privados ni hechos binarios. Falsador: un binario de expediente en el árbol. Prueba: `test_no_private_blobs_or_binary_facts`.
- **3.63** El Tractatus es ejecutable: toda proposición 3.x tiene falsador y cita pruebas que existen; la numeración es única y consecutiva; las pruebas huérfanas no aumentan. Falsador: una proposición sin falsador, con prueba inexistente o numeración rota pasa el lint. Pruebas: `test_tractatus_lint_passes`, `test_lint_detects_missing_cited_test`, `test_lint_detects_missing_falsifier_and_duplicate_numbering`, `test_lint_detects_gap_in_numbering`, `test_orphan_tests_do_not_grow`.
- **3.64** Un archivo del corpus que no figura en `corpus.lock` refuta la integridad. Falsador: un archivo intruso pasa `verify`. Prueba: `test_corpus_verify_fails_on_extra_file`.
- **3.65** `file_count` del lock debe coincidir con los archivos listados. Falsador: un recuento falso pasa `verify`. Prueba: `test_corpus_verify_fails_on_file_count_mismatch`.
- **3.66** El HEAD del corpus debe ser el commit fijado. Falsador: un HEAD movido pasa `verify` aunque los bytes coincidan. Prueba: `test_corpus_verify_fails_when_head_moves`.
- **3.67** `pin` y `sync` son reproducibles: lo fijado se recupera íntegro y cualquier alteración posterior se detecta. Falsador: tras `pin`→`sync`, un hecho alterado pasa `verify`. Prueba: `test_corpus_pin_then_sync_roundtrip`.
- **3.68** Cada regla crítica tiene un mutante automático que su prueba elimina (`tools/mutate.py`, en CI). Falsador: un mutante sobrevive o deja de aplicarse al código actual. Prueba: `test_mutants_apply_to_current_sources`.

## Deuda de falsación

Proposiciones sin prueba dedicada en `tests/`:

- **D1** (resuelta: ahora 3.47; ver `contradicciones.md`).
- **D2** (pagada con evidencia Real, 02/10/2026): renovación tras más de 1 h, t=0/35/70 min `synthetic_success`, t=70 sin intervención; ver `STATUS.md`. La parte automática sigue siendo `test_expiring_token_is_refreshed` (simulada).
- **D3** (pagada con matiz, 03/10/2026): lanzamiento móvil, ID `0fc2e9a7201fc0bcc41ef1eb690a2b25` recuperado; PC2 apagada y PC1 desvinculada (monitor). «Ambos apagados» literal sigue sin probarse.
- **D4** Nivel de suscripción comprobado por vía oficial (matriz: no comprobado).
- **D5** No se fusiona un PR sin autorización explícita de su número (`AGENTS.md`): regla de proceso.
- **D6** La conservación documental no habilita el agente en nube (`AGENTS.md`).

## Recuento

- Con prueba: **42** (3.11–3.17: 7; 3.21–3.29: 9; 3.31–3.37: 7; 3.41–3.48: 8; 3.51–3.53: 3; 3.61–3.68: 8). Mutantes: 9/9 eliminados (`tools/mutate.py`). Comprobado automáticamente por `tools/tractatus.py` (3.63).
- Sin prueba automática: D2–D3 pagadas con evidencia Real; deuda abierta **3** (D4–D6).
