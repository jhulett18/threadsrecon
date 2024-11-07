import requests
from bs4 import BeautifulSoup

class ThreadsScraper:
    def __init__(self, base_url):
        self.base_url = base_url