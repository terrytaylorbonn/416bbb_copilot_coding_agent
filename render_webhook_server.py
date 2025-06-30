#!/usr/bin/env python3
"""
Production Webhook Server for Render.com Deployment
"""

import os
import json
import hashlib
import hmac
import logging
from flask import Flask, request, jsonify
import threading

# Set up logging for production
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_env_vars():
    """Load environment variables from .env file if it exists"""
    env_file = '.env'
    env_vars = {}
    
    if os.path.exists(env_file):
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    return env_vars

# Load environment variables
load_env_vars()

app = Flask(__name__)

# Configuration - CRITICAL: Render.com requires PORT env var
PORT = int(os.getenv('PORT', 10000))
WEBHOOK_SECRET = os.getenv('GITHUB_WEBHOOK_SECRET', 'your-webhook-secret-here')
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

@app.route('/health', methods=['GET'])
def health_check():
    """Simple health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'webhook_server': 'running',
        'github_token': 'configured' if GITHUB_TOKEN else 'missing',
        'openai_key': 'configured' if OPENAI_API_KEY else 'missing',
        'environment': 'production',
        'port': PORT
    }), 200

@app.route('/', methods=['GET'])
def index():
    """Root endpoint with basic info"""
    return jsonify({
        'name': 'AI Copilot Webhook Server',
        'version': '1.0.0',
        'environment': 'production',
        'status': 'ready',
        'port': PORT
    }), 200

@app.route('/webhook', methods=['POST'])
def github_webhook():
    """Handle GitHub webhook events"""
    logger.info("🔔 Webhook endpoint hit!")
    
    event_type = request.headers.get('X-GitHub-Event')
    logger.info(f"📨 Event Type: {event_type}")
    
    try:
        payload = request.get_json()
        logger.info(f"📦 Payload received")
    except Exception as e:
        logger.error(f"❌ Error parsing JSON: {e}")
        return jsonify({'error': 'Invalid JSON'}), 400
    
    if event_type == 'pull_request':
        action = payload.get('action')
        pr_data = payload.get('pull_request', {})
        pr_number = pr_data.get('number')
        
        logger.info(f"🔄 PR Action: {action}, PR #{pr_number}")
        
        return jsonify({
            'status': 'success',
            'message': f'Webhook received for PR #{pr_number}'
        }), 200
    
    return jsonify({'status': 'ignored'}), 200

if __name__ == '__main__':
    logger.info("🚀 Starting AI Copilot Webhook Server...")
    logger.info(f"🌐 Port: {PORT}")
    logger.info(f"🔑 GitHub Token: {'✅' if GITHUB_TOKEN else '❌'}")
    
    # CRITICAL: Render.com requires host='0.0.0.0' and the PORT env var
    app.run(host='0.0.0.0', port=PORT, debug=False)