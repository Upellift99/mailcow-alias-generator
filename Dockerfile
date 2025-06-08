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

# Create non-root user first
RUN useradd -m -u 1000 appuser

# Switch to appuser and create logs directory
USER appuser
RUN mkdir -p /app/logs && \
    touch /app/logs/mailcow_alias.log && \
    touch /app/logs/alias_log.json

# Expose port (default 5000, can be overridden)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:5000/api/status || exit 1

# Run the application
CMD ["python", "app.py"]