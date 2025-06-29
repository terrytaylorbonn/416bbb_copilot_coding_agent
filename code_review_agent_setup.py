# code_review_agent_setup.py
#!/usr/bin/env python3
"""
Code Review Agent Setup - REAL Actions Only

This script sets up what you need to test the code_review_agent.py:
1. Creates a GitHub issue requesting a code review test
2. Creates a branch with sample code that has review issues
3. Creates a pull request for the code review agent to analyze

Usage: python code_review_agent_setup.py
"""

import requests
import json
import os
import subprocess
import tempfile
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
    print("🤖 Code Review Agent Setup")
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
    
    return repo_owner, repo_name


def create_github_issue(repo_owner, repo_name, github_token):
    """Create a GitHub issue requesting code review test."""
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/issues"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    title = f"Code Review Test - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    description = """## 🤖 Code Review Agent Test Setup

This issue was created to set up a test for the automated code review agent.

### What will be created:
1. ✅ This GitHub issue
2. ✅ Sample code files with intentional review issues
3. ✅ Pull request for the code review agent to analyze

### Files to be created:
- `test_code.py` - Python script with review issues (print statements, TODO comments)
- `sample_script.js` - JavaScript with console.log and var usage
- `test_docs.md` - Large documentation file

### Purpose:
Test the automated code review functionality by creating code that will trigger various review comments.

---
*This issue was created by code_review_agent_setup.py*
"""
    
    issue_data = {
        "title": title,
        "body": description,
        "labels": ["enhancement", "code-review-test"]
    }
    
    print(f"\n🚀 Creating GitHub issue for code review test...")
    print(f"📁 Repository: {repo_owner}/{repo_name}")
    print(f"📝 Title: {title}")
    
    try:
        response = requests.post(url, headers=headers, json=issue_data)
        
        if response.status_code == 201:
            issue = response.json()
            print(f"✅ SUCCESS! Issue #{issue['number']} created!")
            print(f"🔗 URL: {issue['html_url']}")
            return issue
        else:
            print(f"❌ Failed to create issue: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating issue: {e}")
        return None


def create_test_files_and_branch(repo_owner, repo_name, github_token, issue_number):
    """Create branch with test files that have review issues."""
    
    repo_url = f"https://{github_token}@github.com/{repo_owner}/{repo_name}.git"
    temp_dir = Path(tempfile.mkdtemp())
    repo_path = temp_dir / repo_name
    
    print(f"\n🔄 Creating test files with intentional review issues...")
    
    try:
        # Clone the repository
        print(f"📥 Cloning repository to {repo_path}...")
        result = subprocess.run(
            ["git", "clone", repo_url, str(repo_path)],
            capture_output=True,
            text=True,
            check=True
        )
        print("✅ Repository cloned successfully!")
        
        # Change to repo directory
        original_cwd = os.getcwd()
        os.chdir(repo_path)
        
        # Create branch
        branch_name = f"code-review-test-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        subprocess.run(["git", "checkout", "-b", branch_name], check=True, capture_output=True)
        print(f"✅ Created branch: {branch_name}")
        
        # Create test_code.py with review issues
        test_code_content = f'''#!/usr/bin/env python3
"""
Test Code - Created for Code Review Agent Testing

This file intentionally contains issues that should be caught by code review.
"""

from datetime import datetime
import os
from pathlib import *  # Wildcard import - should be flagged

def main():
    """Main function with review issues."""
    # TODO: This function needs refactoring
    print("Starting test code execution...")  # Should suggest logging
    print(f"Current time: {{datetime.now()}}")  # Another print statement
    
    # FIXME: Handle error cases properly
    password = "secret123"  # Should flag security issue
    api_token = "abc123xyz"  # Should flag security issue
    
    print("Test completed!")  # Another print statement
    
    # TODO: Add proper error handling
    return 0

if __name__ == "__main__":
    main()
'''
        
        with open("test_code.py", "w", encoding="utf-8") as f:
            f.write(test_code_content)
        print("✅ Created test_code.py (with review issues)")
        
        # Create sample_script.js with review issues
        js_content = f'''// Sample JavaScript - Created for Code Review Agent Testing
// This file intentionally contains issues for review testing

var globalVar = "should use let or const";  // Should flag var usage
var anotherVar = "more var usage";

function testFunction() {{
    console.log("Debug message 1");  // Should flag console.log
    console.log("Debug message 2");  // Another console.log
    
    var localVar = "local variable";  // More var usage
    console.log("Local var:", localVar);  // More console.log
    
    return "test complete";
}}

// Call the function
testFunction();
console.log("Script finished");  // Final console.log
'''
        
        with open("sample_script.js", "w", encoding="utf-8") as f:
            f.write(js_content)
        print("✅ Created sample_script.js (with review issues)")
        
        # Create large test_docs.md
        large_doc_lines = []
        large_doc_lines.append("# Large Test Documentation\\n")
        large_doc_lines.append("## Overview\\n")
        large_doc_lines.append("This is a large documentation file created for testing code review.\\n")
        
        for i in range(60):  # Create 60+ lines to trigger large file warning
            large_doc_lines.append(f"### Section {i+1}\\n")
            large_doc_lines.append(f"This is section {i+1} with some content about testing.\\n")
            large_doc_lines.append(f"More details for section {i+1}.\\n")
            large_doc_lines.append("\\n")
        
        large_doc_content = "\\n".join(large_doc_lines)
        
        with open("test_docs.md", "w", encoding="utf-8") as f:
            f.write(large_doc_content)
        print("✅ Created test_docs.md (large documentation file)")
        
        # Create test config with review info
        test_config = {
            "test_type": "code_review_agent_test",
            "purpose": "Test automated code review functionality",
            "issue_number": issue_number,
            "branch": branch_name,
            "timestamp": datetime.now().isoformat(),
            "expected_issues": [
                "Python print statements",
                "TODO/FIXME comments",
                "Wildcard imports",
                "JavaScript console.log statements",
                "JavaScript var usage",
                "Security concerns (hardcoded secrets)",
                "Large documentation file"
            ]
        }
        
        with open("test_config.json", "w", encoding="utf-8") as f:
            json.dump(test_config, f, indent=2)
        print("✅ Created test_config.json")
        
        # Add files to git
        subprocess.run(["git", "add", "."], check=True, capture_output=True)
        print("✅ Added files to git")
        
        # Commit files
        commit_message = f"🧪 Add test files for code review agent - Issue #{issue_number}"
        subprocess.run(["git", "commit", "-m", commit_message], check=True, capture_output=True)
        print("✅ Created git commit")
        
        # Push to GitHub
        subprocess.run(["git", "push", "-u", "origin", branch_name], check=True, capture_output=True)
        print("✅ Pushed branch to GitHub")
        
        print(f"\\n🎉 Test files created successfully!")
        print(f"🌿 Branch: {branch_name}")
        print(f"📁 Files: test_code.py, sample_script.js, test_docs.md, test_config.json")
        
        return branch_name
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        return None
    except Exception as e:
        print(f"❌ Error creating files: {e}")
        return None
    finally:
        os.chdir(original_cwd)


