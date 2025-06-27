# simple_demo.py
#!/usr/bin/env python3
"""
Simple GitHub Issue Creator - REAL Actions Only

This script creates a REAL GitHub issue in your repository.
No simulations, just one simple action.
"""

import requests
import json
import os
from datetime import datetime


def create_github_issue(repo_owner, repo_name, github_token, title, description):
    """Create a real GitHub issue using the GitHub API."""
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    issue_data = {
        "title": title,
        "body": description,
        "labels": ["enhancement", "copilot-test"]
    }
    
    print(f"🚀 Creating real GitHub issue...")
    print(f"📁 Repository: {repo_owner}/{repo_name}")
    print(f"📝 Title: {title}")
    
    try:
        response = requests.post(url, headers=headers, json=issue_data)
        
        if response.status_code == 201:
            issue = response.json()
            print(f"✅ SUCCESS! Issue created!")
            print(f"🔗 Issue #{issue['number']}: {issue['html_url']}")
            print(f"📅 Created at: {issue['created_at']}")
            return issue
        else:
            print(f"❌ Failed to create issue: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating issue: {e}")
        return None


def main():
    """Main function - creates a real GitHub issue."""
    
    # Configuration
    repo_owner = "terrytaylorbonn"
    repo_name = "416bbb_copilot_coding_agent"
    
    # Get GitHub token from environment variable
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ Error: GitHub token not found!")
        print("Please set your GitHub token:")
        print("1. Go to GitHub Settings > Developer settings > Personal access tokens")
        print("2. Create a token with 'repo' permissions")
        print("3. Set environment variable: set GITHUB_TOKEN=your_token_here")
        print("4. Or run: python simple_demo.py YOUR_TOKEN_HERE")
        return 1
    
    # Issue content
    title = f"Test Issue - Created by Script on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    
    description = """## 🤖 Test Issue Created by Real Script

This is a **REAL** GitHub issue created by a simple Python script.

### Purpose
- Test GitHub API integration
- Demonstrate real issue creation (no simulation)
- Verify script functionality

### What to do
- ✅ This issue was created successfully
- 🔍 Check that it appears in the Issues tab
- 📝 You can comment on this issue
- 🗑️ You can close this issue when done testing

---
*Created by simple_demo.py script*
"""
    
    print("🎯 Simple GitHub Issue Creator Demo")
    print("="*50)
    
    # Create the issue
    issue = create_github_issue(repo_owner, repo_name, github_token, title, description)
    
    if issue:
        print("\n🎉 Demo completed successfully!")
        print(f"📋 Go check your repository: https://github.com/{repo_owner}/{repo_name}/issues")
    else:
        print("\n❌ Demo failed!")
        return 1
    
    return 0


if __name__ == "__main__":
    import sys
    
    # Allow token to be passed as command line argument
    if len(sys.argv) > 1:
        os.environ['GITHUB_TOKEN'] = sys.argv[1]
    
    exit(main())
