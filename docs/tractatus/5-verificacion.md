# 5. Verificación

5 Una proposición vale mientras su falsador no ocurra. Verificar es intentar refutarla.

5.1 **Pruebas.** Cada proposición de `3-proposiciones.md` nombra una prueba de `tests/`. Que el nombre exista se comprueba con `grep` sobre `tests/`; que pase, con `python -m pytest -q` y `node --test tests/*.cjs`.

5.2 **Mutaciones.** Una prueba solo cuenta si falla cuando se rompe la regla. Mutaciones mínimas recomendadas: aceptar `sum != 42` (3.11), permitir un segundo `claim` (3.23), devolver `cloud_gate_passed: true` (D1), omitir la comprobación de generación (3.26), no borrar secretos del entorno hijo (3.16), alterar un byte del corpus (3.61, ya automatizada). Ninguna mutación se fusiona.

5.3 **Evidencia REAL vs SIMULADA.**
- **REAL**: observada en Render o Apps Script con identificador, hora y resultado registrados en `docs/first-milestone.md` o `docs/HANDOFF.md`.
- **SIMULADA**: reproducida por pruebas locales o dobles de prueba. No completa una fila de la matriz.
- **Pendiente**: sin evidencia. Una prueba Simulada nunca se reetiqueta como Real.

5.4 La deuda de falsación (D1–D6) se paga con una prueba o con evidencia Real; mientras tanto, esas proposiciones no se afirman como verificadas.
