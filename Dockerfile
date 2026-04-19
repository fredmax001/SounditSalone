# Sound It Platform - Production Dockerfile
# Multi-stage build with security hardening

# ==========================================
# Stage 1: Build dependencies
# ==========================================
FROM python:3.11-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# ==========================================
# Stage 2: Production image
# ==========================================
FROM python:3.11-slim AS production

# Security: Create non-root user
RUN groupadd -r soundit && useradd -r -g soundit soundit

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Copy Python packages from builder
COPY --from=builder /root/.local /home/soundit/.local
ENV PATH=/home/soundit/.local/bin:$PATH

# Copy application code
COPY --chown=soundit:soundit . .

# Create required directories
RUN mkdir -p uploads logs static && \
    chown -R soundit:soundit /app

# Security: Remove write permissions for group/others
RUN chmod -R u+rwX,go-rwx /app

# Switch to non-root user
USER soundit

# Environment variables (DO NOT set secrets here - use .env or secrets manager)
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

EXPOSE 8000

# Use production server configuration
CMD ["uvicorn", "main_production:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "4"]
