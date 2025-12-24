# herald/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    python3-dev \
    curl \
    libpq-dev \
    linux-libc-dev \
    libc6-dev \
    --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY herald/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy Herald application code
COPY herald/ .

# Copy Squire module
COPY squire/ ./squire/

# Copy Alembic configuration and migrations
COPY alembic.ini .
COPY alembic/ ./alembic/

EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run with single worker (suitable for small VPS)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--workers", "1"]
