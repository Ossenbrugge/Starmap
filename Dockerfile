# Starmap Docker Image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create app directory
WORKDIR /app

# Create non-root user
RUN useradd --create-home --shell /bin/bash starmap
RUN chown -R starmap:starmap /app

# Copy requirements first for better caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY --chown=starmap:starmap . .

# Create necessary directories
RUN mkdir -p /app/starmap_db /app/logs
RUN chown -R starmap:starmap /app/starmap_db /app/logs

# Switch to non-root user
USER starmap

# Make scripts executable
RUN chmod +x migrate_to_montydb.sh run_starmap.sh

# Initialize database
RUN ./migrate_to_montydb.sh

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/api/spectral-types || exit 1

# Default command
CMD ["python", "app_montydb.py"]

# Labels for metadata
LABEL org.opencontainers.image.title="Starmap" \
      org.opencontainers.image.description="Interactive 3D stellar cartography for science fiction world-building" \
      org.opencontainers.image.authors="Starmap Contributors" \
      org.opencontainers.image.url="https://github.com/starmap/starmap" \
      org.opencontainers.image.source="https://github.com/starmap/starmap" \
      org.opencontainers.image.licenses="Apache-2.0" \
      org.opencontainers.image.version="0.1.0-alpha"