#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller for the scraping functionality of Threads Recon Tool
"""

import json
from scraping.scraper import ThreadsScraper

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
        base_url = config["ScraperSettings"]["base_url"]
        usernames = config["ScraperSettings"]["usernames"]
        chromedriver = config["ScraperSettings"]["chromedriver"]
        browser_path = config["ScraperSettings"].get("browser_path")
        instagram_username = config["Credentials"].get("instagram_username")
        instagram_password = config["Credentials"].get("instagram_password")
        
        # Get authentication mode (auto-detected from credentials)
        login_mode = config["ScraperSettings"].get("login_mode", "private")
        
    except KeyError as e:
        missing_key = str(e).strip("'")
        print(f"Missing configuration key: {missing_key}. Check your settings.yaml file.")
        return

    scraper = ThreadsScraper(base_url, chromedriver, browser_path)
    all_profiles_data = {}

    try:
        # Handle authentication based on mode
        if login_mode == "authenticated":
            print("🔐 Using authenticated mode with Instagram credentials")
            if not scraper.login(instagram_username, instagram_password):
                print("❌ Failed to login. Exiting...")
                return
        else:
            print("🕵️ Using private mode (no login, skip cookies)")
            # Try anonymous access with skip_consent=True
            if not scraper.login(None, None, skip_consent=True):
                print("❌ Failed to initialize private mode. Exiting...")
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
            
        print(f"Successfully scraped data for {len(all_profiles_data)} profiles.")
        return all_profiles_data
    finally:
        scraper.driver.quit() 