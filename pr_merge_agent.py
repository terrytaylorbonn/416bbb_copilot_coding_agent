# pr_merge_agent.py
#!/usr/bin/env python3
"""
PR Merge Agent - REAL Actions Only

This script performs automated pull request merging via GitHub API:
1. Fetches PR details and status
2. Checks merge requirements (reviews, status checks, etc.)
3. Automatically merges the PR if safe
4. Optionally deletes the feature branch after merge

Usage: python pr_merge_agent.py
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
    print("🤖 PR Merge Agent - Setup")
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
        pr_input = input("🔄 Enter Pull Request number to merge (e.g., 10): ").strip()
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
            print(f"🔀 Mergeable: {pr_data.get('mergeable', 'unknown')}")
            return pr_data
        else:
            print(f"❌ Failed to fetch PR: {response.status_code}")
            if response.status_code == 404:
                print("   PR not found. Check the number and try again.")
            return None
            
    except Exception as e:
        print(f"❌ Error fetching PR: {e}")
        return None


def check_pr_reviews(repo_owner, repo_name, pr_number, github_token):
    """Check the review status of the pull request."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/reviews"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    print(f"📋 Checking PR reviews...")
    
    try:
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            reviews = response.json()
            
            if not reviews:
                print("⚠️  No reviews found")
                return {"has_reviews": False, "approved": False, "blocked": False}
            
            # Analyze reviews
            latest_reviews = {}
            for review in reviews:
                reviewer = review['user']['login']
                # Keep only the latest review from each reviewer
                latest_reviews[reviewer] = review
            
            approvals = 0
            rejections = 0
            comments = 0
            
            for reviewer, review in latest_reviews.items():
                state = review['state']
                print(f"   👤 {reviewer}: {state}")
                
                if state == 'APPROVED':
                    approvals += 1
                elif state == 'REQUEST_CHANGES':
                    rejections += 1
                elif state == 'COMMENTED':
                    comments += 1
            
            print(f"📊 Review Summary: {approvals} approvals, {rejections} rejections, {comments} comments")
            
            return {
                "has_reviews": True,
                "approved": approvals > 0 and rejections == 0,
                "blocked": rejections > 0,
                "approvals": approvals,
                "rejections": rejections
            }
        else:
            print(f"❌ Failed to fetch reviews: {response.status_code}")
            return {"has_reviews": False, "approved": False, "blocked": False}
            
    except Exception as e:
        print(f"❌ Error fetching reviews: {e}")
        return {"has_reviews": False, "approved": False, "blocked": False}


def check_status_checks(repo_owner, repo_name, pr_number, github_token):
    """Check the status checks for the pull request."""
    # First get the PR to get the head SHA
    pr_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    print(f"🔍 Checking status checks...")
    
    try:
        pr_response = requests.get(pr_url, headers=headers)
        if pr_response.status_code != 200:
            print("❌ Could not fetch PR for status checks")
            return {"has_checks": False, "all_passed": False}
        
        pr_data = pr_response.json()
        head_sha = pr_data['head']['sha']
        
        # Get status checks
        status_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits/{head_sha}/status"
        status_response = requests.get(status_url, headers=headers)
        
        if status_response.status_code == 200:
            status_data = status_response.json()
            state = status_data.get('state', 'unknown')
            statuses = status_data.get('statuses', [])
            
            print(f"📊 Overall status: {state}")
            
            if statuses:
                for status in statuses:
                    print(f"   ✓ {status['context']}: {status['state']}")
            else:
                print("   No status checks found")
            
            return {
                "has_checks": len(statuses) > 0,
                "all_passed": state == 'success',
                "state": state
            }
        else:
            print("⚠️  No status checks found")
            return {"has_checks": False, "all_passed": True}  # No checks = OK to merge
            
    except Exception as e:
        print(f"❌ Error checking status: {e}")
        return {"has_checks": False, "all_passed": False}


