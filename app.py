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
from datetime import datetime, timedelta
from altcha import ChallengeOptions, create_challenge, verify_solution

# Logging configuration
# In Docker, we only log to console (best practice for containers)
if os.getenv('DOCKER_CONTAINER'):
    # Docker environment - console logging only
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[logging.StreamHandler()]
    )
    log_dir = '/app/logs'  # For compatibility with log saving functions
else:
    # Local environment - try file logging with fallback
    log_dir = '/app/logs'
    log_file = os.path.join(log_dir, 'mailcow_alias.log')
    
    handlers = [logging.StreamHandler()]
    try:
        os.makedirs(log_dir, exist_ok=True)
        handlers.append(logging.FileHandler(log_file))
    except (PermissionError, OSError) as e:
        print(f"Warning: Cannot write to log file {log_file}: {e}")
        print("Logging will only be available in console.")
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)

# Default configuration
DEFAULT_CONFIG = {
    "mailcow_url": "https://mail.example.com",
    "api_key": "YOUR_MAILCOW_API_KEY",
    "domains": ["example.com", "example2.com"],
    "default_domain": "example.com",
    "sogo_visible": True,
    "altcha_enabled": False,
    "altcha_hmac_key": "head -c32 /dev/urandom | base64",
    "port": 5000,
    "users": {
        "user1": {
            "password": "password_user1",
            "default_redirect": "user1@example.com",
            "description": "First user"
        },
        "user2": {
            "password": "password_user2",
            "default_redirect": "user2@example.com",
            "description": "Second user"
        }
    }
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
        
        # Support both old 'domain' format and new 'domains' format
        if 'domain' in config and 'domains' not in config:
            # Convert old single domain format to new format
            config['domains'] = [config['domain']]
            config['default_domain'] = config['domain']

        # Check required parameters
        required_keys = ['mailcow_url', 'api_key']
        for key in required_keys:
            if not config.get(key) or config[key] == DEFAULT_CONFIG.get(key):
                logger.error(f"Parameter '{key}' missing or not configured in config.json")
                return None

        # Check domains configuration
        if not config.get('domains') or not isinstance(config['domains'], list) or len(config['domains']) == 0:
            logger.error("Parameter 'domains' missing or not configured properly in config.json")
            return None

        # Set default_domain if not specified
        if not config.get('default_domain'):
            config['default_domain'] = config['domains'][0]
        
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

def create_altcha_challenge(config):
    """Create a new ALTCHA challenge"""
    try:
        altcha_hmac_key = config.get('altcha_hmac_key')
        if not altcha_hmac_key:
            logger.error("ALTCHA HMAC key not configured")
            return None, "ALTCHA not configured"
        
        # Create challenge options
        options = ChallengeOptions(
            expires=datetime.now() + timedelta(hours=1),
            max_number=10000,  # Maximum random number
            hmac_key=altcha_hmac_key,
        )
        
        # Create the challenge
        challenge = create_challenge(options)
        logger.info("ALTCHA challenge created successfully")
        
        return challenge, None
        
    except Exception as e:
        logger.error(f"Error creating ALTCHA challenge: {e}")
        return None, f"ALTCHA error: {str(e)}"

def verify_altcha_solution(payload, config, check_expires=True):
    """Verify an ALTCHA solution"""
    try:
        altcha_hmac_key = config.get('altcha_hmac_key')
        if not altcha_hmac_key:
            logger.error("ALTCHA HMAC key not configured")
            return False, "ALTCHA not configured"
        
        # Verify the solution
        ok, err = verify_solution(payload, altcha_hmac_key, check_expires=check_expires)
        
        if err:
            logger.warning(f"ALTCHA verification error: {err}")
            return False, str(err)
        elif ok:
            logger.info("ALTCHA solution verified successfully")
            return True, "Valid solution"
        else:
            logger.warning("Invalid ALTCHA solution")
            return False, "Invalid solution"
            
    except Exception as e:
        logger.error(f"Error verifying ALTCHA solution: {e}")
        return False, f"ALTCHA error: {str(e)}"

def authenticate_user(password, config):
    """Authenticate user and return user info if successful"""
    # Check multi-user configuration
    users = config.get('users', {})
    for user_id, user_config in users.items():
        if user_config.get('password') == password:
            return {
                'user_id': user_id,
                'default_redirect': user_config.get('default_redirect', 'user@example.com'),
                'description': user_config.get('description', f'User {user_id}')
            }
    
    return None

@app.route('/')
def index():
    """Home page"""
    return send_from_directory('.', 'index.html')

@app.route('/login')
def login():
    """Login page"""
    return send_from_directory('.', 'login.html')

@app.route('/favicon.ico')
def favicon():
    """Serve favicon.ico"""
    return send_from_directory('.', 'favicon.ico')

@app.route('/favicon.svg')
def favicon_svg():
    """Serve favicon.svg"""
    return send_from_directory('.', 'favicon.svg')

@app.route('/altcha.js')
def altcha_js():
    """Serve altcha.js"""
    return send_from_directory('.', 'altcha.js')


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

        # Check that alias uses one of the allowed domains
        allowed_domains = config.get('domains', [])
        alias_domain = alias_email.split('@')[1] if '@' in alias_email else ''
        if not any(alias_email.endswith(f"@{domain}") for domain in allowed_domains):
            domains_list = ', '.join(allowed_domains)
            return jsonify({'error': f'Alias must use one of the allowed domains: {domains_list}'}), 400
        
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
                'domains': config.get('domains', []),
                'default_domain': config.get('default_domain'),
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
    
    # Get user info from query parameter if provided (for authenticated requests)
    user_id = request.args.get('user_id')
    default_redirect = 'user@example.com'
    
    # If user_id is provided, get user-specific default redirect
    if user_id and config.get('users', {}).get(user_id):
        user_config = config['users'][user_id]
        default_redirect = user_config.get('default_redirect', default_redirect)
    
    return jsonify({
        'domains': config.get('domains', [config.get('domain', 'example.com')]),
        'default_domain': config.get('default_domain', config.get('domains', ['example.com'])[0]),
        'default_redirect': default_redirect,
        'altcha_enabled': config.get('altcha_enabled', False),
        'multi_user_enabled': bool(config.get('users'))
    })

@app.route('/api/altcha/challenge', methods=['GET'])
def get_altcha_challenge():
    """Endpoint to get an ALTCHA challenge"""
    config = load_config()
    
    if not config:
        return jsonify({'error': 'Invalid configuration'}), 500
    
    # Check if ALTCHA is enabled
    if not config.get('altcha_enabled', False):
        return jsonify({'error': 'ALTCHA not enabled'}), 400
    
    try:
        challenge, error = create_altcha_challenge(config)
        
        if error:
            return jsonify({'error': error}), 500
        
        return jsonify({
            'algorithm': challenge.algorithm,
            'challenge': challenge.challenge,
            'salt': challenge.salt,
            'signature': challenge.signature
        })
        
    except Exception as e:
        logger.error(f"Error creating ALTCHA challenge: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/api/auth', methods=['POST'])
def authenticate():
    """Endpoint to authenticate with password"""
    config = load_config()
    
    if not config:
        return jsonify({'error': 'Invalid configuration'}), 500
    
    try:
        data = request.get_json()
        if not data or 'password' not in data:
            return jsonify({'error': 'Password required'}), 400
        
        # ALTCHA verification if enabled
        if config.get('altcha_enabled', False):
            altcha_payload = data.get('altcha')
            if not altcha_payload:
                return jsonify({'error': 'ALTCHA solution required'}), 400
            
            # Verify ALTCHA solution
            valid, error_msg = verify_altcha_solution(altcha_payload, config)
            if not valid:
                return jsonify({'error': f'ALTCHA verification failed: {error_msg}'}), 400
        
        provided_password = data['password']
        
        # Authenticate user with new multi-user system
        user_info = authenticate_user(provided_password, config)
        
        if user_info:
            logger.info(f"User authenticated: {user_info['user_id']} ({user_info['description']})")
            return jsonify({
                'success': True,
                'message': 'Authentication successful',
                'user': {
                    'id': user_info['user_id'],
                    'default_redirect': user_info['default_redirect'],
                    'description': user_info['description']
                }
            })
        else:
            logger.warning(f"Failed authentication attempt")
            return jsonify({'error': 'Invalid password'}), 401
            
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    # Load configuration to get port
    config = load_config()
    port = config.get('port', 5000) if config else 5000
    
    print("🚀 Starting Mailcow alias generator...")
    print("📝 Make sure you have configured the config.json file")
    print(f"🌐 Interface available at http://localhost:{port}")
    
    # Use debug=False for production-like behavior
    app.run(debug=False, host='0.0.0.0', port=port)