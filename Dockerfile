# ── Stage 1: Build frontend ──────────────────────────────────────────
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --prefer-offline
COPY frontend/ ./
RUN npm run build

# ── Stage 2: Python dependencies ────────────────────────────────────
FROM python:3.12-slim AS deps
WORKDIR /deps
COPY recruit-ai/backend/requirements.txt .
RUN pip install --no-cache-dir --prefix=/install -r requirements.txt

# ── Stage 3: Runtime ────────────────────────────────────────────────
FROM python:3.12-slim AS runtime

# Install only runtime system deps (no build-essential)
RUN apt-get update && apt-get install -y --no-install-recommends \
    poppler-utils && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy installed Python packages
COPY --from=deps /install /usr/local

# Copy only necessary code (not tests, not venvs, not node_modules)
COPY recruit-ai/backend/ /app/recruit-ai/
COPY component1/ml/ /app/component1/ml/
COPY component1/models/ /app/component1/models/
COPY component2/backend/ /app/component2/backend/
COPY component2/models/ /app/component2/models/
COPY component2/raigs/ /app/component2/raigs/
COPY component3/backend/ /app/component3/backend/
COPY component3/data/ /app/component3/data/
COPY component3/engine/ /app/component3/engine/
COPY component3/ltr/ /app/component3/ltr/
COPY component3/models/ /app/component3/models/
COPY component4/backend/ /app/component4/backend/
COPY component4/models/ /app/component4/models/
COPY component4/ml/ /app/component4/ml/

# Copy built frontend
COPY --from=frontend-build /build/dist/ /app/frontend/dist/

ENV PYTHONPATH="/app:/app/component1/ml:/app/component2/ml:/app/component3:/app/component4"

EXPOSE 8000

CMD ["uvicorn", "recruit-ai.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
