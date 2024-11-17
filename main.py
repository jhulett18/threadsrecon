#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
from scraping.scraper import ThreadsScraper
from analysis.sentiment_analysis import analyze_and_filter_data

script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Check for required Python version
if sys.version_info < (3, 6):
    print("Python 3.6 or higher is required. Please upgrade your Python version.")
    sys.exit(1)


def main():
    '''
    Scraping and adding to JSON
    '''

    # Check for 'data' folder
    if not os.path.exists("data"):
        print("Creating 'data' folder...")
        os.makedirs("data")

    # Check for settings.yaml
    if not os.path.exists("settings.yaml"):
        print("Configuration file 'settings.yaml' is missing. Exiting...")
        sys.exit(1)

    # Notify about missing dependencies
    try:
        import yaml
        import json
    except ImportError:
        print("Required libraries are missing. Run: python3 -m pip install -r requirements.txt")
        sys.exit(1)

    # Load configuration
    with open("settings.yaml", "r") as file:
        config = yaml.safe_load(file)

    # Retrieve configuration values
    try:
        base_url = config["ScraperSettings"]["base_url"]
        usernames = config["ScraperSettings"]["usernames"]
        chromedriver = config["ScraperSettings"]["chromedriver"]
        instagram_username = config["Credentials"]["instagram_username"]
        instagram_password = config["Credentials"]["instagram_password"]
    except KeyError as e:
        missing_key = str(e).strip("'")
        if "Credentials" in missing_key:
            print("Missing credentials key in settings.yaml. Anonymous scraping will be implemented.")
            instagram_username = None
            instagram_password = None
        else:
            print(f"Missing configuration key: {missing_key}. Check your settings.yaml file.")
            sys.exit(1)

    # Ensure chromedriver exists
    if not os.path.exists(chromedriver):
        print(f"Chromedriver not found at path: {chromedriver}. Exiting...")
        sys.exit(1)

    scraper = ThreadsScraper(base_url, chromedriver)

    # Login
    if not scraper.login(instagram_username, instagram_password):
        print("Failed to login. Exiting...")
        scraper.driver.quit()
        return

    all_profiles_data = {}

    # Fetch profile data
    try:
        for username in usernames:
            profile_data = scraper.fetch_profile(username)
            if profile_data:
                print(f"Profile Data for {username}:", profile_data)
                all_profiles_data[username] = profile_data
            else:
                print(f"No data retrieved for {username}.")

        # Write data to JSON file
        with open("data/profiles.json", "w") as json_file:
            json.dump(all_profiles_data, json_file, indent=4)
    finally:
        scraper.driver.quit()

    '''
    ANALYSIS
    '''

    input_file = "data/profiles.json"
    output_file = "data/archived_profiles.json"
    filtered_file = "data/filtered_profiles.json"

    # Filter criteria
    keyword_filter = "#Python"
    date_filter = "2023-07-06T23:35:04.000Z"

    # Run the analysis and filtering
    analyze_and_filter_data(input_file, output_file, filtered_file, keyword_filter, date_filter)
if __name__ == "__main__":
    main()
