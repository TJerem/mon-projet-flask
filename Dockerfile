# Etape 1: Builder
FROM python:3.12-slim AS builder
WORKDIR /app
# Installer uniquement les dependances de production
RUN pip install --no-cache-dir --user flask gunicorn

# Etape 2: Runner
FROM python:3.12-slim AS runner
WORKDIR /app
# Installer curl pour le health check
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*
# Recuperer les dependances de production depuis le builder
COPY --from=builder /root/.local /root/.local
# Code source
COPY src/ ./src/
# Configurer le PATH pour gunicorn
ENV PATH=/root/.local/bin:$PATH
# Health check
HEALTHCHECK --interval=30s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:5000/health || exit 1
EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "src.app:app"]
