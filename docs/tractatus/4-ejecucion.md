# 4. Ejecución

4 La proposición se ejecuta solo por las vías fijadas; cualquier otra queda fuera del hito.

4.1 **Sonda.** El propietario autenticado con Google lanza la sonda desde `web/app.js` (manual o autorun `#autorun=<id>`). `zeruel/server.py` valida la identidad (`google_auth.py`), reclama el checkpoint en Apps Script y solo entonces `probe.py` invoca el CLI con el prompt fijo de 2.2.

4.2 **Orden.** `claim` (lease global, cooldown 30 s) → diario local → inferencia única → `complete` con la misma generación → lectura por `get`. Un fallo en cualquier paso deja `paused_uncertain`, nunca reintenta el modelo (3.15, 3.29).

4.3 **Recuperación.** Solo manual, por el propietario, con confirmación y generación exacta; nunca desde el servidor (3.33, 3.36).

4.4 **Corpus.** `python tools/corpus.py verify` contra `corpus.lock`; `sync` y `pin` solo con decisión del propietario. El cerebro no escribe en `zeruel-corpus`.

4.5 **Pruebas locales.**

```
python -m pytest -q
node --test tests/*.cjs
```
