#!/usr/bin/env python3
"""
Mailcow Alias Generator
Flask server to automatically create aliases via Mailcow API
"""

import os
import json
import requests
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import logging
from datetime import datetime

# Logging configuration
log_dir = 'logs' if os.path.exists('logs') else '.'
log_file = os.path.join(log_dir, 'mailcow_alias.log')

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_file),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Default configuration
DEFAULT_CONFIG = {
    "mailcow_url": "https://mail.example.com",
    "api_key": "YOUR_MAILCOW_API_KEY",
    "domain": "example.com",
    "default_redirect": "user@example.com",
    "sogo_visible": True,
    "port": 5000
}

def load_config():
    """Load configuration from config.json file"""
    config_file = 'config.json'
    
    if not os.path.exists(config_file):
        logger.warning(f"Configuration file {config_file} not found. Creating sample file.")
        with open('config.sample.json', 'w', encoding='utf-8') as f:
            json.dump(DEFAULT_CONFIG, f, indent=2, ensure_ascii=False)
        
        logger.error("Please copy config.sample.json to config.json and configure your settings.")
        return None
    
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Check required parameters
        required_keys = ['mailcow_url', 'api_key', 'domain']
        for key in required_keys:
            if not config.get(key) or config[key] == DEFAULT_CONFIG[key]:
                logger.error(f"Parameter '{key}' missing or not configured in config.json")
                return None
        
        return config
    except json.JSONDecodeError as e:
        logger.error(f"JSON format error in config.json: {e}")
        return None
    except Exception as e:
        logger.error(f"Error loading configuration: {e}")
        return None

