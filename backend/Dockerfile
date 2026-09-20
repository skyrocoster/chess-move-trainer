FROM python:3.12-slim@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9 AS stockfish

ARG STOCKFISH_URL=https://github.com/official-stockfish/Stockfish/releases/download/sf_19/stockfish-linux-x86-64-universal.tar.gz
ARG STOCKFISH_ARCHIVE_SHA256=9defc0d4e55d49c65a6d042f3e571a39fcea499ade6dbe741b53b8c65e03611f

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates tar \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /tmp/stockfish \
    && curl -fsSL -o /tmp/stockfish.tar.gz "$STOCKFISH_URL" \
    && echo "$STOCKFISH_ARCHIVE_SHA256  /tmp/stockfish.tar.gz" | sha256sum -c - \
    && tar -xzf /tmp/stockfish.tar.gz -C /tmp/stockfish \
    && cp "$(find /tmp/stockfish -type f -name 'stockfish*' | head -n 1)" /stockfish \
    && chmod 0755 /stockfish \
    && printf 'uci\nquit\n' | /stockfish | grep -q 'id name Stockfish 19'

FROM python:3.12-slim@sha256:2f17fc044b579bab302c2e8054d3a686e2cb9a83de48e70534b94cd8ebbe06a9

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/workspace:/workspace/src \
    STOCKFISH_EXECUTABLE=/usr/local/bin/stockfish

WORKDIR /workspace

COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir --require-hashes -r requirements.txt \
    && groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home app \
    && chown app:app /workspace

COPY --from=stockfish /stockfish /usr/local/bin/stockfish

COPY --chown=app:app backend ./backend
COPY --chown=app:app src ./src

USER app

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "5666"]
