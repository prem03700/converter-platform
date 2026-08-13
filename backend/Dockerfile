# ─── Stage 1: Build virtualenv ─────────────────────────────────────────────
FROM python:3.12-slim AS builder

WORKDIR /build

# System libraries needed by Python packages at *build* time
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential gcc libmagic-dev libcairo2-dev pkg-config \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --upgrade pip --quiet && \
    /venv/bin/pip install -r requirements.txt --quiet


# ─── Stage 2: Runtime image ────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Runtime system dependencies (converters, OCR)
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    tesseract-ocr \
    tesseract-ocr-eng \
    libreoffice-writer \
    libreoffice-calc \
    libreoffice-impress \
    libmagic1 \
    libcairo2 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy virtualenv from builder — no compilation in the runtime stage
COPY --from=builder /venv /venv
ENV PATH="/venv/bin:$PATH"

# Non-root user for security
RUN useradd --create-home --no-log-init appuser
WORKDIR /app

COPY . .
RUN chown -R appuser:appuser /app
USER appuser

# Storage directory
RUN mkdir -p /app/storage_data

EXPOSE 8000

# Run migrations automatically on startup then boot the server.
# For zero-downtime deployments, split this into a separate migration
# init-container in Kubernetes or a pre-deploy Render/Railway command.
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2"]
