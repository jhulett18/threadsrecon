#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller for the scraping functionality of Threads Recon Tool
"""

import json
import asyncio
from scraping.scraper import ThreadsScraper

def scrape_data(config):
    """
    Handle the scraping functionality
    
    Args:
        config (dict): Configuration containing scraping settings and credentials
    
    Processes:
    1. Extracts required configuration
    2. Initializes scraper
    3. Logs in to Instagram (unless --no-login is specified)
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
        no_login = config["ScraperSettings"].get("no_login", True)
        skip_consent = config["ScraperSettings"].get("skip_consent", True)
        
        # Media collection is always enabled - get customization settings
        collect_images = config["ScraperSettings"].get("collect_images", True)
        collect_videos = config["ScraperSettings"].get("collect_videos", True)
        max_file_size = config["ScraperSettings"].get("max_file_size", 50*1024*1024)
        concurrent_downloads = config["ScraperSettings"].get("concurrent_downloads", 5)
    except KeyError as e:
        missing_key = str(e).strip("'")
        print(f"Missing configuration key: {missing_key}. Check your settings.yaml file.")
        return

    scraper = ThreadsScraper(base_url, chromedriver, browser_path)
    
    # Media collection is always enabled
    print(f"🎬 Media collection enabled (Images: {collect_images}, Videos: {collect_videos})")
    scraper.enable_media_collection(
        collect_images=collect_images,
        collect_videos=collect_videos,
        max_file_size=max_file_size,
        concurrent_downloads=concurrent_downloads
    )
    
    all_profiles_data = {}

    try:
        # Handle authentication based on mode
        if login_mode == "authenticated":
            print("🔐 Using authenticated mode with Instagram credentials")
            login_success = scraper.login(instagram_username, instagram_password, skip_consent=skip_consent)
            if not login_success:
                print("❌ Failed to login. Exiting...")
                return
        else:
            print("🕵️ Using private mode (no login, skip cookies)")
            # Initialize for anonymous access
            if not hasattr(scraper, 'no_login_initialized'):
                try:
                    scraper.driver.get(base_url)
                    scraper.no_login_initialized = True
                    login_success = True
                except Exception as e:
                    print(f"❌ Error initializing private mode: {e}")
                    return
            else:
                login_success = True

        for username in usernames:
            
            profile_data = scraper.fetch_profile(username)
            if profile_data:
                print(f"Profile Data for {username}:", profile_data)
                all_profiles_data[username] = profile_data
                
                # Download collected media (always enabled)
                if scraper.media_collector:
                    print(f"📥 Starting media download for {username}...")
                    try:
                        # Run async media download
                        media_stats = asyncio.run(scraper.download_collected_media(username))
                        
                        # Add media stats to profile data
                        profile_data[username]['media_stats'] = media_stats
                        
                        # Reset collector for next user
                        scraper.reset_media_collection()
                        
                    except Exception as e:
                        print(f"❌ Error downloading media for {username}: {e}")
                
            else:
                print(f"No data retrieved for {username}.")

        # Save collected data
        with open("data/profiles.json", "w") as json_file:
            json.dump(all_profiles_data, json_file, indent=4)
            
        print(f"Successfully scraped data for {len(all_profiles_data)} profiles.")
        return all_profiles_data
    finally:
        scraper.driver.quit() 