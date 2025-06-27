#!/usr/bin/env python3
"""
Git Repository Analyzer - A Copilot Coding Agent Demo

This script demonstrates various capabilities of a coding agent:
- Code generation and structure
- Error handling and validation
- Documentation and type hints
- Command-line interface
- File system operations
"""

import os
import subprocess
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime
import argparse


@dataclass
class GitStats:
    """Data class to hold Git repository statistics."""
    total_commits: int
    total_files: int
    total_lines: int
    contributors: List[str]
    last_commit_date: str
    repository_size: str


class GitAnalyzer:
    """
    A simple Git repository analyzer that demonstrates coding agent capabilities.
    
    This class shows how a coding agent can:
    - Design clean, maintainable code structure
    - Implement proper error handling
    - Add comprehensive documentation
    - Use modern Python features
    """
    
    def __init__(self, repo_path: str):
        """
        Initialize the Git analyzer.
        
        Args:
            repo_path: Path to the Git repository to analyze
            
        Raises:
            ValueError: If the path is not a valid Git repository
        """
        self.repo_path = Path(repo_path).resolve()
        self._validate_git_repo()
    
    def _validate_git_repo(self) -> None:
        """Validate that the given path is a Git repository."""
        if not self.repo_path.exists():
            raise ValueError(f"Path does not exist: {self.repo_path}")
        
        git_dir = self.repo_path / ".git"
        if not git_dir.exists():
            raise ValueError(f"Not a Git repository: {self.repo_path}")
    
    def _run_git_command(self, command: List[str]) -> str:
        """
        Execute a Git command and return the output.
        
        Args:
            command: List of command parts (e.g., ['log', '--oneline'])
            
        Returns:
            Command output as string
            
        Raises:
            subprocess.CalledProcessError: If the Git command fails
        """
        full_command = ["git"] + command
        try:
            result = subprocess.run(
                full_command,
                cwd=self.repo_path,
                capture_output=True,
                text=True,
                check=True
            )
            return result.stdout.strip()
        except subprocess.CalledProcessError as e:
            raise subprocess.CalledProcessError(
                e.returncode, 
                e.cmd, 
                f"Git command failed: {e.stderr}"
            )
    
    def get_commit_count(self) -> int:
        """Get the total number of commits in the repository."""
        try:
            output = self._run_git_command(["rev-list", "--count", "HEAD"])
            return int(output)
        except (subprocess.CalledProcessError, ValueError):
            return 0
    
    def get_file_count(self) -> int:
        """Get the total number of tracked files."""
        try:
            output = self._run_git_command(["ls-files"])
            return len(output.split('\n')) if output else 0
        except subprocess.CalledProcessError:
            return 0
    
    def get_line_count(self) -> int:
        """Get the total number of lines in all tracked files."""
        try:
            files_output = self._run_git_command(["ls-files"])
            if not files_output:
                return 0
            
            total_lines = 0
            for file_path in files_output.split('\n'):
                full_path = self.repo_path / file_path
                if full_path.exists() and full_path.is_file():
                    try:
                        with open(full_path, 'r', encoding='utf-8', errors='ignore') as f:
                            total_lines += sum(1 for _ in f)
                    except (OSError, UnicodeDecodeError):
                        # Skip files that can't be read
                        continue
            
            return total_lines
        except subprocess.CalledProcessError:
            return 0
    
    def get_contributors(self) -> List[str]:
        """Get a list of unique contributors to the repository."""
        try:
            output = self._run_git_command(["shortlog", "-sn", "--all"])
            contributors = []
            for line in output.split('\n'):
                if line.strip():
                    # Format is "count\tname", we want just the name
                    parts = line.strip().split('\t', 1)
                    if len(parts) == 2:
                        contributors.append(parts[1])
            return contributors
        except subprocess.CalledProcessError:
            return []
    
    def get_last_commit_date(self) -> str:
        """Get the date of the last commit."""
        try:
            output = self._run_git_command(["log", "-1", "--format=%ci"])
            return output
        except subprocess.CalledProcessError:
            return "Unknown"
    
    def get_repository_size(self) -> str:
        """Get the size of the repository directory."""
        try:
            total_size = 0
            for dirpath, dirnames, filenames in os.walk(self.repo_path):
                for filename in filenames:
                    filepath = os.path.join(dirpath, filename)
                    if os.path.exists(filepath):
                        total_size += os.path.getsize(filepath)
            
            # Convert to human-readable format
            for unit in ['B', 'KB', 'MB', 'GB']:
                if total_size < 1024.0:
                    return f"{total_size:.1f} {unit}"
                total_size /= 1024.0
            return f"{total_size:.1f} TB"
        except OSError:
            return "Unknown"
    
    def analyze(self) -> GitStats:
        """
        Perform a complete analysis of the Git repository.
        
        Returns:
            GitStats object containing all repository statistics
        """
        print(f"🔍 Analyzing repository: {self.repo_path}")
        
        stats = GitStats(
            total_commits=self.get_commit_count(),
            total_files=self.get_file_count(),
            total_lines=self.get_line_count(),
            contributors=self.get_contributors(),
            last_commit_date=self.get_last_commit_date(),
            repository_size=self.get_repository_size()
        )
        
        return stats
    
    def print_report(self, stats: GitStats) -> None:
        """Print a formatted report of the repository statistics."""
        print("\n" + "="*50)
        print("📊 GIT REPOSITORY ANALYSIS REPORT")
        print("="*50)
        print(f"📁 Repository Path: {self.repo_path}")
        print(f"📈 Total Commits: {stats.total_commits:,}")
        print(f"📄 Total Files: {stats.total_files:,}")
        print(f"📝 Total Lines: {stats.total_lines:,}")
        print(f"💾 Repository Size: {stats.repository_size}")
        print(f"📅 Last Commit: {stats.last_commit_date}")
        print(f"\n👥 Contributors ({len(stats.contributors)}):")
        
        for i, contributor in enumerate(stats.contributors[:10], 1):
            print(f"   {i}. {contributor}")
        
        if len(stats.contributors) > 10:
            print(f"   ... and {len(stats.contributors) - 10} more")
        
        print("="*50)
    
    def export_json(self, stats: GitStats, output_file: str) -> None:
        """Export the analysis results to a JSON file."""
        data = {
            "repository_path": str(self.repo_path),
            "analysis_date": datetime.now().isoformat(),
            "statistics": {
                "total_commits": stats.total_commits,
                "total_files": stats.total_files,
                "total_lines": stats.total_lines,
                "repository_size": stats.repository_size,
                "last_commit_date": stats.last_commit_date,
                "contributors": stats.contributors
            }
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"📄 Analysis exported to: {output_file}")


