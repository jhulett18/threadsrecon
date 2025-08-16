#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for the Threads Data Analysis Tool
This script orchestrates the entire data pipeline:
- Data scraping from Threads.net
- Data analysis and processing
- Visualization generation
- Report creation

Enhanced with comprehensive CLI argument support for easy usage.
"""

import os
import sys
import asyncio
import argparse

# Ensure we're running from the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Import utility functions
from utils.helpers import (
    check_requirements,
    load_config,
    merge_cli_config,
    setup_environment,
    display_ascii_art
)

# Import controllers
from controllers.scrape_controller import scrape_data
from controllers.analysis_controller import analyze_data
from controllers.visualization_controller import visualize_all
from controllers.report_controller import generate_report

def create_parser():
    """
    Create and configure the argument parser with comprehensive CLI options
    
    Returns:
        argparse.ArgumentParser: Configured argument parser
    """
    parser = argparse.ArgumentParser(
        description='threadsrecon - OSINT Tool for threads.net',
        epilog='''
Examples:
  %(prog)s scrape -u username1 username2     # Scrape specific usernames
  %(prog)s scrape -u target --headless       # Scrape in headless mode  
  %(prog)s all -u user --timeout 30          # Full pipeline with custom timeout
  %(prog)s analyze --keywords "crypto btc"   # Analyze with specific keywords
  %(prog)s report --output-dir /custom/path  # Generate report in custom directory
        ''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    # Main command argument
    parser.add_argument(
        'command', 
        choices=['scrape', 'analyze', 'visualize', 'report', 'all'],
        help='Command to execute: scrape, analyze, visualize, report, or all'
    )
    
    # Username arguments
    parser.add_argument(
        '-u', '--usernames',
        nargs='+',
        metavar='USERNAME',
        help='Target usernames to scrape (can specify multiple: -u user1 user2 user3)'
    )
    
    # Browser options
    parser.add_argument(
        '--headless',
        action='store_true',
        help='Run browser in headless mode (invisible browser window)'
    )
    parser.add_argument(
        '--no-headless',
        action='store_true',
        help='Run browser with visible window (useful for debugging)'
    )
    
    # Paths and directories
    parser.add_argument(
        '--chromedriver',
        metavar='PATH',
        help='Path to chromedriver executable'
    )
    parser.add_argument(
        '--output-dir',
        metavar='DIR',
        help='Output directory for generated files'
    )
    parser.add_argument(
        '--config',
        metavar='FILE',
        default='settings.yaml',
        help='Path to configuration YAML file (default: settings.yaml)'
    )
    
    # Analysis options
    parser.add_argument(
        '--keywords',
        nargs='+',
        metavar='KEYWORD',
        help='Keywords for analysis (can specify multiple: --keywords crypto bitcoin web3)'
    )
    
    # Timing and retry options
    parser.add_argument(
        '--timeout',
        type=int,
        metavar='SECONDS',
        help='Page load timeout in seconds'
    )
    parser.add_argument(
        '--element-timeout',
        type=int,
        metavar='SECONDS',
        help='Element wait timeout in seconds'
    )
    parser.add_argument(
        '--max-retries',
        type=int,
        metavar='COUNT',
        help='Maximum number of retry attempts'
    )
    
    # Delay options for rate limiting
    parser.add_argument(
        '--min-delay',
        type=int,
        metavar='SECONDS',
        help='Minimum delay between requests'
    )
    parser.add_argument(
        '--max-delay',
        type=int,
        metavar='SECONDS',
        help='Maximum delay between requests'
    )
    
    # Credentials (optional)
    parser.add_argument(
        '--instagram-username',
        metavar='USERNAME',
        help='Instagram username for authentication (optional)'
    )
    parser.add_argument(
        '--instagram-password',
        metavar='PASSWORD',
        help='Instagram password for authentication (optional)'
    )
    
    # Report options
    parser.add_argument(
        '--wkhtmltopdf',
        metavar='PATH',
        help='Path to wkhtmltopdf executable'
    )
    
    # Telegram options
    parser.add_argument(
        '--telegram-token',
        metavar='TOKEN',
        help='Telegram bot token for notifications'
    )
    parser.add_argument(
        '--telegram-chat-id',
        metavar='CHAT_ID',
        help='Telegram chat ID for notifications'
    )
    
    # Output options
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Suppress non-error output'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable verbose output'
    )
    
    return parser

async def main():
    """
    Main entry point for the application
    
    Handles:
    1. Command line argument parsing with comprehensive options
    2. Configuration loading and CLI argument merging
    3. Initial setup and validation
    4. Execution of requested operations (scrape/analyze/visualize/report)
    5. Sequential execution of all operations if 'all' is specified
    """
    parser = create_parser()
    args = parser.parse_args()
    
    # Validate conflicting arguments
    if args.headless and args.no_headless:
        parser.error("Cannot specify both --headless and --no-headless")
    
    # Display help for common mistakes
    if not args.usernames and args.command in ['scrape', 'all']:
        print("⚠️  No usernames specified. Either:")
        print("   1. Use: threadsrecon {} -u username1 username2".format(args.command))
        print("   2. Or configure usernames in your settings.yaml file")
        print()
    
    # Initial setup
    if not args.quiet:
        print("🔧 Checking requirements...")
    check_requirements()
    
    if not args.quiet:
        print(f"📝 Loading configuration from {args.config}...")
    config = load_config(args.config)
    
    if not args.quiet:
        print("🔄 Merging CLI arguments with configuration...")
    config = merge_cli_config(config, args)
    
    if not args.quiet:
        print("🛠️  Setting up environment...")
    setup_environment(config)
    
    # Show configuration summary if verbose
    if args.verbose:
        usernames = config.get('ScraperSettings', {}).get('usernames', [])
        print(f"📊 Target usernames: {', '.join(usernames) if usernames else 'None specified'}")
        browser_opts = config.get('ScraperSettings', {}).get('browser_options', {})
        headless_mode = browser_opts.get('headless', True)
        print(f"🌐 Browser mode: {'Headless' if headless_mode else 'Visible'}")
        print()
    
    # Variables to track results between pipeline stages
    analysis_results = None
    visualization_paths = None
    
    # Execute requested command
    if args.command == 'scrape' or args.command == 'all':
        if not args.quiet:
            display_ascii_art('scrape')
            print("🔍 Starting data scraping...")
        scrape_data(config)
    
    if args.command == 'analyze' or args.command == 'all':
        if not args.quiet:
            display_ascii_art('analyze')
            print("📈 Starting data analysis...")
        analysis_results = await analyze_data(config)
    
    if args.command == 'visualize' or args.command == 'all':
        if not args.quiet:
            display_ascii_art('visualize')
            print("📊 Generating network visualization...")
            print("⏳ This may take a few minutes for large datasets...")
        visualization_paths = visualize_all(config)
        
    if args.command == 'report' or args.command == 'all':
        if not args.quiet:
            display_ascii_art('report')
            print("📑 Generating PDF report...")
        # Pass visualization paths to the report generator if available
        report_path = generate_report(config, visualization_paths)
        if report_path:
            if not args.quiet:
                print(f"✅ Report generated at: {report_path}")
    
    if not args.quiet:
        print("🎉 Operation completed successfully!")

def cli_main():
    """
    Entry point for console script installation
    Wrapper around main() to handle asyncio
    """
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n❌ Operation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    cli_main()