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
    
    def __init__(self, base_url, chromedriver):
        self.base_url = base_url
        self.chrome_options = Options()
        self.chrome_options.add_argument('--headless=new')

        # Optimize performance
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-extensions')
        self.chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        self.chrome_options.add_argument('--disable-infobars')
        self.chrome_options.add_argument('--ignore-certificate-errors')
        self.chrome_options.add_argument('--disable-logging')
        self.chrome_options.add_argument('--disable-popup-blocking')
        self.chrome_options.add_argument('--enable-automation')
        self.chrome_options.add_argument('--window-size=1920,1080')
        self.chrome_options.add_argument('--start-maximized')
        self.chrome_options.add_argument('--incognito')
        self.chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
        )

        self.chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.chrome_options.add_experimental_option("useAutomationExtension", False)
        self.chrome_options.add_argument('--log-level=3')
        self.driver = webdriver.Chrome(service=Service(chromedriver), options=self.chrome_options)

        # Adjust WebDriver to appear more human
        self.driver.execute_cdp_cmd(
            "Network.setUserAgentOverride",
            {"userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36"},
        )
        self.driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        self.wait = WebDriverWait(self.driver, 20)
        self.is_logged_in = False

    def login(self, username, password):
        """Log into Threads using Instagram credentials with improved error handling"""
        if self.is_logged_in:
            return True

        try:
            # Handle cookies popup
            def handle_cookies():
                try:
                    print("Looking for the Accept Cookies button...")
                    accept_cookies_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//div[text()='Allow all cookies']"))
                    )
                    accept_cookies_button.click()
                    print("Accepted cookies")
                except Exception as e:
                    print(f"Could not find or click the Accept Cookies button: {str(e)}")
                    self.driver.save_screenshot("accept_cookies_error.png")

            # Check if credentials are provided
            if username is None or password is None:
                print("Attempting anonymous access...")
                self.driver.get(self.base_url + "/login/")
                time.sleep(2)
                handle_cookies()

                try:
                    print("Selecting 'Use without a profile'...")
                    use_without_profile_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//a[@href='/nonconsent/']//span[text()='Use without a profile']"))
                    )
                    use_without_profile_button.click()
                    print("Successfully selected 'Use without a profile'")
                    self.is_logged_in = True
                    return True
                except Exception as e:
                    print(f"Failed to select 'Use without a profile': {str(e)}")
                    self.driver.save_screenshot("use_without_profile_error.png")
                    return False

                # Select "Use without a profile"
                try:
                    print("Selecting 'Use without a profile'...")
                    use_without_profile_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//div[text()='Use without a profile']"))
                    )
                    use_without_profile_button.click()
                    print("Successfully selected 'Use without a profile'")
                    self.is_logged_in = True
                    return True
                except Exception as e:
                    print(f"Failed to select 'Use without a profile': {str(e)}")
                    self.driver.save_screenshot("use_without_profile_error.png")
                    return False

            print("Attempting to log in...")
            self.driver.get(self.base_url + "/login/?show_choice_screen=false")
            time.sleep(2)
            handle_cookies()

            # Navigate to the login form
            try:
                login_div = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Log in')]")))
                login_div.click()
                print("Clicked login div, redirecting to login page...")
            except Exception as e:
                print(f"Failed to click the login div: {str(e)}")
                self.driver.save_screenshot("login_div_error.png")
                return False

            # Fill in username
            try:
                print("Waiting for login form...")
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username, phone or email']"))
                )
                print("Found username input")
                username_input.clear()
                username_input.send_keys(username)
                time.sleep(1)
            except Exception as e:
                print(f"Error locating or filling the username input: {str(e)}")
                self.driver.save_screenshot("username_input_error.png")
                return False

            # Fill in password
            try:
                print("Entering password...")
                password_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
                )
                password_input.clear()
                password_input.send_keys(password + Keys.RETURN)  # Press Enter to submit
                time.sleep(2)
            except Exception as e:
                print(f"Error entering password or submitting form: {str(e)}")
                self.driver.save_screenshot("password_submit_error.png")
                return False

            # Verify login success or detect 2FA
            try:
                print("Checking login success...")
                if self.wait.until(
                    EC.any_of(
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Search']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "svg[aria-label='Home']")),
                        EC.presence_of_element_located((By.CSS_SELECTOR, "input[placeholder='Search']"))
                    )
                ):
                    print("Login successful!")
                    self.is_logged_in = True
                    return True
            except TimeoutException:
                # Check for 2FA prompt
                try:
                    print("Login not confirmed. Checking for 2FA prompt...")
                    if self.wait.until(
                        EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Security code']"))
                    ):
                        print("2FA detected. Use an account with 2FA disabled for this script.")
                        return False
                except TimeoutException:
                    print("No 2FA prompt detected. Login failed.")
                except Exception as e:
                    print(f"Unexpected error during 2FA detection: {str(e)}")

            # If neither login success nor 2FA detected, assume login failed
            print("Login failed.")
            self.driver.save_screenshot("login_failure.png")
            return False

        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.save_screenshot("login_failed_error.png")
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


    def fetch_profile(self, username):
        url = f"{self.base_url}/@{username}"
        self.driver.get(url)
        time.sleep(3)

        self.scroll_to_load_all_content()

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')    
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
                profile_data['followers'] = followers_text.get_text(strip=True).replace('followers', '').strip()
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
        

        first_post_date = None
        last_post_date = None
        # Iterate over each post and extract the date
        for post in posts:
            date_tag = post.find('time', class_='x1rg5ohu xnei2rj x2b8uid xuxw1ft') 
            if date_tag:
                # Extract the date (assuming it's in a recognizable format)
                post_date = date_tag['datetime']  # or date_tag.text if the date is in text format
                post_date_obj = datetime.fromisoformat(post_date)  # Parse the date to a datetime object

                # Update first and last post dates
                if first_post_date is None or post_date_obj < first_post_date:
                    first_post_date = post_date_obj
                    profile_data['first_post_date(YYYY/DD/MM)']=first_post_date
                if last_post_date is None or post_date_obj > last_post_date:
                    last_post_date = post_date_obj
                    profile_data['last_post_date(YYYY/DD/MM)']=last_post_date


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