# Trust Bench SecureEval + Ops - Production Dockerfile
# Multi-stage build for smaller final image

FROM python:3.11-slim as builder

# Set working directory
WORKDIR /app

# Install build dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        gcc \
        g++ \
        build-essential && \
    rm -rf /var/lib/apt/lists/*

# Copy requirements files
COPY Project2v2/requirements-phase1.txt ./
COPY Project2v2/requirements-optional.txt ./

# Create virtual environment and install dependencies
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements-phase1.txt && \
    pip install --no-cache-dir -r requirements-optional.txt

# Final stage - smaller runtime image
FROM python:3.11-slim

# Install runtime dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        git \
        ca-certificates && \
    rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 trustbench && \
    mkdir -p /app /data /logs && \
    chown -R trustbench:trustbench /app /data /logs

# Copy virtual environment from builder
COPY --from=builder --chown=trustbench:trustbench /opt/venv /opt/venv

# Set working directory and user
WORKDIR /app
USER trustbench

# Copy application code
COPY --chown=trustbench:trustbench Project2v2/ ./Project2v2/
COPY --chown=trustbench:trustbench trustbench_core/ ./trustbench_core/

# Set environment variables
ENV PATH="/opt/venv/bin:$PATH" \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    TB_RUN_MODE=strict \
    ENABLE_SECURITY_FILTERS=true \
    WEB_PORT=5001

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5001/healthz').read()" || exit 1

# Expose web interface port
EXPOSE 5001

# Volume for persistent data
VOLUME ["/data", "/logs"]

# Set working directory to Project2v2
WORKDIR /app/Project2v2

# Start web interface
CMD ["python", "web_interface.py"]
