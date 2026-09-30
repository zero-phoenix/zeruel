FROM python:3.12-slim-bookworm
RUN apt-get update && apt-get install -y --no-install-recommends ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY scripts/install_cli.py scripts/install_cli.py
# Root-owned binary: the runtime user cannot self-update it, so the pinned version stays fixed.
RUN python3 scripts/install_cli.py --destination /opt/agy
COPY zeruel zeruel
COPY web web
RUN useradd --create-home zeruel && mkdir -p /app/work/private && chown -R zeruel:zeruel /app/work
USER zeruel
ENV ZERUEL_AGY_BIN=/opt/agy/agy
ENV ZERUEL_PRIVATE_HOME=/app/work/private/gemini-home
ENV PYTHONUNBUFFERED=1
CMD ["python3", "-m", "zeruel.server"]
