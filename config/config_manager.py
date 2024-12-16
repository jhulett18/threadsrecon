# config/config_manager.py
import yaml
from typing import Dict, Any

class ConfigManager:
    def __init__(self, config_path: str = 'settings.yaml'):
        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)
            
    def get_scraper_settings(self) -> Dict[str, Any]:
        return self.config.get('ScraperSettings', {})
    
    def get_timeouts(self) -> Dict[str, int]:
        return self.get_scraper_settings().get('timeouts', {
            'page_load': 20,
            'element_wait': 10
        })
    
    def get_retries(self) -> Dict[str, int]:
        return self.get_scraper_settings().get('retries', {
            'max_attempts': 3,
            'initial_delay': 1
        })
    
    def get_delays(self) -> Dict[str, int]:
        return self.get_scraper_settings().get('delays', {
            'min_wait': 1,
            'max_wait': 3
        })
    
    def get_user_agents(self) -> list:
        return self.get_scraper_settings().get('user_agents', [])
    
    def get_browser_options(self) -> Dict[str, Any]:
        return self.get_scraper_settings().get('browser_options', {})