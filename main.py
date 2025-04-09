#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main entry point for the Threads Data Analysis Tool
This script orchestrates the entire data pipeline:
- Data scraping from Threads.net
- Data analysis and processing
- Visualization generation
- Report creation
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
    setup_environment,
    display_ascii_art
)

# Import controllers
from controllers.scrape_controller import scrape_data
from controllers.analysis_controller import analyze_data
from controllers.visualization_controller import visualize_all
from controllers.report_controller import generate_report

async def main():
    """
    Main entry point for the application
    
    Handles:
    1. Command line argument parsing
    2. Initial setup and configuration
    3. Execution of requested operations (scrape/analyze/visualize/report)
    4. Sequential execution of all operations if 'all' is specified
    
    Command line options:
    - scrape: Collect data from Threads.net
    - analyze: Process and analyze collected data
    - visualize: Generate visualization of analysis results
    - report: Create PDF report of findings
    - all: Execute all above operations in sequence
    """
    parser = argparse.ArgumentParser(description='Threads Data Analysis Tool')
    parser.add_argument('command', choices=['scrape', 'analyze', 'visualize','report', 'all'],
                      help='Command to execute: scrape, analyze, visualize, report, or all')
    
    args = parser.parse_args()
    
    # Initial setup
    check_requirements()
    config = load_config()
    setup_environment(config)
    
    # Variables to track results between pipeline stages
    analysis_results = None
    visualization_paths = None
    
    # Execute requested command
    if args.command == 'scrape' or args.command == 'all':
        display_ascii_art('scrape')
        print("Starting data scraping...")
        scrape_data(config)
    
    if args.command == 'analyze' or args.command == 'all':
        display_ascii_art('analyze')
        print("Starting data analysis...")
        analysis_results = await analyze_data(config)
    
    if args.command == 'visualize' or args.command == 'all':
        display_ascii_art('visualize')
        print("Generating network visualization...")
        print("This may take a few minutes for large datasets...")
        visualization_paths = visualize_all(config)
        
    if args.command == 'report' or args.command == 'all':
        display_ascii_art('report')
        print("Generating pdf report...")
        # Pass visualization paths to the report generator if available
        report_path = generate_report(config, visualization_paths)
        if report_path:
            print(f"Report generated at: {report_path}")

if __name__ == "__main__":
    asyncio.run(main())