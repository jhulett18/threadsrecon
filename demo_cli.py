#!/usr/bin/env python3
"""
Demo script to show the new CLI functionality and download path configuration
"""

import argparse
import os
import sys

# Add the project root to the path so we can import our modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import load_config, merge_cli_config

def demo_cli_functionality():
    """Demonstrate the new CLI functionality without running the full application"""
    
    # Create a mock argument parser similar to main.py
    parser = argparse.ArgumentParser(description='threadsrecon - OSINT Tool Demo')
    parser.add_argument('command', choices=['scrape', 'analyze', 'visualize', 'report', 'all'])
    parser.add_argument('-u', '--usernames', nargs='+', help='Target usernames')
    parser.add_argument('--headless', action='store_true', help='Run browser in headless mode')
    parser.add_argument('--output-dir', help='Custom output directory')
    parser.add_argument('--timeout', type=int, help='Page load timeout')
    parser.add_argument('--keywords', nargs='+', help='Analysis keywords')
    
    # Parse some example arguments
    test_args = [
        'scrape', '-u', 'user1', 'user2', '--headless', '--timeout', '30',
        '--output-dir', '/tmp/custom_output', '--keywords', 'crypto', 'bitcoin'
    ]
    
    args = parser.parse_args(test_args)
    
    print("🎯 Demo: threadsrecon Enhanced CLI Interface")
    print("=" * 50)
    
    print("\n📝 Command parsed:")
    print(f"  Command: {args.command}")
    print(f"  Usernames: {args.usernames}")
    print(f"  Headless: {args.headless}")
    print(f"  Timeout: {args.timeout}")
    print(f"  Output Dir: {args.output_dir}")
    print(f"  Keywords: {args.keywords}")
    
    # Load original config
    print("\n📂 Loading original configuration...")
    try:
        config = load_config()
        print("  ✅ Configuration loaded successfully")
    except SystemExit:
        print("  ⚠️  Using mock configuration for demo")
        config = {
            'ScraperSettings': {
                'usernames': ['example_user'],
                'chromedriver': '/usr/local/bin/chromedriver',
                'browser_options': {'headless': True}
            },
            'AnalysisSettings': {
                'input_file': 'data/profiles.json',
                'output_file': 'data/analyzed_profiles.json',
                'visualization_dir': 'data/visualizations',
                'keywords': ['keyword1', 'keyword2']
            },
            'ReportGeneration': {
                'output_path': 'data/reports/report.pdf'
            }
        }
    
    # Show original paths
    print("\n📁 Original download/output paths:")
    analysis = config.get('AnalysisSettings', {})
    report = config.get('ReportGeneration', {})
    print(f"  Profiles data: {analysis.get('input_file', 'data/profiles.json')}")
    print(f"  Analysis output: {analysis.get('output_file', 'data/analyzed_profiles.json')}")
    print(f"  Visualizations: {analysis.get('visualization_dir', 'data/visualizations')}")
    print(f"  PDF reports: {report.get('output_path', 'data/reports/report.pdf')}")
    
    # Merge CLI arguments
    print("\n🔄 Merging CLI arguments with configuration...")
    merged_config = merge_cli_config(config, args)
    
    # Show updated paths
    print("\n📁 Updated download/output paths after CLI merge:")
    analysis = merged_config.get('AnalysisSettings', {})
    report = merged_config.get('ReportGeneration', {})
    scraper = merged_config.get('ScraperSettings', {})
    
    print(f"  Target usernames: {scraper.get('usernames', [])}")
    print(f"  Profiles data: {analysis.get('input_file')}")
    print(f"  Analysis output: {analysis.get('output_file')}")
    print(f"  Visualizations: {analysis.get('visualization_dir')}")
    print(f"  PDF reports: {report.get('output_path')}")
    print(f"  Analysis keywords: {analysis.get('keywords', [])}")
    print(f"  Browser headless: {scraper.get('browser_options', {}).get('headless')}")
    
    print("\n📦 How data is packaged:")
    print("  🔍 Scraping: Raw data saved as JSON files")
    print("     └── profiles.json (user profiles, posts, followers)")
    print("  📈 Analysis: Processed data with sentiment analysis")
    print("     └── analyzed_profiles.json (enhanced with insights)")
    print("  📊 Visualization: Charts and network graphs")
    print("     └── *.png files (follower networks, sentiment charts)")
    print("  📑 Reports: Comprehensive PDF report")
    print("     └── report_TIMESTAMP.pdf (complete findings)")
    
    print("\n🎉 Demo completed! The new CLI interface allows:")
    print("  ✅ Custom usernames via -u flag")
    print("  ✅ Custom output directory via --output-dir")
    print("  ✅ Browser control via --headless/--no-headless")
    print("  ✅ Timeout control via --timeout")
    print("  ✅ Analysis keywords via --keywords")
    print("  ✅ All settings configurable without editing YAML!")

if __name__ == "__main__":
    demo_cli_functionality()