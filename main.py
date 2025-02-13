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
import yaml
import json
import asyncio
import argparse
import pandas as pd
import plotly.graph_objects as go
from scraping.scraper import ThreadsScraper
from analysis.sentiment_analysis import analyze_sentiment_nltk, process_posts
from processing.data_processing import DataProcessor
from reports.report_generator import GenerateReport
from visualization.visualization import HashtagNetworkAnalyzer
from datetime import datetime
import glob
import matplotlib.pyplot as plt
import plotly.io as pio

# Ensure we're running from the correct directory
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def check_requirements():
    """
    Check Python version and required dependencies
    Exits if Python version is < 3.6 or if required packages are missing
    """
    if sys.version_info < (3, 6):
        print("Python 3.6 or higher is required. Please upgrade your Python version.")
        sys.exit(1)

    try:
        import yaml
        import json
    except ImportError:
        print("Required libraries are missing. Run: python3 -m pip install -r requirements.txt")
        sys.exit(1)

def load_config():
    """
    Load and validate configuration from settings.yaml
    
    Returns:
        dict: Configuration settings from YAML file
    
    Exits if settings.yaml is missing
    """
    if not os.path.exists("settings.yaml"):
        print("Configuration file 'settings.yaml' is missing. Exiting...")
        sys.exit(1)

    with open("settings.yaml", "r") as file:
        config = yaml.safe_load(file)

    return config

def setup_environment(config):
    """
    Set up necessary folders and validate paths
    
    Creates required directories if they don't exist:
    - data/
    - data/visualizations/
    - data/reports/
    
    Args:
        config (dict): Configuration dictionary containing path settings
    
    Exits if chromedriver is not found at specified path
    """
    # Create necessary directories
    for directory in ["data", "data/visualizations", "data/reports"]:
        if not os.path.exists(directory):
            print(f"Creating '{directory}' folder...")
            os.makedirs(directory)

    # Validate chromedriver existence
    chromedriver = config["ScraperSettings"]["chromedriver"]
    if not os.path.exists(chromedriver):
        print(f"Chromedriver not found at path: {chromedriver}. Exiting...")
        sys.exit(1)

def scrape_data(config):
    """
    Handle the scraping functionality
    
    Args:
        config (dict): Configuration containing scraping settings and credentials
    
    Processes:
    1. Extracts required configuration
    2. Initializes scraper
    3. Logs in to Instagram
    4. Scrapes profile data for each username
    5. Saves results to JSON file
    """
    try:
        # Extract required configuration
        base_url = config["ScraperSettings"]["base_url"]
        usernames = config["ScraperSettings"]["usernames"]
        chromedriver = config["ScraperSettings"]["chromedriver"]
        instagram_username = config["Credentials"].get("instagram_username")
        instagram_password = config["Credentials"].get("instagram_password")
    except KeyError as e:
        missing_key = str(e).strip("'")
        print(f"Missing configuration key: {missing_key}. Check your settings.yaml file.")
        sys.exit(1)

    scraper = ThreadsScraper(base_url, chromedriver)
    all_profiles_data = {}

    try:
        # Attempt login and data collection
        if not scraper.login(instagram_username, instagram_password):
            print("Failed to login. Exiting...")
            return

        for username in usernames:
            profile_data = scraper.fetch_profile(username)
            if profile_data:
                print(f"Profile Data for {username}:", profile_data)
                all_profiles_data[username] = profile_data
            else:
                print(f"No data retrieved for {username}.")

        # Save collected data
        with open("data/profiles.json", "w") as json_file:
            json.dump(all_profiles_data, json_file, indent=4)
    finally:
        scraper.driver.quit()
        
