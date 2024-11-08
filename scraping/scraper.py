from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime

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


        name = soup.find('h1', class_='x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye x133cpev x1xlr1w8 xp07o12 x1yc453h')
        if name:
            profile_data['name'] = name.get_text(strip=True)
        else:
            profile_data['name'] = "Name not found"



        profile_picture = soup.find('img', class_='xl1xv1r x14yjl9h xudhj91 x18nykt9 xww2gxu xvapks4 x1bgq0ue')
        if profile_picture:
            image_url = profile_picture.get('src')
            if image_url:
                profile_data['profile_picture'] = image_url
            else:
                profile_data['profile_picture'] = "Profile picture not found"
        else:
            profile_data['profile_picture'] = "Profile picture not found"



        bio_container = soup.find('div', class_='x17zef60')
        if bio_container:
            bio_text = bio_container.find('span', class_='x1lliihq')
            if bio_text:
                profile_data['bio'] = bio_text.get_text(strip=True)
            else:
                profile_data['bio'] = "Bio not found"
        else:
            profile_data['bio'] = "Bio not found"
        


        followers = soup.find('div', class_='x78zum5 x2lah0s')
        if followers:
            followers_text = followers.find('span', class_='x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xjohtrz xo1l8bm x12rw4y6 x1yc453h')
            if followers_text:
                profile_data['followers'] = followers_text.get_text(strip=True)
            else:
                profile_data['followers'] = "Followers not found"



        external = soup.find('div', class_='x1iyjqo2 xeuugli')
        if external:
            external_text = external.find('span', class_='x1lliihq x1plvlek xryxfnj x1n2onr6 x1ji0vk5 x18bv5gf x193iq5w xeuugli x1fj9vlw x13faqbe x1vvkbs x1s928wv xhkezso x1gmr53x x1cpjm7i x1fgarty x1943h6x x1i0vuye xjohtrz xo1l8bm x12rw4y6 x1yc453h')
            if external_text:
                profile_data['external_links'] = external_text.get_text(strip=True)
            else:
                profile_data['external_links'] = "External links not found"


        
        instagram = soup.find('div', class_='x6s0dn4 x78zum5 x1c4vz4f xykv574 x1i64zmx')
        if instagram:
            # Find the anchor tag with the Instagram profile link (assuming this structure)
            anchor_tag = instagram.find('a', href=True)

            if anchor_tag:
                # Extract the Instagram URL from the 'href' attribute
                instagram_url = anchor_tag['href']
                
                # Check if the URL contains query parameters
                if 'u=' in instagram_url:
                    # Parse the URL and decode the 'u' parameter
                    parsed_url = urlparse(instagram_url)
                    query_params = parse_qs(parsed_url.query)

                    # Extract the Instagram URL from the 'u' parameter and decode it
                    instagram_url = query_params.get('u', [None])[0]
                    if instagram_url:
                        cleaned_url = unquote(instagram_url)  # Decode the URL-encoded string
                        profile_data['instagram'] = cleaned_url
                    else:
                        profile_data['instagram'] = "Instagram URL not found in 'u' parameter"
                else:
                    # If the URL doesn't have query params, directly use the href
                    profile_data['instagram_link'] = instagram_url
            else:
                profile_data['instagram_link'] = "Instagram link not found"
        else:
            profile_data['instagram_link'] = "Instagram container not found"


        
        posts = soup.find_all('div', class_='x78zum5 xdt5ytf')
        num_posts =len(posts)
        if num_posts == 0:
            profile_data['posts']="Nothing posted"
        else:
            profile_data['posts']=num_posts
        


        first_post_date = None
        last_post_date = None
        # Iterate over each post and extract the date
        for post in posts:
            # Assuming the date is in a tag with a specific class (you may need to adjust this)
            date_tag = post.find('time', class_='x1rg5ohu xnei2rj x2b8uid xuxw1ft') 
            if date_tag:
                # Extract the date (assuming it's in a recognizable format)
                post_date = date_tag['datetime']  # or date_tag.text if the date is in text format
                post_date_obj = datetime.fromisoformat(post_date)  # Parse the date to a datetime object

                # Update first and last post dates
                if first_post_date is None or post_date_obj < first_post_date:
                    first_post_date = post_date_obj
                    profile_data['first_post_date']=first_post_date
                if last_post_date is None or post_date_obj > last_post_date:
                    last_post_date = post_date_obj
                    profile_data['last_post_date']=last_post_date

        return profile_data
