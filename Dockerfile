# ───────────────────────────────────
#  Dockerfile  (SecretHitler Fa Bot)
# ───────────────────────────────────

# 1) base image
FROM python:3.10-slim

ARG GIT_SHA=""

# 2) install system deps required by cryptography / pycparser
RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        libffi-dev \
        libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# 3) workdir inside the container
WORKDIR /app

# 4) copy requirements and install (wheel cache disabled for smaller image)
COPY requirements.txt .
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# 5) copy the rest of the source code
COPY . .

# 6) runtime env-vars (optional defaults; real TOKEN via Fly secrets)
ENV PYTHONUNBUFFERED=1 \
    BOT_TOKEN="" \
    STATS_PATH="./stats.json" \
    GIT_SHA=$GIT_SHA

# 7) start command (match your MainController location)
CMD ["python", "MainController.py"]
