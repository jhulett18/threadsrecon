#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import json
import asyncio
import argparse
import pandas as pd
from scraping.scraper import ThreadsScraper
from analysis.sentiment_analysis import analyze_sentiment_nltk, process_posts
from processing.data_processing import DataProcessor
from reports.report_generator import GenerateReport
from visualization.visualization import HashtagNetworkAnalyzer
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

def check_requirements():
    """Check Python version and required dependencies"""
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
    """Load and validate configuration from settings.yaml"""
    if not os.path.exists("settings.yaml"):
        print("Configuration file 'settings.yaml' is missing. Exiting...")
        sys.exit(1)

    with open("settings.yaml", "r") as file:
        config = yaml.safe_load(file)

    return config

def setup_environment(config):
    """Set up necessary folders and validate paths"""
    if not os.path.exists("data"):
        print("Creating 'data' folder...")
        os.makedirs("data")

    chromedriver = config["ScraperSettings"]["chromedriver"]
    if not os.path.exists(chromedriver):
        print(f"Chromedriver not found at path: {chromedriver}. Exiting...")
        sys.exit(1)

def scrape_data(config):
    """Handle the scraping functionality"""
    try:
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

        with open("data/profiles.json", "w") as json_file:
            json.dump(all_profiles_data, json_file, indent=4)
    finally:
        scraper.driver.quit()
        
def visualize_all(config):
    """Handle all visualizations"""
    processor = DataProcessor(config["AnalysisSettings"]["input_file"])
    
    # Get all posts data as a DataFrame
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
    
    # Now create analyzer with the processed DataFrame
    analyzer = HashtagNetworkAnalyzer(combined_df)
    
    # Generate static and interactive network visualizations
    static_fig = analyzer.plot_matplotlib()
    interactive_fig = analyzer.plot_plotly()
    
    # Generate other visualizations
    sentiment_plot = analyzer.plot_sentiment_trends(combined_df)
    engagement_plot = analyzer.plot_engagement_metrics(combined_df)
    mutual_followers_plot = analyzer.plot_mutual_followers_network(processor.data)
    hashtag_dist_plot = analyzer.plot_hashtag_distribution()
    
    # Save the visualizations
    if static_fig:
        static_fig.savefig(config["AnalysisSettings"]["hashtag_network_static"])
    if interactive_fig:
        interactive_fig.write_html(config["AnalysisSettings"]["hashtag_network_interactive"])
    if sentiment_plot:
        sentiment_plot.savefig(config["AnalysisSettings"]["sentiment_plot"])
    if engagement_plot:
        engagement_plot.savefig(config["AnalysisSettings"]["engagement_plot"])
    if mutual_followers_plot:
        mutual_followers_plot.savefig(config["AnalysisSettings"]["mutual_followers_plot"])
    if hashtag_dist_plot:
        hashtag_dist_plot.savefig(config["AnalysisSettings"]["hashtag_dist_plot"])
    
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
    report = GenerateReport()
    report.create_report(config["AnalysisSettings"]["output_file"],
                         config["ReportGeneration"]["path_to_wkhtmltopdf"],
                         config["AnalysisSettings"]["hashtag_network_static"],
                         config["AnalysisSettings"]["sentiment_plot"],
                         config["AnalysisSettings"]["engagement_plot"],
                         config["AnalysisSettings"]["mutual_followers_plot"],
                         config["AnalysisSettings"]["hashtag_dist_plot"]
                            )
    
    
async def analyze_data(config):
    """Handle the analysis functionality with warning system integration"""
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