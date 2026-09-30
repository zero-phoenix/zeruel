FROM node:22-bookworm-slim AS node
FROM python:3.12-slim-bookworm
COPY --from=node /usr/local/bin/node /usr/local/bin/node
RUN apt-get update && apt-get install -y --no-install-recommends libstdc++6 ca-certificates \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY scripts/install_cli.py scripts/install_cli.py
RUN python3 scripts/install_cli.py --destination /opt/zeruel-cli
COPY zeruel zeruel
COPY web web
RUN useradd --create-home zeruel && mkdir -p /app/work/private && chown -R zeruel:zeruel /app /opt/zeruel-cli
USER zeruel
ENV ZERUEL_CLI_BUNDLE=/opt/zeruel-cli/package/bundle/gemini.js
ENV ZERUEL_PRIVATE_HOME=/app/work/private/gemini-home
ENV PYTHONUNBUFFERED=1
CMD ["python3", "-m", "zeruel.server"]
