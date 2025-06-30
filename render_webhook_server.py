#!/usr/bin/env python3
"""
Production Webhook Server for Render.com Deployment
"""

import os
import json
import hashlib
import hmac
import logging
import requests
import re
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

def get_pr_files(pr_number, github_token, repo_name):
    """Get changed files from a PR"""
    try:
        url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/files"
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return response.json()
        else:
            logger.error(f"Failed to get PR files: {response.status_code}")
            return []
    except Exception as e:
        logger.error(f"Error getting PR files: {e}")
        return []

def analyze_code_change(patch, file_path):
    """Analyze code changes from git patch"""
    changes = []
    if not patch:
        return changes
    
    lines = patch.split('\n')
    line_number = 0
    
    for line in lines:
        if line.startswith('@@'):
            # Parse line number from hunk header
            match = re.search(r'\+(\d+)', line)
            if match:
                line_number = int(match.group(1))
        elif line.startswith('+') and not line.startswith('+++'):
            # This is an added line
            code = line[1:]  # Remove the '+' prefix
            if code.strip():  # Only non-empty lines
                changes.append({
                    'type': 'addition',
                    'line': line_number,
                    'code': code
                })
            line_number += 1
        elif not line.startswith('-'):
            line_number += 1
    
    return changes

def generate_ai_review(code, file_path, change_type, openai_key):
    """Generate AI review comment using OpenAI"""
    try:
        # Simple AI review prompt
        prompt = f"""Review this code change:

File: {file_path}
Code: {code}

Provide a brief code review focusing on:
- Potential bugs or errors
- Security issues
- Performance improvements
- Best practices

Keep response under 100 words."""

        # OpenAI API call (simplified)
        headers = {
            'Authorization': f'Bearer {openai_key}',
            'Content-Type': 'application/json'
        }
        
        data = {
            'model': 'gpt-3.5-turbo',
            'messages': [{'role': 'user', 'content': prompt}],
            'max_tokens': 150,
            'temperature': 0.7
        }
        
        response = requests.post('https://api.openai.com/v1/chat/completions', 
                               headers=headers, json=data, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            return result['choices'][0]['message']['content'].strip()
        else:
            logger.error(f"OpenAI API error: {response.status_code}")
            return "Error: AI review unavailable"
            
    except Exception as e:
        logger.error(f"Error generating AI review: {e}")
        return f"Error: {str(e)}"

def post_review_comment(pr_number, sha, file_path, line, comment, github_token, repo_name):
    """Post a review comment on GitHub PR"""
    try:
        url = f"https://api.github.com/repos/{repo_name}/pulls/{pr_number}/comments"
        headers = {
            'Authorization': f'token {github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {
            'body': comment,
            'commit_id': sha,
            'path': file_path,
            'position': line  # Use 'position' instead of 'line' for diff line numbers
        }
        
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 201:
            logger.info(f"✅ Posted comment successfully")
            return True
        else:
            logger.error(f"Failed to post comment: {response.status_code} - {response.text}")
            return False
            
    except Exception as e:
        logger.error(f"Error posting comment: {e}")
        return False

def run_ai_review(pr_number, repo_name):
    """Run AI code review in background thread"""
    try:
        logger.info(f"🤖 Starting AI review for PR #{pr_number} in {repo_name}")
        
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