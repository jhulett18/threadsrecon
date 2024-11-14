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


    def scroll_to_load_all_content(self):
        """Scroll down until all posts, replies, and reposts are loaded"""
        print("Starting to scroll and load content...")
        previous_content_count = 0
        same_count_iterations = 0
        max_same_count = 3

        while True:
            # Scroll to bottom
            self.driver.execute_script(
                "window.scrollTo(0, document.body.scrollHeight);"
            )
            time.sleep(2)

            # Wait for any new posts, replies, or reposts to load
            self.wait_for_content_to_load()

            # Get current content count (posts + replies + reposts)
            current_content_count = self.get_current_content_count()
            print(f"Loading more content...")

            if current_content_count == previous_content_count:
                same_count_iterations += 1
                if same_count_iterations >= max_same_count:
                    print("Reached the end of content or hit a limit")
                    break
            else:
                same_count_iterations = 0

            previous_content_count = current_content_count
            time.sleep(2)

    def wait_for_content_to_load(self):
        """Wait for posts, replies, and reposts to be present on the page"""
        try:
            self.wait.until(
                EC.presence_of_all_elements_located(
                    (By.CSS_SELECTOR, 'div[class*="x78zum5 xdt5ytf"]')
                )
            )
        except TimeoutException:
            print("Timeout waiting for content to load")

    def get_current_content_count(self):
        """Get the current number of posts, replies, and reposts loaded on the page"""
        posts = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="x78zum5 xdt5ytf"]')
        replies = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="x9f619 x1n2onr6 x1ja2u2z"]') 
        reposts = self.driver.find_elements(By.CSS_SELECTOR, 'div[class*="x78zum5 xdt5ytf"]')
        return len(posts) + len(replies) + len(reposts)


    def get_last_post_date(self):
        """Get the date of the most recent post using BeautifulSoup"""
        try:
            # Get current page source and parse with BeautifulSoup
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            
            # Find the first post
            posts = soup.find_all('div', class_='x78zum5 xdt5ytf')
            if posts:
                # Get the date from the first post
                first_post = posts[0]
                date_tag = first_post.find('time', class_='x1rg5ohu xnei2rj x2b8uid xuxw1ft')
                if date_tag and 'datetime' in date_tag.attrs:
                    return datetime.fromisoformat(date_tag['datetime'])
        except Exception as e:
            print(f"Error getting last post date: {str(e)}")
        return None

    def fetch_profile(self, username):
        url = f"{self.base_url}/@{username}"
        self.driver.get(url)
        time.sleep(1)

        profile_data = {'username': username}

        self.scroll_to_load_all_content()

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

        posts = soup.find_all('div', class_='x78zum5 xdt5ytf')
        num_posts =len(posts)
        profile_data['posts_count'] = num_posts
        print(f"Found {num_posts} posts")
        
        last_post_date = self.get_last_post_date()
        if last_post_date:
            profile_data['last_post_date(YYYY/DD/MM)'] = last_post_date
        if posts:
            last_post = posts[-1]
            last_date_tag = last_post.find('time', class_='x1rg5ohu xnei2rj x2b8uid xuxw1ft')
            if last_date_tag and 'datetime' in last_date_tag.attrs:
                first_post_date = datetime.fromisoformat(last_date_tag['datetime'])
                profile_data['first_post_date(YYYY/DD/MM)'] = first_post_date


        replies_url=f"{url}/replies"
        self.driver.get(replies_url)
        self.scroll_to_load_all_content()
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        replies = soup.find_all('div', class_='x9f619 x1n2onr6 x1ja2u2z')
        num_replies =len(replies)-1
        if num_replies == 0:
            profile_data['replies']="No replies found"
        else:
            profile_data['replies']=num_replies
        print(f"Found {num_replies} replies")



        reposts_url=f"{url}/reposts"
        self.driver.get(reposts_url)
        self.scroll_to_load_all_content()
        soup = BeautifulSoup(self.driver.page_source, 'html.parser')

        reposts = soup.find_all('div', class_='x78zum5 xdt5ytf')
        num_reposts =len(reposts)
        if num_reposts == 0:
            profile_data['reposts']="No reposts found"
        else:
            profile_data['reposts']=num_reposts
        print(f"Found {num_reposts} reposts")


        return profile_data