def visualize_all(config):
    """
    Generate all visualizations from the processed data
    
    Args:
        config (dict): Configuration containing visualization settings
    """
    processor = DataProcessor(config["AnalysisSettings"]["input_file"])
    
    # Get visualization directory from config
    viz_dir = config["AnalysisSettings"]["visualization_dir"]
    os.makedirs(viz_dir, exist_ok=True)
    
    # Combine all posts data into a single DataFrame
    all_posts_data = []
    for username, outer_profile in processor.data.items():
        if isinstance(outer_profile, dict):
            inner_profile = outer_profile.get(username, {})
            posts = inner_profile.get('posts', {})
            if posts:
                posts_df = process_posts(posts)
                posts_df['username'] = username
                all_posts_data.append(posts_df)
    
    combined_df = pd.concat(all_posts_data, ignore_index=True) if all_posts_data else pd.DataFrame()
    
    # Initialize analyzer and generate visualizations
    analyzer = HashtagNetworkAnalyzer(combined_df)
    
    # Generate and save all visualizations with standardized naming
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Save all figures
    visualizations = {
        'hashtag_network': analyzer.plot_plotly(),
        'sentiment': analyzer.plot_sentiment_trends(combined_df),
        'engagement': analyzer.plot_engagement_metrics(combined_df),
        'mutual_followers': analyzer.plot_mutual_followers_network(processor.data),
        'hashtag_dist': analyzer.plot_hashtag_distribution()
    }
    
    for name, fig in visualizations.items():
        if fig:
            if isinstance(fig, plt.Figure):  # Matplotlib figure
                output_path = os.path.join(viz_dir, f"{name}_{timestamp}.png")
                fig.savefig(output_path)
                plt.close(fig)
            else:  # Plotly figure
                # Save interactive HTML
                html_path = os.path.join(viz_dir, f"{name}_{timestamp}.html")
                fig.write_html(html_path)
                
                # Save static PNG
                png_path = os.path.join(viz_dir, f"{name}_{timestamp}.png")
                fig.write_image(png_path)
    
    # Print strongest connections
    edge_weights = sorted(
        [(tags, weight) for tags, weight in analyzer.edge_weights.items()],
        key=lambda x: x[1],
        reverse=True
    )[:10]
    
    print("\nStrongest hashtag connections:")
    for (tag1, tag2), weight in edge_weights:
        print(f"#{tag1} - #{tag2}: {weight} co-occurrences")

def generate_report(config):
    """
    Generate a PDF report with all analysis results
    """
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_path = config["ReportGeneration"]["output_path"]
    
    # Insert timestamp before the file extension
    base, ext = os.path.splitext(output_path)
    output_path_with_timestamp = f"{base}_{timestamp}{ext}"
    
    # Get the most recent visualization files
    viz_dir = config["AnalysisSettings"]["visualization_dir"]
    network_plot = max(glob.glob(os.path.join(viz_dir, "hashtag_network_*.png")), default=None)
    sentiment_plot = max(glob.glob(os.path.join(viz_dir, "sentiment_*.html")), default=None)
    engagement_plot = max(glob.glob(os.path.join(viz_dir, "engagement_*.html")), default=None)
    mutual_followers_plot = max(glob.glob(os.path.join(viz_dir, "mutual_followers_*.html")), default=None)
    hashtag_dist_plot = max(glob.glob(os.path.join(viz_dir, "hashtag_dist_*.png")), default=None)
    
    report = GenerateReport()
    report.create_report(
        config["AnalysisSettings"]["output_file"],
        config["ReportGeneration"]["path_to_wkhtmltopdf"],
        network_plot,
        sentiment_plot,
        engagement_plot,
        mutual_followers_plot,
        hashtag_dist_plot,
        output_path_with_timestamp
    )

async def analyze_data(config):
    """
    Handle the analysis functionality with warning system integration
    
    Args:
        config (dict): Configuration containing analysis settings and warning system credentials
    
    Features:
    - Integrates with Telegram warning system
    - Processes data based on configured date range
    - Archives processed data
    - Reports processing statistics
    
    Returns:
        None, but prints processing results
    """
    # Get Telegram credentials from config
    telegram_token = config.get("WarningSystem", {}).get("token")
    chat_id = config.get("WarningSystem", {}).get("chat_id")
    priority_keywords = config.get("WarningSystem", {}).get("priority_keywords", {
        'HIGH': ['urgent', 'emergency'],
        'MEDIUM': ['important', 'attention'],
        'LOW': ['update', 'info']
    })

    # Get analysis settings with defaults
    analysis_settings = config.get("AnalysisSettings", {})
    date_range = analysis_settings.get("date_range", {})
    
    # Initialize DataProcessor with warning system
    processor = DataProcessor(
        analysis_settings.get("input_file"),
        telegram_token=telegram_token,
        chat_id=chat_id,
        priority_keywords=priority_keywords
    )
    
    result = await processor.process_and_archive(
        analysis_settings.get("output_file"),
        analysis_settings.get("archive_file"),
        analysis_settings.get("keywords"),
        date_range.get("start"),
        date_range.get("end")
    )
    
    if result:
        print(f"Processing complete. Processed {result['metadata']['total_posts']} posts.")
    else:
        print("No data to process.")

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
    
    # Execute requested command
    if args.command == 'scrape' or args.command == 'all':
        print("Starting data scraping...")
        scrape_data(config)
    
    if args.command == 'analyze' or args.command == 'all':
        print("Starting data analysis...")
        await analyze_data(config)
    
    if args.command == 'visualize' or args.command == 'all':
        print("Generating network visualization...")
        visualize_all(config)
        
    if args.command == 'report' or args.command == 'all':
        print("Generating pdf report...")
        generate_report(config)

if __name__ == "__main__":
    asyncio.run(main())