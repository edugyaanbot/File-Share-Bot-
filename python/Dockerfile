FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY app/ ./app/

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8080/healthz || exit 1

# Run with gunicorn + uvicorn workers
CMD ["gunicorn", "app.web.main:app", \
     "-k", "uvicorn.workers.UvicornWorker", \
     "--workers", "2", \
     "--threads", "1", \
     "--bind", "0.0.0.0:8080", \
     "--timeout", "60", \
     "--graceful-timeout", "30", \
     "--keep-alive", "75", \
     "--access-logfile", "-", \
     "--error-logfile", "-"]
