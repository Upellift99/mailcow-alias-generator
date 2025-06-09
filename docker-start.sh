#!/bin/bash

# Docker startup script for Mailcow alias generator
echo "🚀 Starting Mailcow Alias Generator with Gunicorn..."

# Extract port from config.json if it exists, otherwise use default
if [ -f "config.json" ] && command -v python3 &> /dev/null; then
    PORT=$(python3 -c "
import json
import os
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    print(config.get('port', 5000))
except:
    print(5000)
" 2>/dev/null || echo "5000")
else
    PORT=${PORT:-5000}
fi

echo "🌐 Starting server on port $PORT"
echo "📝 Make sure you have configured the config.json file"

# Start Gunicorn with the configured port
exec gunicorn --bind "0.0.0.0:$PORT" --workers 2 --timeout 120 --access-logfile - --error-logfile - app:app