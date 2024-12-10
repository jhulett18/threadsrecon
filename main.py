#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import yaml
import json
import asyncio
import argparse
from scraping.scraper import ThreadsScraper
from analysis.sentiment_analysis import analyze_sentiment_nltk, process_posts
from processing.data_processing import DataProcessor

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
def visualize_network(config):
    """Handle the hashtag network visualization"""
    processor = DataProcessor(config["AnalysisSettings"]["input_file"])
    network_analysis = processor.analyze_hashtag_network()
    
    if network_analysis['static']:
        network_analysis['static'].savefig(
            config["AnalysisSettings"]["hashtag_network_static"]
        )

    if network_analysis['interactive']:
        network_analysis['interactive'].write_html(
            config["AnalysisSettings"]["hashtag_network_interactive"]
        )

    print("\nStrongest hashtag connections:")
    for (tag1, tag2), weight in network_analysis['strongest_connections']:
        print(f"#{tag1} - #{tag2}: {weight} co-occurrences")
        
async def analyze_data(config):
    """Handle the analysis functionality with warning system integration"""
    # Get Telegram credentials from config
    telegram_token = config.get("WarningSystem", {}).get("token")
    chat_id = config.get("WarningSystem", {}).get("chat_id")
    priority_keywords = config.get("WarningSystem", {}).get("priority_keywords", {
        # If "priority_keywords" isn't found, uses the default dictionary provided:
        'HIGH': ['urgent', 'emergency'],
        'MEDIUM': ['important', 'attention'],
        'LOW': ['update', 'info']
    })

    # Initialize DataProcessor with warning system
    processor = DataProcessor(
        config["AnalysisSettings"]["input_file"],
        telegram_token=telegram_token,
        chat_id=chat_id,
        priority_keywords=priority_keywords
    )
    
    result = await processor.process_and_archive(
        config["AnalysisSettings"]["output_file"],
        config["AnalysisSettings"]["archive_file"],
        config["AnalysisSettings"]["keywords"],
        config["AnalysisSettings"]["date_range"]["start"],
        config["AnalysisSettings"]["date_range"]["end"]
    )
    
    if result:
        print(f"Processing complete. Processed {result['metadata']['total_posts']} posts.")
    else:
        print("No data to process.")

async def main():
    parser = argparse.ArgumentParser(description='Threads Data Analysis Tool')
    parser.add_argument('command', choices=['scrape', 'analyze', 'visualize', 'all'],
                      help='Command to execute: scrape, analyze, visualize, or all')
    
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
        visualize_network(config)

if __name__ == "__main__":
    asyncio.run(main())