def merge_pull_request(repo_owner, repo_name, pr_number, pr_data, github_token):
    """Merge the pull request via GitHub API."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls/{pr_number}/merge"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    merge_data = {
        "commit_title": f"Merge pull request #{pr_number} from {pr_data['head']['ref']}",
        "commit_message": f"Automated merge by PR Merge Agent\n\n{pr_data['title']}",
        "merge_method": "merge"  # Options: merge, squash, rebase
    }
    
    print(f"\n🔀 Merging pull request #{pr_number}...")
    print(f"📝 Commit title: {merge_data['commit_title']}")
    
    try:
        response = requests.put(url, headers=headers, json=merge_data)
        
        if response.status_code == 200:
            merge_result = response.json()
            print(f"✅ SUCCESS! PR merged successfully!")
            print(f"🔗 Merge commit: {merge_result['sha']}")
            print(f"📝 Message: {merge_result['message']}")
            return True
        else:
            print(f"❌ Failed to merge PR: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error merging PR: {e}")
        return False


def delete_branch(repo_owner, repo_name, branch_name, github_token):
    """Delete the feature branch after successful merge."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/git/refs/heads/{branch_name}"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }
    
    print(f"\n🗑️  Deleting branch: {branch_name}...")
    
    try:
        response = requests.delete(url, headers=headers)
        
        if response.status_code == 204:
            print(f"✅ Branch {branch_name} deleted successfully!")
            return True
        else:
            print(f"❌ Failed to delete branch: {response.status_code}")
            if response.status_code == 422:
                print("   Branch may be protected or already deleted")
            return False
            
    except Exception as e:
        print(f"❌ Error deleting branch: {e}")
        return False


def main():
    """Main function - performs automated PR merge."""
    
    # Load environment variables
    load_env_file()
    
    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ Error: GitHub token not found!")
        print("Please set the GITHUB_TOKEN environment variable or create a .env file")
        return 1
    
    print("🎯 PR Merge Agent - Automated Pull Request Merging")
    print("="*60)
    
    # Get user inputs
    repo_owner, repo_name, pr_number = get_user_inputs()
    
    # Fetch PR details
    pr_data = fetch_pr_details(repo_owner, repo_name, pr_number, github_token)
    if not pr_data:
        print("❌ Cannot proceed without PR data")
        return 1
    
    # Check if PR is open
    if pr_data['state'] != 'open':
        print(f"❌ PR is {pr_data['state']}, not open. Cannot merge.")
        return 1
    
    # Check if PR is mergeable
    if pr_data.get('mergeable') == False:
        print("❌ PR has merge conflicts. Cannot auto-merge.")
        print("   Resolve conflicts manually before merging.")
        return 1
    
    # Check reviews
    review_status = check_pr_reviews(repo_owner, repo_name, pr_number, github_token)
    
    # Check status checks
    status_checks = check_status_checks(repo_owner, repo_name, pr_number, github_token)
    
    # Evaluate merge safety
    print(f"\n📋 Merge Safety Assessment:")
    print(f"   🔍 PR State: {pr_data['state']}")
    print(f"   🔀 Mergeable: {pr_data.get('mergeable', 'unknown')}")
    print(f"   ✅ Reviews: {'✓' if review_status['approved'] else '⚠️'} ({review_status.get('approvals', 0)} approvals)")
    print(f"   🚫 Blocked: {'✓' if not review_status['blocked'] else '❌'}")
    print(f"   🔍 Status Checks: {'✓' if status_checks['all_passed'] else '⚠️'}")
    
    # Determine if safe to merge
    safe_to_merge = (
        pr_data['state'] == 'open' and
        pr_data.get('mergeable') != False and
        not review_status['blocked'] and
        status_checks['all_passed']
    )
    
    if not safe_to_merge:
        print(f"\n⚠️  Merge Safety Check Failed!")
        if review_status['blocked']:
            print("   - PR has requested changes")
        if not status_checks['all_passed']:
            print("   - Status checks are not passing")
        
        proceed = input("\n🤔 Merge anyway? This may not be safe (y/N): ").strip().lower()
        if proceed != 'y':
            print("👋 Merge cancelled for safety")
            return 0
    
    # Ask for final confirmation
    print(f"\n🤔 Ready to merge PR #{pr_number}?")
    print(f"   Title: {pr_data['title']}")
    print(f"   Author: {pr_data['user']['login']}")
    confirm = input("Proceed with merge? (Y/n): ").strip().lower()
    
    if confirm in ['', 'y', 'yes']:
        # Perform the merge
        success = merge_pull_request(repo_owner, repo_name, pr_number, pr_data, github_token)
        
        if success:
            print(f"\n🎉 PR #{pr_number} merged successfully!")
            
            # Ask about deleting the branch
            branch_name = pr_data['head']['ref']
            if branch_name != 'main' and branch_name != 'master':
                delete_branch_confirm = input(f"\n🗑️  Delete feature branch '{branch_name}'? (Y/n): ").strip().lower()
                
                if delete_branch_confirm in ['', 'y', 'yes']:
                    delete_branch(repo_owner, repo_name, branch_name, github_token)
            
            print(f"\n✅ Automated merge completed!")
            print(f"🔗 View repository: https://github.com/{repo_owner}/{repo_name}")
        else:
            print(f"\n❌ Merge failed!")
            return 1
    else:
        print("👋 Merge cancelled")
        return 0
    
    return 0


if __name__ == "__main__":
    exit(main())