def main():
    """
    Main function demonstrating command-line interface capabilities.
    
    This shows how a coding agent can create user-friendly CLI tools.
    """
    parser = argparse.ArgumentParser(
        description="Analyze a Git repository and generate statistics",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python git.py .                           # Analyze current directory
  python git.py /path/to/repo               # Analyze specific repository
  python git.py . --export stats.json      # Export results to JSON
        """
    )
    
    parser.add_argument(
        "repository",
        nargs="?",
        default=".",
        help="Path to the Git repository (default: current directory)"
    )
    
    parser.add_argument(
        "--export",
        metavar="FILE",
        help="Export analysis results to JSON file"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="Git Analyzer Demo 1.0 - Copilot Coding Agent Showcase"
    )
    
    args = parser.parse_args()
    
    try:
        # Create analyzer and perform analysis
        analyzer = GitAnalyzer(args.repository)
        stats = analyzer.analyze()
        
        # Display results
        analyzer.print_report(stats)
        
        # Export if requested
        if args.export:
            analyzer.export_json(stats, args.export)
        
        print("\n✅ Analysis complete!")
        
    except ValueError as e:
        print(f"❌ Error: {e}")
        return 1
    except subprocess.CalledProcessError as e:
        print(f"❌ Git command failed: {e}")
        return 1
    except KeyboardInterrupt:
        print("\n⚠️  Analysis interrupted by user")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())