FROM python:3.12-slim

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    STOCKFISH_URL=https://github.com/official-stockfish/Stockfish/releases/download/sf_18/stockfish-ubuntu-x86-64-avx2.tar \
    STOCKFISH_EXECUTABLE=/usr/local/bin/stockfish

WORKDIR /workspace

COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir -r requirements.txt

# Official Linux Stockfish 18 for the analysis worker. The repository ships a
# Windows-only exe under data/stockfish, which cannot run in this Linux image.
# The build fails unless the downloaded engine identifies as Stockfish 18.
RUN apt-get update \
    && apt-get install -y --no-install-recommends curl ca-certificates tar \
    && rm -rf /var/lib/apt/lists/* \
    && mkdir -p /tmp/sf-ex \
    && curl -fsSL -o /tmp/sf.tar "$STOCKFISH_URL" \
    && tar -xf /tmp/sf.tar -C /tmp/sf-ex \
    && cp "$(find /tmp/sf-ex -type f -name 'stockfish*' | head -n 1)" "$STOCKFISH_EXECUTABLE" \
    && chmod +x "$STOCKFISH_EXECUTABLE" \
    && rm -rf /tmp/sf.tar /tmp/sf-ex \
    && printf 'uci\nquit\n' | "$STOCKFISH_EXECUTABLE" | grep -q 'id name Stockfish 18'

COPY backend ./backend
COPY src ./src
RUN python -m pip install --no-cache-dir --no-deps -e .

CMD ["python", "-m", "uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "5666"]
