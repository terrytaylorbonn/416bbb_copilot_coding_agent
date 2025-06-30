#!/usr/bin/env python3
"""
MINIMAL CODING AGENT - Actually does coding actions
- Receives GitHub events
- Takes real coding actions (creates files, commits, etc.)
"""

import os
import requests
import base64
from flask import Flask, request, jsonify

app = Flask(__name__)
PORT = int(os.getenv('PORT', 10000))

# GitHub API setup
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN', 'your-token-here')
GITHUB_API = "https://api.github.com"

def create_file_on_github(repo_name, file_path, content, message):
    """Create a file directly on GitHub via API"""
    try:
        url = f"{GITHUB_API}/repos/{repo_name}/contents/{file_path}"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        # Encode content to base64
        content_encoded = base64.b64encode(content.encode()).decode()
        
        data = {
            "message": message,
            "content": content_encoded
        }
        
        response = requests.put(url, headers=headers, json=data)
        return response.status_code == 201
        
    except Exception as e:
        print(f"❌ Error creating file: {e}", flush=True)
        return False

def add_comment_to_issue(repo_name, issue_number, comment):
    """Add a comment to a GitHub issue"""
    try:
        url = f"{GITHUB_API}/repos/{repo_name}/issues/{issue_number}/comments"
        headers = {
            'Authorization': f'token {GITHUB_TOKEN}',
            'Accept': 'application/vnd.github.v3+json'
        }
        
        data = {"body": comment}
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 201
        
    except Exception as e:
        print(f"❌ Error adding comment: {e}", flush=True)
        return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "ok", 
        "agent": "minimal coding agent",
        "github_token": "configured" if GITHUB_TOKEN != 'your-token-here' else "missing"
    })

@app.route('/webhook', methods=['POST'])
def webhook():
    # Get event info
    event_type = request.headers.get('X-GitHub-Event', 'unknown')
    data = request.get_json() or {}
    action = data.get('action', 'no-action')
    
    print(f"🤖 Coding Agent received: {event_type} - {action}", flush=True)
    
    # CODING ACTIONS based on events
    if event_type == 'issues' and action == 'opened':
        # When issue is opened, create a response file
        issue = data.get('issue', {})
        repo_name = data.get('repository', {}).get('full_name')
        issue_number = issue.get('number')
        issue_title = issue.get('title', 'Unknown')
        
        print(f"🐛 New issue #{issue_number}: {issue_title}", flush=True)
        
        # Create a response file
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"issue_responses/issue_{issue_number}_{timestamp}.md"
        file_content = f"""# Response to Issue #{issue_number}

**Issue Title:** {issue_title}

**Auto-generated response:**
- Issue received and logged
- Created: {timestamp}
- Status: Under review

## Next Steps
- [ ] Analyze issue requirements
- [ ] Plan implementation
- [ ] Begin development

---
*This file was automatically created by the Minimal Coding Agent*
"""
        
        success = create_file_on_github(
            repo_name, 
            file_name, 
            file_content, 
            f"Auto-response to issue #{issue_number}: {issue_title}"
        )
        
        if success:
            # Also comment on the issue
            comment = f"🤖 **Coding Agent Response**\n\nI've automatically created a tracking file: `{file_name}`\n\nThis issue is now being tracked and will be processed according to our automated workflow."
            add_comment_to_issue(repo_name, issue_number, comment)
            print(f"✅ Created response file and commented on issue #{issue_number}", flush=True)
            return jsonify({"status": "processed", "action": "file_created", "file": file_name})
        else:
            print(f"❌ Failed to create response file for issue #{issue_number}", flush=True)
            return jsonify({"status": "error", "message": "Failed to create file"})
    
    elif event_type == 'pull_request' and action == 'opened':
        # When PR is opened, create a review checklist
        pr = data.get('pull_request', {})
        repo_name = data.get('repository', {}).get('full_name')
        pr_number = pr.get('number')
        pr_title = pr.get('title', 'Unknown')
        
        print(f"🔄 New PR #{pr_number}: {pr_title}", flush=True)
        
        timestamp = __import__('datetime').datetime.now().strftime('%Y%m%d_%H%M%S')
        file_name = f"pr_reviews/pr_{pr_number}_checklist_{timestamp}.md"
        file_content = f"""# PR Review Checklist - #{pr_number}

**PR Title:** {pr_title}

## Automated Review Checklist
- [ ] Code style check
- [ ] Security review
- [ ] Performance analysis
- [ ] Documentation updated
- [ ] Tests included
- [ ] Breaking changes documented

## Review Status
- **Created:** {timestamp}
- **Status:** Pending review
- **Reviewer:** Coding Agent

---
*This checklist was automatically generated by the Minimal Coding Agent*
"""
        
        success = create_file_on_github(
            repo_name,
            file_name,
            file_content,
            f"Auto-generated review checklist for PR #{pr_number}"
        )
        
        if success:
            print(f"✅ Created review checklist for PR #{pr_number}", flush=True)
            return jsonify({"status": "processed", "action": "checklist_created", "file": file_name})
    
    # For other events, just log
    print(f"📡 Event logged: {event_type} - {action}", flush=True)
    return jsonify({"status": "logged", "event": event_type, "action": action})

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        "name": "Minimal Coding Agent",
        "status": "ready to code",
        "capabilities": [
            "Auto-creates response files for new issues",
            "Generates review checklists for PRs", 
            "Comments on issues",
            "Direct GitHub integration"
        ],
        "github_integration": "configured" if GITHUB_TOKEN != 'your-token-here' else "needs_token"
    })

if __name__ == '__main__':
    print(f"🤖 Minimal Coding Agent starting on port {PORT}", flush=True)
    print("Ready to take coding actions on GitHub events!", flush=True)
    app.run(host='0.0.0.0', port=PORT, debug=False)
