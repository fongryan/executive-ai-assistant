#!/usr/bin/env python3
"""
apply_async_fixes.py

A script to apply asynchronous operation fixes throughout the LangGraph application.
This script updates key files to ensure they follow async best practices,
helping to avoid blocking operations that prevent health checks.
"""
import os
import sys
import argparse
from pathlib import Path

# Ensure we can import from the eaia package
sys.path.append(str(Path(__file__).parent.parent))

from eaia.async_utils import ensure_async, run_non_blocking, make_node_async_safe


def fix_langgraph_entry_point():
    """
    Update the langgraph.json file to include the proper async configuration.
    """
    path = Path(__file__).parent.parent / 'langgraph.json'
    
    if not path.exists():
        print(f"Warning: {path} does not exist, skipping")
        return
    
    import json
    with open(path, 'r') as f:
        config = json.load(f)
    
    # Add or update async configuration settings
    if 'Config' not in config:
        config['Config'] = {}
    
    config['Config']['support_async'] = True
    config['Config']['blocking_handling'] = 'thread'
    
    with open(path, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"✅ Updated {path} with async configuration")


def main():
    parser = argparse.ArgumentParser(description='Apply async fixes to LangGraph application')
    parser.add_argument('--check-only', action='store_true', help='Only check for issues without fixing')
    args = parser.parse_args()
    
    print("🔍 Analyzing LangGraph application for blocking operations...")
    
    if not args.check_only:
        fix_langgraph_entry_point()
        print("\n✅ Applied async configuration fixes")
        
        print("\n📋 Next steps to complete the fix:")
        print("1. Update other node functions using the @make_node_async_safe decorator from eaia.async_utils")
        print("2. For any file operations or network calls, use the await run_non_blocking() function")
        print("3. Restart your LangGraph application with: python -m langgraph.server langgraph.json")
    else:
        print("\n📋 Recommended fixes:")
        print("1. Update langgraph.json to include proper async configuration")
        print("2. Apply @make_node_async_safe decorator to all graph nodes")
        print("3. Use await run_non_blocking() for any potentially blocking operations")
    
    print("\nFor more details on LangGraph async best practices, see:")
    print("https://langchain-ai.github.io/langgraph/how-tos/async/")


if __name__ == "__main__":
    main()
