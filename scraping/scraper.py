import requests
from bs4 import BeautifulSoup

class ThreadsScraper:
    def __init__(self, base_url):
        self.base_url = base_url

    def fetch_profile(self, username):
        url = f"{self.base_url}/{username}"
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            profile_data = {'username': username}
            # Parse bio information within the specific div and span structure
            biocontainer = soup.find('div', class_='x17zef60')
            if biocontainer:
                bio_text = biocontainer.find('span', class_='x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xjohtrz xo1l8bm xp07o12 x1yc453h')
                profile_data['bio'] = bio_text.get_text(strip=True)
            else:
                profile_data['bio'] = "Bio not found"
                return profile_data
        else:
            print(f"Failed to retrieve data for {username}")
            return None