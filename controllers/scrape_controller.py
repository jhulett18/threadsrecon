#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Controller for the scraping functionality of Threads Recon Tool
"""

import json
import os
from scraping.scraper import ThreadsScraper

def scrape_data(config, debug=False):
    """
    Handle the scraping functionality
    
    Args:
        config (dict): Configuration containing scraping settings and credentials
        debug (bool): Enable detailed debug output
    
    Processes:
    1. Extracts required configuration
    2. Initializes scraper
    3. Logs in to Instagram
    4. Scrapes profile data for each username
    5. Saves results to individual JSON files and summary
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

    scraper = ThreadsScraper(base_url, chromedriver, browser_path, debug=debug)
    all_profiles_data = {}
    
    # Create users directory structure
    users_dir = "data/users"
    os.makedirs(users_dir, exist_ok=True)

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
            print(f"🔍 Scraping profile: {username}")
            profile_data_wrapper = scraper.fetch_profile(username)
            if profile_data_wrapper:
                # Extract the actual profile data from the wrapper
                profile_data = profile_data_wrapper.get(username, {})
                
                # Create individual user directory
                user_dir = os.path.join(users_dir, username)
                os.makedirs(user_dir, exist_ok=True)
                
                # Save individual profile JSON
                profile_file = os.path.join(user_dir, "profile.json")
                with open(profile_file, "w", encoding='utf-8') as json_file:
                    json.dump(profile_data_wrapper, json_file, indent=4, ensure_ascii=False)
                
                # Add to summary data
                all_profiles_data[username] = {
                    "scraped_at": profile_data.get("scraped_at"),
                    "posts_count": profile_data.get("posts_count", 0),
                    "replies_count": profile_data.get("replies_count", 0),
                    "reposts_count": profile_data.get("reposts_count", 0),
                    "media_summary": profile_data.get("media_summary", {}),
                    "profile_file": profile_file
                }
                
                # Show summary
                media_summary = profile_data.get("media_summary", {})
                images = media_summary.get("images_downloaded", 0)
                videos = media_summary.get("videos_downloaded", 0)
                posts = profile_data.get("posts_count", 0)
                replies = profile_data.get("replies_count", 0)
                
                print(f"✅ {username}: {posts} posts, {replies} replies, {images} images, {videos} videos")
                print(f"   📁 Saved to: {profile_file}")
            else:
                print(f"❌ No data retrieved for {username}")
                if debug:
                    print(f"   └── Check if username exists and is accessible")

        # Save summary data
        with open("data/profiles.json", "w", encoding='utf-8') as json_file:
            json.dump(all_profiles_data, json_file, indent=4, ensure_ascii=False)
            
        print(f"\n🎉 Successfully scraped {len(all_profiles_data)} profiles")
        print(f"📋 Summary saved to: data/profiles.json")
        return all_profiles_data
    finally:
        scraper.driver.quit() 