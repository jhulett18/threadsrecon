from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import time

class ThreadsScraper:
    def __init__(self, base_url):
        self.base_url = base_url
        # Set up Chrome options
        self.chrome_options = Options()
        #self.chrome_options.add_argument('--headless')  # Run in headless mode
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36')
        
        self.driver = webdriver.Chrome(service=Service('chromedriver'),options=self.chrome_options)
        self.wait = WebDriverWait(self.driver, 20)
        self.is_logged_in = False

    def login(self, username, password):
        """Log into Threads using Instagram credentials with improved error handling"""
        if self.is_logged_in:
            return True

        try:
            print("Attempting to log in...")
            # Go directly to Instagram login page
            self.driver.get("https://threads.net/login/")
            time.sleep(5)  # Wait for page to fully load

            try:
                print("Looking for the Accept Cookies button...")
                accept_cookies_button = self.wait.until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "div[class*='x1i10hfl x1ypdohk x2lah0s xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r x2lwn1j xexx8yu x18d9i69 x1n2onr6 x16tdsg8 x1hl2dhg xggy1nq x1ja2u2z x1t137rt x1q0g3np x1lku1pv x1a2a7pz x6s0dn4 x1a2cdl4 xnhgr82 x1qt0ttw xgk8upj x9f619 x3nfvp2 x1s688f x90ne7k xl56j7k x193iq5w x1swvt13 x1pi30zi x12w9bfk x1g2r6go x11xpdln xz4gly6 x87ps6o xuxw1ft x19kf12q x111bo7f x1vmvj1k x45e8q x3tjt7u x35z2i1 x13fuv20 xu3j5b3 x1q0q8m5 x26u7qi x178xt8z xm81vs4 xso031l xy80clv xteu7em x11r8ahe x1iyjqo2 x15x72sd']"))
                )
                accept_cookies_button.click()
                print("Accepted cookies")
            except Exception as e:
                print(f"No Accept Cookies button found or failed to click: {str(e)}")

            login_div = self.wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "div.x78zum5.xdt5ytf.xgpatz3.xyamay9")))
            login_div.click()
            print("Clicked login div, redirecting to login page...")
            
            print("Waiting for login form...")
            # Wait for and fill in username
            username_input = self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[value='']"))
            )
            print("Found username input")
            username_input.clear()
            username_input.send_keys(username)
            time.sleep(1)

            # Fill in password
            print("Entering password...")
            password_input = self.driver.find_element(By.CSS_SELECTOR, "input[value='']")
            password_input.clear()
            password_input.send_keys(password)
            time.sleep(1)

            # Try multiple methods to submit the login form
            password_input.send_keys(Keys.RETURN)  # This submits the form by pressing Enter
            print("Login attempt submitted by pressing Enter")
            time.sleep(3)  # Wait for login to complete

            # Wait for login to complete
            print("Waiting for login to complete...")
            time.sleep(3)

            # Check for successful login
            try:
                # Try to find elements that would indicate successful login
                self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Search']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']"))
                    )
                )
                print("Login successful!")
                self.is_logged_in = True
                return True
            except TimeoutException:
                print("Could not verify login success")
                return False

        except Exception as e:
            print(f"Login failed: {str(e)}")
            return False
    def extract_post_data(self, post_element):
        """Extract data from a post element"""
        try:
            text_element = post_element.find('div', class_='x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7')
            text = text_element.get_text(strip=True) if text_element else ""
            
            date_element = post_element.find('time')
            date_posted = date_element.get('datetime') if date_element else ""
            
            return {
                "text": text,
                "date_posted": date_posted
            }
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

    def extract_reply_data(self, reply_element):
        """Extract data from a reply element"""
        try:
            text_element = reply_element.find('div', class_='x1a2a7pz x1n2onr6')
            text = text_element.get_text(strip=True) if text_element else ""
            
            date_element = reply_element.find('time')
            date_posted = date_element.get('datetime') if date_element else ""
            
            original_post = reply_element.find('div', class_='x1xdureb xkbb5z x13vxnyz')
            original_post_data = self.extract_post_data(original_post) if original_post else None
            
            return {
                "text": text,
                "date_posted": date_posted,
                "original_post": original_post_data
            }
        except Exception as e:
            print(f"Error extracting reply data: {str(e)}")
            return None

    def extract_repost_data(self, repost_element):
        """Extract data from a repost element"""
        try:
            text_element = repost_element.find('div', class_='x1a6qonq x6ikm8r x10wlt62 xj0a0fe x126k92a x6prxxf x7r5mf7')
            text = text_element.get_text(strip=True) if text_element else ""
            
            date_element = repost_element.find('time')
            date_posted = date_element.get('datetime') if date_element else ""
            
            original_poster_element = repost_element.find('a', class_='x1i10hfl xjbqb8w x1ejq31n xd10rxx x1sy0etr x17r0tee x972fbf xcfux6l x1qhh985 xm0m39n x9f619 x1ypdohk xt0psk2 xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz xp07o12 xzmqwrg x1citr7e x1kdxza xt0b8zv')
            original_poster = original_poster_element.get_text(strip=True) if original_poster_element else ""
            
            return {
                "text": text,
                "date_posted": date_posted,
                "original_poster": original_poster
            }
        except Exception as e:
            print(f"Error extracting repost data: {str(e)}")
            return None

    def scroll_and_collect_content(self, content_type='posts'):
        """Scroll and collect content with progress tracking"""
        print(f"Starting to collect {content_type}...")
        previous_content_count = 0
        same_count_iterations = 0
        max_same_count = 3
        collected_content = {}
        content_index = 1

        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            if content_type == 'posts':
                elements = soup.find_all('div', class_='x78zum5 xdt5ytf')
                for element in elements[len(collected_content):]:
                    post_data = self.extract_post_data(element)
                    if post_data:
                        collected_content[f"post {content_index}"] = post_data
                        content_index += 1
                        
            elif content_type == 'replies':
                elements = soup.find_all('div', class_='x9f619 x1n2onr6 x1ja2u2z')
                for element in elements[len(collected_content):]:
                    reply_data = self.extract_reply_data(element)
                    if reply_data:
                        collected_content[f"reply {content_index}"] = reply_data
                        content_index += 1
                        
            elif content_type == 'reposts':
                elements = soup.find_all('div', class_='x78zum5 xdt5ytf')
                for element in elements[len(collected_content):]:
                    repost_data = self.extract_repost_data(element)
                    if repost_data:
                        collected_content[f"repost {content_index}"] = repost_data
                        content_index += 1

            current_content_count = len(elements)
            print(f"Found {len(collected_content)} {content_type} so far...")

            if current_content_count == previous_content_count:
                same_count_iterations += 1
                if same_count_iterations >= max_same_count:
                    break
            else:
                same_count_iterations = 0

            previous_content_count = current_content_count
            time.sleep(2)

        return collected_content


    def fetch_profile(self, username):
        url = f"{self.base_url}/@{username}"

        profile_data = {username: {
            "username": username,
            "name": "",
            "profile_picture": "",
            "bio": "",
            "followers": "",
            "external_links": "",
            "instagram": "",
            "posts_count": 0,
            "posts": {},
            "replies_count": 0,
            "replies": {},
            "reposts_count": 0,
            "reposts": {}
        }}

        self.driver.get(url)
        time.sleep(1)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')    

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

        # Collect posts
        print("Collecting posts...")
        posts = self.scroll_and_collect_content('posts')
        profile_data[username]["posts"] = posts
        profile_data[username]["posts_count"] = len(posts)

        # Collect replies
        print("Collecting replies...")
        self.driver.get(f"{url}/replies")
        time.sleep(2)
        replies = self.scroll_and_collect_content('replies')
        profile_data[username]["replies"] = replies
        profile_data[username]["replies_count"] = len(replies)

        # Collect reposts
        print("Collecting reposts...")
        self.driver.get(f"{url}/reposts")
        time.sleep(2)
        reposts = self.scroll_and_collect_content('reposts')
        profile_data[username]["reposts"] = reposts
        profile_data[username]["reposts_count"] = len(reposts)


        return profile_data
