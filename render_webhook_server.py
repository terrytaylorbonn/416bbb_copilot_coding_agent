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

def run_ai_review(pr_number, repo_name):
    """Run AI code review in background thread"""
    try:
        logger.info(f"🤖 Starting AI review for PR #{pr_number} in {repo_name}")
        
        import sys
        sys.path.append('.')
        
        from ai_code_reviewer import (
            get_pr_files, 
            analyze_code_change, 
            generate_ai_review, 
            post_review_comment,
            load_env_vars
        )
        
        load_env_vars()
        
        github_token = os.getenv('GITHUB_TOKEN')
        openai_key = os.getenv('OPENAI_API_KEY')
        
        if not github_token or not openai_key:
            logger.error("❌ Missing API keys for AI review")
            return
        
        logger.info(f"🔍 Fetching PR #{pr_number} files...")
        files = get_pr_files(pr_number, github_token, repo_name)
        
        if not files:
            logger.warning("❌ No files found in PR")
            return
        
        logger.info(f"📁 Found {len(files)} changed files")
        review_count = 0
        
        for file_data in files:
            file_path = file_data['filename']
            patch = file_data.get('patch', '')
            sha = file_data['sha']
            
            logger.info(f"📄 Reviewing: {file_path}")
            
            # Skip certain file types
            if any(file_path.endswith(ext) for ext in ['.md', '.txt', '.json', '.yml', '.yaml']):
                continue
            
            changes = analyze_code_change(patch, file_path)
            
            if not changes:
                continue
            
            # Review up to 3 changes per file
            for change in changes[:3]:
                if change['type'] == 'addition':
                    logger.info(f"🧠 Generating AI review for line {change['line']}...")
                    
                    ai_comment = generate_ai_review(
                        change['code'], 
                        file_path, 
                        change['type'], 
                        openai_key
                    )
                    
                    if not ai_comment.startswith("Error:"):
                        success = post_review_comment(
                            pr_number, 
                            sha, 
                            file_path, 
                            change['line'], 
                            f"🤖 **Auto AI Review:**\n\n{ai_comment}", 
                            github_token, 
                            repo_name
                        )
                        
                        if success:
                            logger.info(f"✅ Posted AI review comment on line {change['line']}")
                            review_count += 1
                        else:
                            logger.error(f"❌ Failed to post comment on line {change['line']}")
        
        logger.info(f"🎉 AI Review Complete! Posted {review_count} comments on PR #{pr_number}")
        
    except Exception as e:
        logger.error(f"❌ Error in AI review: {e}")

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
        repo_data = payload.get('repository', {})
        
        pr_number = pr_data.get('number')
        repo_name = repo_data.get('full_name')
        pr_title = pr_data.get('title', 'Unknown')
        
        logger.info(f"🔄 PR Action: {action}")
        logger.info(f"📋 PR #{pr_number}: {pr_title}")
        logger.info(f"📁 Repository: {repo_name}")
        
        # Trigger AI review when PR is opened
        if action == 'opened':
            logger.info(f"🚀 New PR detected! Triggering AI review...")
            
            # Run AI review in background thread
            thread = threading.Thread(
                target=run_ai_review, 
                args=(pr_number, repo_name)
            )
            thread.daemon = True
            thread.start()
            
            return jsonify({
                'status': 'success',
                'message': f'AI review triggered for PR #{pr_number}'
            }), 200
        
        else:
            return jsonify({
                'status': 'ignored',
                'message': f'Action "{action}" not handled'
            }), 200
    
    return jsonify({'status': 'ignored'}), 200

if __name__ == '__main__':
    logger.info("🚀 Starting AI Copilot Webhook Server...")
    logger.info(f"🌐 Port: {PORT}")
    logger.info(f"🔑 GitHub Token: {'✅' if GITHUB_TOKEN else '❌'}")
    
    # CRITICAL: Render.com requires host='0.0.0.0' and the PORT env var
    app.run(host='0.0.0.0', port=PORT, debug=False)