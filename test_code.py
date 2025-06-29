#!/usr/bin/env python3
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
    print(f"Current time: {datetime.now()}")  # Another print statement
    
    # FIXME: Handle error cases properly
    password = "secret123"  # Should flag security issue
    api_token = "abc123xyz"  # Should flag security issue
    
    print("Test completed!")  # Another print statement
    
    # TODO: Add proper error handling
    return 0

if __name__ == "__main__":
    main()
