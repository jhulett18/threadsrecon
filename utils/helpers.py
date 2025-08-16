#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Helper utilities for the Threads Recon Tool
"""

import os
import sys
import yaml
import json

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

def load_config(config_path="settings.yaml"):
    """
    Load and validate configuration from YAML file
    
    Args:
        config_path (str): Path to the configuration YAML file
    
    Returns:
        dict: Configuration settings from YAML file
    
    Exits if configuration file is missing
    """
    if not os.path.exists(config_path):
        print(f"Configuration file '{config_path}' is missing. Exiting...")
        sys.exit(1)

    with open(config_path, "r") as file:
        config = yaml.safe_load(file)

    return config

def merge_cli_config(config, args):
    """
    Merge command line arguments with YAML configuration
    CLI arguments take precedence over YAML settings
    
    Args:
        config (dict): Configuration loaded from YAML file
        args (argparse.Namespace): Parsed command line arguments
    
    Returns:
        dict: Merged configuration with CLI overrides applied
    """
    # Deep copy to avoid modifying original config
    import copy
    merged_config = copy.deepcopy(config)
    
    # Ensure required sections exist
    if 'ScraperSettings' not in merged_config:
        merged_config['ScraperSettings'] = {}
    if 'AnalysisSettings' not in merged_config:
        merged_config['AnalysisSettings'] = {}
    if 'ReportGeneration' not in merged_config:
        merged_config['ReportGeneration'] = {}
    if 'Credentials' not in merged_config:
        merged_config['Credentials'] = {}
    if 'WarningSystem' not in merged_config:
        merged_config['WarningSystem'] = {}
    
    # ScraperSettings overrides
    scraper_settings = merged_config['ScraperSettings']
    
    # Username overrides
    if args.usernames:
        scraper_settings['usernames'] = args.usernames
    
    # ChromeDriver path override
    if hasattr(args, 'chromedriver') and args.chromedriver:
        scraper_settings['chromedriver'] = args.chromedriver
    
    # Browser options overrides
    if 'browser_options' not in scraper_settings:
        scraper_settings['browser_options'] = {}
    
    if hasattr(args, 'headless') and args.headless:
        scraper_settings['browser_options']['headless'] = True
    elif hasattr(args, 'no_headless') and args.no_headless:
        scraper_settings['browser_options']['headless'] = False
    
    # Timeout overrides
    if 'timeouts' not in scraper_settings:
        scraper_settings['timeouts'] = {}
    
    if hasattr(args, 'timeout') and args.timeout:
        scraper_settings['timeouts']['page_load'] = args.timeout
    if hasattr(args, 'element_timeout') and args.element_timeout:
        scraper_settings['timeouts']['element_wait'] = args.element_timeout
    
    # Retry overrides
    if 'retries' not in scraper_settings:
        scraper_settings['retries'] = {}
    
    if hasattr(args, 'max_retries') and args.max_retries:
        scraper_settings['retries']['max_attempts'] = args.max_retries
    
    # Delay overrides
    if 'delays' not in scraper_settings:
        scraper_settings['delays'] = {}
    
    if hasattr(args, 'min_delay') and args.min_delay:
        scraper_settings['delays']['min_wait'] = args.min_delay
    if hasattr(args, 'max_delay') and args.max_delay:
        scraper_settings['delays']['max_wait'] = args.max_delay
    
    # AnalysisSettings overrides
    analysis_settings = merged_config['AnalysisSettings']
    
    if hasattr(args, 'keywords') and args.keywords:
        analysis_settings['keywords'] = args.keywords
    
    # Output directory overrides
    if hasattr(args, 'output_dir') and args.output_dir:
        # Update all output paths to use custom directory
        base_dir = args.output_dir
        analysis_settings['input_file'] = os.path.join(base_dir, "profiles.json")
        analysis_settings['archive_file'] = os.path.join(base_dir, "archived_profiles.json")
        analysis_settings['output_file'] = os.path.join(base_dir, "analyzed_profiles.json")
        analysis_settings['visualization_dir'] = os.path.join(base_dir, "visualizations")
        merged_config['ReportGeneration']['output_path'] = os.path.join(base_dir, "reports", "report.pdf")
    
    # Credentials overrides
    if hasattr(args, 'instagram_username') and args.instagram_username:
        merged_config['Credentials']['instagram_username'] = args.instagram_username
    if hasattr(args, 'instagram_password') and args.instagram_password:
        merged_config['Credentials']['instagram_password'] = args.instagram_password
    
    # Report generation overrides
    if hasattr(args, 'wkhtmltopdf') and args.wkhtmltopdf:
        merged_config['ReportGeneration']['path_to_wkhtmltopdf'] = args.wkhtmltopdf
    
    # Telegram overrides
    if hasattr(args, 'telegram_token') and args.telegram_token:
        merged_config['WarningSystem']['token'] = args.telegram_token
    if hasattr(args, 'telegram_chat_id') and args.telegram_chat_id:
        merged_config['WarningSystem']['chat_id'] = args.telegram_chat_id
    
    # Auto-detect authentication mode based on credentials
    has_username = hasattr(args, 'instagram_username') and args.instagram_username
    has_password = hasattr(args, 'instagram_password') and args.instagram_password
    
    if has_username and has_password:
        # Authenticated mode: use login with cookie handling
        merged_config['ScraperSettings']['login_mode'] = 'authenticated'
        merged_config['ScraperSettings']['no_login'] = False
        merged_config['ScraperSettings']['skip_consent'] = False
    else:
        # Private mode: skip login and cookies (default)
        merged_config['ScraperSettings']['login_mode'] = 'private'
        merged_config['ScraperSettings']['no_login'] = True
        merged_config['ScraperSettings']['skip_consent'] = True
    
    # Media collection is always enabled - just handle customization
    merged_config['ScraperSettings']['collect_media'] = True
    
    # Parse media types
    media_types = getattr(args, 'media_types', ['all'])
    if 'all' in media_types:
        collect_images = collect_videos = True
    else:
        collect_images = 'images' in media_types
        collect_videos = 'videos' in media_types
    
    merged_config['ScraperSettings']['collect_images'] = collect_images
    merged_config['ScraperSettings']['collect_videos'] = collect_videos
    
    # File size limit (convert MB to bytes)
    if hasattr(args, 'max_file_size') and args.max_file_size:
        merged_config['ScraperSettings']['max_file_size'] = args.max_file_size * 1024 * 1024
    
    # Concurrent downloads
    if hasattr(args, 'concurrent_downloads') and args.concurrent_downloads:
        merged_config['ScraperSettings']['concurrent_downloads'] = args.concurrent_downloads
    
    return merged_config

def setup_environment(config):
    """
    Set up necessary folders and validate paths
    
    Creates required directories based on configuration:
    - Analysis input/output directories
    - Visualization directory
    - Reports directory
    
    Args:
        config (dict): Configuration dictionary containing path settings
    
    Exits if chromedriver is not found at specified path
    """
    # Get directories from configuration
    analysis_settings = config.get('AnalysisSettings', {})
    report_settings = config.get('ReportGeneration', {})
    
    # Determine directories to create
    directories_to_create = set()
    
    # Add analysis directories
    for file_path in [
        analysis_settings.get('input_file', 'data/profiles.json'),
        analysis_settings.get('archive_file', 'data/archived_profiles.json'),
        analysis_settings.get('output_file', 'data/analyzed_profiles.json')
    ]:
        directories_to_create.add(os.path.dirname(file_path))
    
    # Add visualization directory
    viz_dir = analysis_settings.get('visualization_dir', 'data/visualizations')
    directories_to_create.add(viz_dir)
    
    # Add reports directory
    report_path = report_settings.get('output_path', 'data/reports/report.pdf')
    directories_to_create.add(os.path.dirname(report_path))
    
    # Create all required directories
    for directory in directories_to_create:
        if directory and not os.path.exists(directory):
            print(f"Creating '{directory}' folder...")
            os.makedirs(directory, exist_ok=True)
    
    # Validate chromedriver existence
    chromedriver = config.get("ScraperSettings", {}).get("chromedriver")
    if chromedriver and not os.path.exists(chromedriver):
        print(f"Warning: ChromeDriver not found at path: {chromedriver}")
        print("Please ensure ChromeDriver is installed and the path is correct.")
        # Don't exit, let the user try to proceed (they might have it in PATH)

def display_ascii_art(command):
    """
    Display ASCII art based on the command being executed
    
    Args:
        command (str): The command being executed
    """
    art = {
        "scrape": """
    ╔═╗┌─┐┬─┐┌─┐┌─┐┌─┐┬─┐
    ╚═╗│  ├┬┘├─┤├─┘├┤ ├┬┘
    ╚═╝└─┘┴└─┴ ┴┴  └─┘┴└─
        """,
        "analyze": """
    ╔═╗┌┐┌┌─┐┬  ┬┌─┐┌─┐
    ╠═╣│││├─┤│  │┌─┘├┤ 
    ╩ ╩┘└┘┴ ┴┴─┘┴└─┘└─┘
        """,
        "visualize": """
    ╦  ╦┬┌─┐┬ ┬┌─┐┬  ┬┌─┐┌─┐
    ╚╗╔╝│└─┐│ │├─┤│  │┌─┘├┤ 
     ╚╝ ┴└─┘└─┘┴ ┴┴─┘┴└─┘└─┘
        """,
        "report": """
    ╦═╗┌─┐┌─┐┌─┐┬─┐┌┬┐
    ╠╦╝├┤ ├─┘│ │├┬┘ │ 
    ╩╚═└─┘┴  └─┘┴└─ ┴ 
        """,
        "all": """
    ╔═╗┬  ┬  ┬
    ╠═╣│  │  │
    ╩ ╩┴─┘┴─┘┴─┘
        """
    }
    print("\033[96m" + art.get(command, "") + "\033[0m")  # Cyan color with reset 