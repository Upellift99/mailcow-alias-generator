#!/bin/bash

# Docker startup script for Mailcow alias generator
echo "🚀 Starting Mailcow Alias Generator with Gunicorn..."

# Container always uses port 5000 internally - FORCED in Docker mode
DOCKER_PORT=5000

# In Docker mode, we ALWAYS use port 5000 regardless of config.json
# This ensures consistency with docker-compose.yml port mapping
PORT=$DOCKER_PORT

echo "🌐 Starting server on port $PORT"
echo "📝 Make sure you have configured the config.json file"

# Start Gunicorn with the configured port
exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app