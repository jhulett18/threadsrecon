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