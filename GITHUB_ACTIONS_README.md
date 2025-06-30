# GitHub Actions Demos 🚀

This repository contains simple GitHub Actions workflow examples to demonstrate CI/CD automation.

## Workflows Created

### 1. **Hello World** (`.github/workflows/hello-world.yml`)
- **Trigger**: Push or PR to main/master
- **Purpose**: Simplest possible action
- **What it does**: Prints hello message, shows date and environment variables

### 2. **Python Tests** (`.github/workflows/python-test.yml`)
- **Trigger**: Push or PR to main/master  
- **Purpose**: Test Python code across multiple versions
- **What it does**: Tests Python 3.8-3.11, installs dependencies, runs test files

### 3. **Code Quality** (`.github/workflows/code-quality.yml`)
- **Trigger**: Push or PR to main/master
- **Purpose**: Check code formatting and linting
- **What it does**: Runs Black, isort, and flake8 on Python files

### 4. **Manual Trigger** (`.github/workflows/manual-trigger.yml`)
- **Trigger**: Manual dispatch only (from GitHub Actions tab)
- **Purpose**: Show workflow inputs and manual triggering
- **What it does**: Takes custom inputs and simulates deployment

### 5. **Scheduled Health Check** (`.github/workflows/scheduled-health.yml`)
- **Trigger**: Daily at 9 AM UTC (cron: `0 9 * * *`)
- **Purpose**: Daily automated repository health check
- **What it does**: Reports repo stats, checks files, shows system info

### 6. **Auto Comment** (`.github/workflows/auto-comment.yml`)
- **Trigger**: New issues or pull requests
- **Purpose**: Automatically comment on new issues/PRs
- **What it does**: Posts welcome messages using GitHub API

## How to Use

### To Test Locally:
1. Run the test file: `python test_simple.py`
2. Check code quality: `flake8 *.py` (install with `pip install flake8`)

### To Use on GitHub:
1. **Push to GitHub**: All workflows will be automatically available
2. **View Actions**: Go to your repository → "Actions" tab
3. **Manual Trigger**: Go to Actions → "Manual Demo" → "Run workflow"
4. **Monitor**: Watch workflows run in real-time

## Workflow Triggers

| Trigger Type | Example | When It Runs |
|--------------|---------|--------------|
| `push` | `on: push` | Every commit push |
| `pull_request` | `on: pull_request` | PR opened/updated |
| `workflow_dispatch` | Manual only | From Actions tab |
| `schedule` | `cron: '0 9 * * *'` | Daily at 9 AM UTC |
| `issues` | `types: [opened]` | New issue created |

## Key Concepts Demonstrated

- ✅ **Basic workflow structure** (name, on, jobs, steps)
- ✅ **Multiple trigger types** (push, PR, manual, schedule, issues)
- ✅ **Matrix builds** (testing multiple Python versions)
- ✅ **Using actions** (`actions/checkout`, `actions/setup-python`)
- ✅ **Environment variables** (`$GITHUB_ACTOR`, `$RUNNER_OS`)
- ✅ **Conditional execution** (`if` statements)
- ✅ **GitHub API integration** (commenting via `actions/github-script`)
- ✅ **Workflow inputs** (custom parameters for manual triggers)

## Next Steps

1. **Enable Actions**: Push this to GitHub to see workflows in action
2. **Create Issues/PRs**: Test the auto-comment workflow
3. **Manual Triggers**: Try the manual workflow with different inputs
4. **Scheduled**: Wait for or manually trigger the daily health check
5. **Customize**: Modify workflows for your specific needs

## Useful Commands

```bash
# Test the simple Python file
python test_simple.py

# Check code quality locally
pip install flake8 black isort
flake8 *.py
black --check *.py
isort --check-only *.py
```

## Resources

- [GitHub Actions Documentation](https://docs.github.com/en/actions)
- [Workflow Syntax](https://docs.github.com/en/actions/using-workflows/workflow-syntax-for-github-actions)
- [Marketplace](https://github.com/marketplace?type=actions) - Pre-built actions
