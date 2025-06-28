#!/usr/bin/env python3
"""
Example Script - Created by Copilot Agent Demo

This file demonstrates real file creation by a Copilot agent.
"""

from datetime import datetime
import json

def main():
    """Example function created by Copilot agent."""
    print("🤖 Hello from Copilot Agent!")
    print(f"📅 Created on: 2025-06-28 15:52:14")
    print(f"📝 Issue that triggered this: #5")
    print("✅ This is a REAL file, not a simulation!")
    print("🔄 This demo will also create a REAL pull request!")
    
    # Load demo config
    try:
        with open("demo_config.json", "r") as f:
            config = json.load(f)
            print(f"📋 Demo type: {config['demo_type']}")
            print(f"🎯 Purpose: {config['purpose']}")
    except FileNotFoundError:
        print("⚠️ demo_config.json not found")

if __name__ == "__main__":
    main()