def create_mailcow_alias(alias_email, redirect_to, config):
    """Create an alias in Mailcow via API"""
    
    # Mailcow API URL for aliases
    api_url = f"{config['mailcow_url'].rstrip('/')}/api/v1/add/alias"
    
    # Headers for authentication
    headers = {
        'X-API-Key': config['api_key'],
        'Content-Type': 'application/json'
    }
    
    # Data to create the alias
    data = {
        'address': alias_email,
        'goto': redirect_to,
        'active': 1,
        'sogo_visible': 1 if config.get('sogo_visible', True) else 0
    }
    
    try:
        logger.info(f"Creating alias {alias_email} -> {redirect_to}")
        
        response = requests.post(api_url, headers=headers, json=data, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            
            # Handle Mailcow API response format (array of objects)
            if isinstance(result, list) and len(result) > 0:
                first_result = result[0]
                if first_result.get('type') == 'success':
                    logger.info(f"Alias created successfully: {alias_email}")
                    return True, "Alias created successfully"
                else:
                    error_msg = first_result.get('msg', 'Unknown error')
                    if isinstance(error_msg, list):
                        error_msg = ' '.join(str(x) for x in error_msg)
                    logger.error(f"Mailcow API error: {error_msg}")
                    return False, error_msg
            # Fallback for other response formats
            elif isinstance(result, dict):
                if result.get('type') == 'success':
                    logger.info(f"Alias created successfully: {alias_email}")
                    return True, "Alias created successfully"
                else:
                    error_msg = result.get('msg', 'Unknown error')
                    logger.error(f"Mailcow API error: {error_msg}")
                    return False, error_msg
            else:
                logger.error(f"Unexpected API response format: {result}")
                return False, "Unexpected API response format"
        else:
            logger.error(f"HTTP error {response.status_code}: {response.text}")
            return False, f"HTTP error {response.status_code}"
            
    except requests.exceptions.Timeout:
        logger.error("Timeout connecting to Mailcow")
        return False, "Connection timeout"
    except requests.exceptions.ConnectionError:
        logger.error("Unable to connect to Mailcow")
        return False, "Unable to connect to Mailcow server"
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return False, f"Unexpected error: {str(e)}"

def check_alias_exists(alias_email, config):
    """Check if an alias already exists"""
    
    api_url = f"{config['mailcow_url'].rstrip('/')}/api/v1/get/alias/all"
    
    headers = {
        'X-API-Key': config['api_key'],
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(api_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            aliases_data = response.json()
            
            # Handle different response formats from Mailcow API
            if isinstance(aliases_data, list):
                aliases = aliases_data
            elif isinstance(aliases_data, dict):
                # Sometimes the API returns a dict with aliases in a specific key
                aliases = aliases_data.get('data', aliases_data.get('aliases', []))
                if not isinstance(aliases, list):
                    aliases = []
            else:
                aliases = []
            
            # Check if alias exists
            for alias in aliases:
                if isinstance(alias, dict) and alias.get('address') == alias_email:
                    return True
        
        return False
        
    except Exception as e:
        logger.warning(f"Unable to check alias existence: {e}")
        return False

@app.route('/')
def index():
    """Home page"""
    return send_from_directory('.', 'index.html')

@app.route('/api/create-alias', methods=['POST'])
def create_alias():
    """Endpoint to create an alias"""
    
    # Load configuration
    config = load_config()
    if not config:
        return jsonify({'error': 'Invalid configuration'}), 500
    
    try:
        data = request.get_json()
        
        if not data:
            return jsonify({'error': 'Missing JSON data'}), 400
        
        alias_email = data.get('alias', '').strip().lower()
        redirect_to = data.get('redirectTo', '').strip().lower()
        
        # Data validation
        if not alias_email or not redirect_to:
            return jsonify({'error': 'Alias and redirect address required'}), 400
        
        # Check email format
        if '@' not in alias_email or '@' not in redirect_to:
            return jsonify({'error': 'Invalid email format'}), 400
        
        # Check that alias uses the correct domain
        if not alias_email.endswith(f"@{config['domain']}"):
            return jsonify({'error': f'Alias must use domain {config["domain"]}'}), 400
        
        # Check if alias already exists (temporarily disabled due to API format issues)
        # if check_alias_exists(alias_email, config):
        #     return jsonify({'error': 'This alias already exists'}), 409
        
        # Create alias
        success, message = create_mailcow_alias(alias_email, redirect_to, config)
        
        if success:
            # Activity log
            log_entry = {
                'timestamp': datetime.now().isoformat(),
                'alias': alias_email,
                'redirect_to': redirect_to,
                'status': 'success'
            }
            
            # Save to JSON log file
            try:
                alias_log_file = os.path.join(log_dir, 'alias_log.json')
                with open(alias_log_file, 'a', encoding='utf-8') as f:
                    f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
            except Exception as e:
                logger.warning(f"Unable to save log: {e}")
            
            return jsonify({
                'success': True,
                'message': message,
                'alias': alias_email,
                'redirect_to': redirect_to
            })
        else:
            return jsonify({'error': message}), 400
            
    except Exception as e:
        logger.error(f"Error creating alias: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/status')
def status():
    """Endpoint to check API status"""
    config = load_config()
    
    if not config:
        return jsonify({
            'status': 'error',
            'message': 'Invalid configuration'
        }), 500
    
    # Test connection to Mailcow
    try:
        api_url = f"{config['mailcow_url'].rstrip('/')}/api/v1/get/domain/all"
        headers = {'X-API-Key': config['api_key']}
        
        response = requests.get(api_url, headers=headers, timeout=5)
        
        if response.status_code == 200:
            return jsonify({
                'status': 'ok',
                'mailcow_url': config['mailcow_url'],
                'domain': config['domain'],
                'connection': 'success'
            })
        else:
            return jsonify({
                'status': 'error',
                'message': f'Mailcow connection error: {response.status_code}'
            }), 500
            
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': f'Unable to connect to Mailcow: {str(e)}'
        }), 500

@app.route('/api/config')
def get_config():
    """Endpoint to get public configuration information"""
    config = load_config()
    
    if not config:
        return jsonify({
            'status': 'error',
            'message': 'Invalid configuration'
        }), 500
    
    return jsonify({
        'domain': config['domain'],
        'default_redirect': config.get('default_redirect', 'user@example.com')
    })

if __name__ == '__main__':
    # Load configuration to get port
    config = load_config()
    port = config.get('port', 5000) if config else 5000
    
    print("🚀 Starting Mailcow alias generator...")
    print("📝 Make sure you have configured the config.json file")
    print(f"🌐 Interface available at http://localhost:{port}")
    
    app.run(debug=True, host='0.0.0.0', port=port)