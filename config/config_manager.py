# config/config_manager.py
"""
Configuration Manager Module

This module handles loading and accessing configuration settings from YAML files.
It provides a structured way to access different configuration sections with default values.
"""

import yaml
from typing import Dict, Any

class ConfigManager:
    """
    A class to manage configuration settings for the application
    
    This class loads configuration from a YAML file and provides methods
    to access different sections of the configuration with default values
    when settings are not specified.
    
    Attributes:
        config (dict): The complete configuration dictionary loaded from YAML
    """
    
    def __init__(self, config_path: str = 'settings.yaml'):
        """
        Initialize the ConfigManager with a YAML configuration file
        
        Args:
            config_path (str): Path to the YAML configuration file
                             Defaults to 'settings.yaml' in the current directory
                             
        Raises:
            FileNotFoundError: If the configuration file doesn't exist
            yaml.YAMLError: If the configuration file is not valid YAML
        """
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
    def get_scraper_settings(self) -> Dict[str, Any]:
        """
        Get all scraper-related settings
        
        Returns:
            Dict[str, Any]: Dictionary containing all scraper settings
                           Returns empty dict if 'ScraperSettings' section is missing
        
        Example config section:
            ScraperSettings:
              base_url: "https://example.com"
              timeouts:
                page_load: 20
                element_wait: 10
        """
        return self.config.get('ScraperSettings', {})
    
    def get_timeouts(self) -> Dict[str, int]:
        """
        Get timeout settings for web scraping operations
        
        Returns:
            Dict[str, int]: Dictionary containing timeout settings with defaults:
                - page_load: 20 seconds (timeout for entire page load)
                - element_wait: 10 seconds (timeout for individual element waits)
                
        Example config section:
            ScraperSettings:
              timeouts:
                page_load: 20
                element_wait: 10
        """
        return self.get_scraper_settings().get('timeouts', {
            'page_load': 20,    # Default page load timeout
            'element_wait': 10  # Default element wait timeout
        })
    
    def get_retries(self) -> Dict[str, int]:
        """
        Get retry settings for failed operations
        
        Returns:
            Dict[str, int]: Dictionary containing retry settings with defaults:
                - max_attempts: 3 (maximum number of retry attempts)
                - initial_delay: 1 (initial delay in seconds between retries)
                
        Example config section:
            ScraperSettings:
              retries:
                max_attempts: 3
                initial_delay: 1
        """
        return self.get_scraper_settings().get('retries', {
            'max_attempts': 3,    # Default number of retry attempts
            'initial_delay': 1    # Default delay between retries in seconds
        })
    
    def get_delays(self) -> Dict[str, int]:
        """
        Get delay settings for rate limiting
        
        Returns:
            Dict[str, int]: Dictionary containing delay settings with defaults:
                - min_wait: 1 (minimum wait time in seconds)
                - max_wait: 3 (maximum wait time in seconds)
                
        Example config section:
            ScraperSettings:
              delays:
                min_wait: 1
                max_wait: 3
        """
        return self.get_scraper_settings().get('delays', {
            'min_wait': 1,  # Default minimum wait time between requests
            'max_wait': 3   # Default maximum wait time between requests
        })
    
    def get_user_agents(self) -> list:
        """
        Get list of user agents for request rotation
        
        Returns:
            list: List of user agent strings to rotate through
                 Returns empty list if no user agents are configured
                 
        Example config section:
            ScraperSettings:
              user_agents:
                - "Mozilla/5.0 ..."
                - "Chrome/91.0 ..."
        """
        return self.get_scraper_settings().get('user_agents', [])
    
    def get_browser_options(self) -> Dict[str, Any]:
        """
        Get browser configuration options
        
        Returns:
            Dict[str, Any]: Dictionary containing browser options
                           Returns empty dict if no options are configured
                           
        Example config section:
            ScraperSettings:
              browser_options:
                headless: true
                disable_images: true
                proxy: "http://proxy.example.com:8080"
        """
        return self.get_scraper_settings().get('browser_options', {})