def create_pull_request(repo_owner, repo_name, github_token, branch_name, issue_number):
    """Create a pull request for code review testing."""
    
    url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/pulls"
    
    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json"
    }
    
    pr_title = f"🧪 Code Review Test Files - Issue #{issue_number}"
    pr_body = f"""## 🤖 Code Review Agent Test

This pull request was created to test the automated code review agent functionality.

### What's included:
- ✅ `test_code.py` - Python with intentional review issues
- ✅ `sample_script.js` - JavaScript with review issues  
- ✅ `test_docs.md` - Large documentation file
- ✅ `test_config.json` - Test configuration

### Expected Review Issues:
1. **Python Issues**:
   - Print statements (should suggest logging)
   - TODO/FIXME comments
   - Wildcard imports
   - Hardcoded secrets

2. **JavaScript Issues**:
   - console.log statements
   - var usage (should suggest let/const)

3. **Documentation Issues**:
   - Large file size

### Related Issue
Closes #{issue_number}

### Testing Instructions:
1. Run `python code_review_agent.py`
2. Enter this PR number when prompted
3. Review the automated comments generated

---
*This PR was automatically generated by code_review_agent_setup.py*
"""
    
    pr_data = {
        "title": pr_title,
        "body": pr_body,
        "head": branch_name,
        "base": "main",
        "draft": False
    }
    
    print(f"\\n🔄 Creating pull request for testing...")
    print(f"📝 Title: {pr_title}")
    print(f"🌿 From branch: {branch_name}")
    print(f"🎯 To branch: main")
    
    try:
        response = requests.post(url, headers=headers, json=pr_data)
        
        if response.status_code == 201:
            pr = response.json()
            print(f"✅ SUCCESS! Pull Request #{pr['number']} created!")
            print(f"🔗 URL: {pr['html_url']}")
            return pr
        else:
            print(f"❌ Failed to create pull request: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"❌ Error creating pull request: {e}")
        return None


def main():
    """Main function - sets up code review test environment."""
    
    # Load environment variables
    load_env_file()
    
    # Get GitHub token
    github_token = os.getenv('GITHUB_TOKEN')
    
    if not github_token:
        print("❌ Error: GitHub token not found!")
        print("Please set the GITHUB_TOKEN environment variable or create a .env file")
        return 1
    
    print("🎯 Code Review Agent Setup")
    print("="*60)
    
    # Get user inputs
    repo_owner, repo_name = get_user_inputs()
    
    # Step 1: Create issue
    issue = create_github_issue(repo_owner, repo_name, github_token)
    if not issue:
        print("❌ Failed to create issue. Stopping.")
        return 1
    
    # Step 2: Create test files and branch
    branch_name = create_test_files_and_branch(repo_owner, repo_name, github_token, issue['number'])
    if not branch_name:
        print("\\n❌ Setup failed during file creation!")
        return 1
    
    # Step 3: Create pull request
    pr = create_pull_request(repo_owner, repo_name, github_token, branch_name, issue['number'])
    
    if pr:
        print(f"\\n🎉 Code Review Test Setup completed successfully!")
        print(f"✅ Issue #{issue['number']}: {issue['html_url']}")
        print(f"✅ Branch created: {branch_name}")
        print(f"✅ Pull Request #{pr['number']}: {pr['html_url']}")
        print(f"\\n📋 Next Steps:")
        print(f"   1. Run: python code_review_agent.py")
        print(f"   2. Enter PR number: {pr['number']}")
        print(f"   3. Watch the automated code review in action!")
    else:
        print("\\n❌ Setup failed during pull request creation!")
        print(f"✅ But issue and files were created successfully:")
        print(f"   Issue #{issue['number']}: {issue['html_url']}")
        print(f"   Branch: {branch_name}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
