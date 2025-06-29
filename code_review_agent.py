# code_review_agent.py
#!/usr/bin/env python3
"""
Code Review Agent - REAL Actions Only

This script performs automated code review on GitHub pull requests:
1. Fetches PR details and diff
2. Analyzes code changes
3. Posts review comments via GitHub API

Usage: python code_review_agent.py
"""

import requests
import json
import os
import sys
from datetime import datetime
from pathlib import Path


def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path(".env")
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key.strip()] = value.strip()


def get_user_inputs():
    """Prompt user for required inputs."""
    print("🤖 Code Review Agent - Setup")
    print("="*50)
    
    # Get repository info
    repo_owner = input("📁 Enter repository owner (e.g., terrytaylorbonn): ").strip()
    if not repo_owner:
        repo_owner = "terrytaylorbonn"  # Default
        print(f"   Using default: {repo_owner}")
    
    repo_name = input("📁 Enter repository name (e.g., 416bbb_copilot_coding_agent): ").strip()
    if not repo_name:
        repo_name = "416bbb_copilot_coding_agent"  # Default
        print(f"   Using default: {repo_name}")
    
    # Get PR number
    while True:
        pr_input = input("🔄 Enter Pull Request number (e.g., 8): ").strip()
        try:
            pr_number = int(pr_input)
            break
        except ValueError:
            print("❌ Please enter a valid number")
    
    return repo_owner, repo_name, pr_number


