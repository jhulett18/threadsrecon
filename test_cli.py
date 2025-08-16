#!/usr/bin/env python3
"""
Quick test to verify CLI functionality without dependencies
"""

import argparse
import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_cli_parser():
    """Test the argument parser functionality"""
    
    # Import the parser creation function from main
    try:
        from main import create_parser
        
        parser = create_parser()
        
        # Test help output
        print("🧪 Testing CLI Help Output:")
        print("=" * 50)
        
        # Capture help output
        try:
            parser.parse_args(['--help'])
        except SystemExit:
            pass  # Help always exits
            
        # Test parsing valid arguments
        print("\n🧪 Testing Argument Parsing:")
        print("=" * 40)
        
        test_cases = [
            ['scrape', '-u', 'user1', 'user2'],
            ['all', '--headless', '--timeout', '30'],
            ['analyze', '--keywords', 'crypto', 'bitcoin'],
            ['report', '--output-dir', '/tmp/test']
        ]
        
        for i, test_args in enumerate(test_cases, 1):
            try:
                args = parser.parse_args(test_args)
                print(f"✅ Test {i}: {' '.join(test_args)}")
                print(f"   Parsed: command={args.command}")
                if hasattr(args, 'usernames') and args.usernames:
                    print(f"           usernames={args.usernames}")
                if hasattr(args, 'headless') and args.headless:
                    print(f"           headless={args.headless}")
                if hasattr(args, 'timeout') and args.timeout:
                    print(f"           timeout={args.timeout}")
                if hasattr(args, 'keywords') and args.keywords:
                    print(f"           keywords={args.keywords}")
                if hasattr(args, 'output_dir') and args.output_dir:
                    print(f"           output_dir={args.output_dir}")
            except Exception as e:
                print(f"❌ Test {i} failed: {e}")
        
        print("\n🎉 CLI Parser Test Complete!")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False

if __name__ == "__main__":
    success = test_cli_parser()
    sys.exit(0 if success else 1)