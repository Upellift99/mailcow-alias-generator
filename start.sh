#!/bin/bash

# Startup script for mailcow Alias Generator
# Usage: ./start.sh

echo "🔗 mailcow Alias Generator"
echo "=========================="

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is not installed"
    exit 1
fi

# Check if configuration file exists
if [ ! -f "config.json" ]; then
    echo "⚠️  config.json file missing"
    echo "📝 Creating configuration file..."
    
    if [ -f "config.sample.json" ]; then
        cp config.sample.json config.json
        echo "✅ config.json file created from config.sample.json"
        echo ""
        echo "🔧 IMPORTANT: Edit config.json with your mailcow settings:"
        echo "   - mailcow_url: URL of your mailcow instance"
        echo "   - api_key: Your mailcow API key"
        echo "   - domain: Your domain for aliases"
        echo "   - default_redirect: Default redirect address"
        echo ""
        echo "Then run this script again."
        exit 1
    else
        echo "❌ config.sample.json file missing"
        exit 1
    fi
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
if ! python3 -c "import flask, flask_cors, requests" 2>/dev/null; then
    echo "📥 Installing dependencies..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Error installing dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
else
    echo "✅ Dependencies already installed"
fi

# Check configuration
echo "🔧 Checking configuration..."
if grep -q "YOUR_MAILCOW_API_KEY" config.json; then
    echo "❌ Configuration not completed"
    echo "🔧 Please edit config.json with your real mailcow settings"
    exit 1
fi

if grep -q "mail.example.com" config.json; then
    echo "❌ mailcow URL not configured"
    echo "🔧 Please edit config.json with your real mailcow URL"
    exit 1
fi

echo "✅ Configuration looks correct"

# Start application
echo ""
echo "🚀 Starting application..."

# Extract port from config.json if it exists
if command -v jq &> /dev/null && [ -f "config.json" ]; then
    PORT=$(jq -r '.port // 5000' config.json 2>/dev/null || echo "5000")
else
    PORT="5000"
fi

echo "🌐 Interface available at: http://localhost:$PORT"
echo "🛑 Press Ctrl+C to stop"
echo ""

python3 app.py