def fetch_pr_details(repo_owner, repo_name, pr_number, github_token):
    """Fetch pull request details from GitHub API."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    print(f"\n📥 Fetching PR #{pr_number} details...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            pr_data = response.json()
            print(f"✅ Found PR: {pr_data['title']}")
            print(f"📝 Author: {pr_data['user']['login']}")
            print(f"🌿 Branch: {pr_data['head']['ref']} → {pr_data['base']['ref']}")
            print(f"📊 Status: {pr_data['state']}")
            return pr_data
        else:
            print(f"❌ Failed to fetch PR: {response.status_code}")
            if response.status_code == 404:
                print("   PR not found. Check the number and try again.")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching PR: {e}")
        return None


def fetch_pr_files(repo_owner, repo_name, pr_number, github_token):
    """Fetch the files changed in the pull request."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/files"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    print(f"📁 Fetching changed files...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            files_data = response.json()
            print(f"✅ Found {len(files_data)} changed files")
            
            for file_data in files_data:
                print(f"   📄 {file_data['filename']} (+{file_data['additions']} -{file_data['deletions']})")
            
            return files_data
        else:
            print(f"❌ Failed to fetch files: {response.status_code}")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching files: {e}")
        return None


def analyze_code_changes(files_data):
    """Analyze code changes and generate review comments."""
    print(f"\n🔍 Analyzing code changes...")
    
    review_comments = []
    
    for file_data in files_data:
        filename = file_data['filename']
        patch = file_data.get('patch', '')
        additions = file_data['additions']
        deletions = file_data['deletions']
        
        print(f"   🔍 Reviewing {filename}...")
        
        # Basic code review checks
        issues = []
        
        # Check for large files
        if additions > 100:
            issues.append("Large number of additions - consider breaking into smaller changes")
        
        # Check file types and common issues
        if filename.endswith('.py'):
            # Python-specific checks
            if 'print(' in patch:
                issues.append("Consider using logging instead of print statements for production code")
            
            if 'TODO' in patch or 'FIXME' in patch:
                issues.append("TODO/FIXME comments found - ensure these are addressed")
            
            if 'import *' in patch:
                issues.append("Avoid wildcard imports - use specific imports instead")
        
        elif filename.endswith('.js') or filename.endswith('.ts'):
            # JavaScript/TypeScript checks
            if 'console.log' in patch:
                issues.append("Remove console.log statements before production")
            
            if 'var ' in patch:
                issues.append("Consider using 'let' or 'const' instead of 'var'")
        
        elif filename.endswith('.md'):
            # Markdown checks
            if len(patch.split('\n')) > 50:
                issues.append("Large documentation change - ensure it's well structured")
        
        # Check for potential security issues
        if 'password' in patch.lower() or 'secret' in patch.lower() or 'token' in patch.lower():
            issues.append("⚠️ SECURITY: Potential sensitive information detected - ensure no hardcoded secrets")
        
        # Add comments for this file
        if issues:
            for issue in issues:
                review_comments.append({
                    'filename': filename,
                    'comment': f"🤖 **Automated Review**: {issue}",
                    'line': None  # General comment
                })
        else:
            review_comments.append({
                'filename': filename,
                'comment': f"🤖 **Automated Review**: Code looks good! No issues detected.",
                'line': None
            })
    
    return review_comments


def post_review_comments(repo_owner, repo_name, pr_number, review_comments, github_token):
    """Post review comments to the GitHub PR."""
    if not review_comments:
        print("📝 No review comments to post")
        return True
    
    # Create a review with comments
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    # Prepare review body
    review_body = f"""## 🤖 Automated Code Review
    
**Review completed at**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

**Summary**: Analyzed {len(set(c['filename'] for c in review_comments))} files with automated checks.

### 📋 Review Comments:
"""
    
    for comment in review_comments:
        review_body += f"\n**{comment['filename']}**: {comment['comment']}\n"
    
    review_body += """
---
*This review was automatically generated by the Code Review Agent.*
*Please review the suggestions and make changes as needed.*
"""
    
    review_data = {
        "body": review_body,
        "event": "COMMENT"  # APPROVE, REQUEST_CHANGES, or COMMENT
    }
    
    print(f"\n📝 Posting automated review...")
    
    try:
        response = requests.post(url, headers=headers, json=review_data)
        
        if response.status_code == 200:
            review = response.json()
            print(f"✅ Review posted successfully!")
            print(f"🔗 Review URL: {review['html_url']}")
            return True
        else:
            print(f"❌ Failed to post review: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error posting review: {e}")
        return False


def main():
    """Main function - performs automated code review."""
    
    # Load environment variables
    load_env_file()
    
    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ Error: GitHub token not found!")
        print("Please set the GITHUB_TOKEN environment variable or create a .env file")
        return 1
    
    print("🎯 Code Review Agent - Automated PR Review")
    print("="*60)
    
    # Get user inputs
    repo_owner, repo_name, pr_number = get_user_inputs()
    
    # Fetch PR details
    pr_data = fetch_pr_details(repo_owner, repo_name, pr_number, github_token)
    if not pr_data:
        print("❌ Cannot proceed without PR data")
        return 1
    
    # Check if PR is in reviewable state
    if pr_data['state'] != 'open':
        print(f"⚠️ Warning: PR is {pr_data['state']}, not open")
        proceed = input("Continue anyway? (y/N): ").strip().lower()
        if proceed != 'y':
            print("👋 Review cancelled")
            return 0
    
    # Fetch changed files
    files_data = fetch_pr_files(repo_owner, repo_name, pr_number, github_token)
    if not files_data:
        print("❌ Cannot proceed without file data")
        return 1
    
    # Analyze code changes
    review_comments = analyze_code_changes(files_data)
    
    # Show preview of comments
    print(f"\n📋 Review Summary:")
    print(f"   Files analyzed: {len(set(c['filename'] for c in review_comments))}")
    print(f"   Comments generated: {len(review_comments)}")
    
    # Ask for confirmation
    print(f"\n🤔 Ready to post automated review to PR #{pr_number}?")
    confirm = input("Post review? (Y/n): ").strip().lower()
    
    if confirm in ['', 'y', 'yes']:
        # Post review comments
        success = post_review_comments(repo_owner, repo_name, pr_number, review_comments, github_token)
        
        if success:
            print(f"\n🎉 Code review completed successfully!")
            print(f"✅ Review posted to PR #{pr_number}")
            print(f"🔗 View at: https://github.com/{repo_owner}/{repo_name}/pull/{pr_number}")
        else:
            print(f"\n❌ Code review failed!")
            return 1
    else:
        print("👋 Review cancelled")
        return 0
    
    return 0


if __name__ == "__main__":
    exit(main())
