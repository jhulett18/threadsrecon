from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
import time

class ThreadsScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        # Set up Chrome options
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless')  # Run in headless mode
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')


    def fetch_profile(self, username):
        url = f"{self.base_url}/{username}"
        service = Service('chromedriver')
        driver = webdriver.Chrome(service=service)
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        driver.quit()
    
        profile_data = {'username': username}
        bio_container = soup.find('div', class_='x17zef60')
        if bio_container:
            bio_text = bio_container.find('span', class_='x1lliihq')
            if bio_text:
                profile_data['bio'] = bio_text.get_text(strip=True)
            else:
                profile_data['bio'] = "Bio not found"
        else:
            profile_data['bio'] = "Bio not found"

        return profile_data