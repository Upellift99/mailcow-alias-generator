FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY app.py .
COPY index.html .
COPY login.html .
COPY favicon.ico .
COPY favicon.svg .
COPY altcha.js .
COPY docker-start.sh .

# Create non-root user and set up permissions
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to appuser and create logs directory with proper permissions
USER appuser
RUN mkdir -p /app/logs && \
    touch /app/logs/mailcow_alias.log && \
    touch /app/logs/alias_log.json && \
    chmod 664 /app/logs/mailcow_alias.log && \
    chmod 664 /app/logs/alias_log.json && \
    chmod +x docker-start.sh

# Set environment variable to indicate Docker container
ENV DOCKER_CONTAINER=true

# Set default port (can be overridden)
ENV PORT=5000

# Expose port (configurable via environment variable)
EXPOSE $PORT

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT}/api/status || exit 1

# Run the application with our custom startup script
CMD ["./docker-start.sh"]