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
import random

class ThreadsScraper:
    
    def __init__(self, base_url, chromedriver):
        self.base_url = base_url
        self.chrome_options = Options()
        #self.chrome_options.add_argument('--headless=new')

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
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
        ]
        self.chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')

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

                # Check for automated behavior warning
                try:
                    print("Checking for automated behavior warning...")
                    dismiss_button = self.wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, "div[role='button'][aria-label='Dismiss']"))
                    )
                    dismiss_button.click()
                    print("Dismissed automated behavior warning")
                    self.is_logged_in = True
                    return True
                except Exception as e:
                    print(f"No automated behavior warning found or could not dismiss: {str(e)}")
                
                return False
            # If neither login success nor 2FA detected, assume login failed
            print("Login failed.")
            self.driver.save_screenshot("login_failure.png")
            return False

        except Exception as e:
            print(f"Login failed: {str(e)}")
            self.driver.save_screenshot("login_failed_error.png")
            return False
    
    
    def extract_post_data(self, post_element):
        """Extract data from a post element"""
        try:
            # Find the main text container without relying on specific class names
            text_container = post_element.find('div', recursive=False)


            post_cleaned, post_metadata = self.clean_and_extract_metadata(text_container)

                # Extract the date from the `time` element
            date_element = post_element.find('time')
            date_posted = date_element.get('datetime') if date_element else ""

            return {
                "text": post_cleaned,
                "date_posted": date_posted,
                "metadata": post_metadata
            }
        except Exception as e:
            print(f"Error extracting post data: {str(e)}")
            return None

    def extract_reply_data(self, reply_element):
        """Extract data from a reply element including both original post and reply"""
        try:
            # Find all divs that could contain post content
            content_divs = reply_element.find_all('div', attrs={"data-pressable-container":"true"})

            if len(content_divs) < 2:
                print("Warning: Could not find both original post and reply divs")
                return None

            # Extract data from original post (first div)
            original_post_div = content_divs[0]
            original_post_text = original_post_div.find('div', recursive=False)
            original_post_date = original_post_div.find('time')
            original_post_author = original_post_div.find('a', href=True) 

            # Clean and extract metadata from the original post text
            original_post_cleaned, original_metadata = self.clean_and_extract_metadata(original_post_text)

            # Extract data from reply (second div)
            reply_div = content_divs[1]
            reply_text = reply_div.find('div', recursive=False)
            reply_date = reply_div.find('time')

            # Clean and extract metadata from the reply text
            reply_cleaned, reply_metadata = self.clean_and_extract_metadata(reply_text)

            return {
                "original_post": {
                    "text": original_post_cleaned,
                    "date_posted": original_post_date.get('datetime') if original_post_date else "",
                    "author": original_post_author.get_text(strip=True) if original_post_author else "",
                    "metadata": original_metadata
                },
                "reply": {
                    "text": reply_cleaned,
                    "date_posted": reply_date.get('datetime') if reply_date else "",
                    "metadata": reply_metadata
                }
            }

        except Exception as e:
            print(f"Error extracting reply data: {str(e)}")
            return None

    def extract_repost_data(self, repost_element):
        """Extract data from a repost element"""
        try:
            # Find the main text container without relying on specific class names 
            text_container = repost_element.find('div', recursive=False)
            
           
            reply_cleaned, reply_metadata = self.clean_and_extract_metadata(text_container)

                # Extract date
            date_element = repost_element.find('time')
            date_posted = date_element.get('datetime') if date_element else ""

            return {
                "text": reply_cleaned,
                "date_posted": date_posted,
                "metadata": reply_metadata
            }

        except Exception as e:
            print(f"Error extracting repost data: {str(e)}")
            return None
        return None
    
    def clean_and_extract_metadata(self, text_element):
        """Cleans text and extracts metadata"""
        if not text_element:
            return "", ""

        raw_text = text_element.get_text(separator=" ", strip=True)

        # Split into main text and metadata if "Like" is present
        if " Like " in raw_text:
            main_text, metadata = raw_text.rsplit(" Like ", 1)
            metadata = f"Like {metadata.strip()}"
        else:
            main_text, metadata = raw_text, ""

        # Remove unwanted prefixes from the main text
        start_keywords = ["Follow", "More"]
        cleaned_text = main_text  # Focus only on the main post text

        for keyword in start_keywords:
            if keyword in cleaned_text:
                cleaned_text = cleaned_text.split(keyword, 1)[-1]

        return cleaned_text.strip(), metadata.strip()

    def scroll_and_collect_content(self, content_type='posts'):
        """Scroll and collect content with progress tracking"""
        print(f"Starting to collect {content_type}...")
        same_count_iterations = 0
        max_same_count = 3
        processed_timestamps = set()  # Track unique timestamps
        collected_content = {}
        content_index = 1
        
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)
            
            # XPath patterns for different content types
            # Replies maybe work maybe not, cant see because cba making a new account
            xpath_patterns = {
                'posts': """//div[
                    .//img[contains(@alt, 'profile picture')] and
                    .//time and
                    .//span[@dir='auto']
                ]""",
                'replies': """//div[
                    .//img[contains(@alt, 'profile picture')] and
                    .//time and
                    .//span[@dir='auto'] and
                    .//div[@style='--lpa98a5]']
                ]""",
                'reposts': """//div[
                    .//img[contains(@alt, 'profile picture')] and
                    .//time and
                    .//span[@dir='auto']
                ]"""
            }
            
            elements = self.driver.find_elements('xpath', xpath_patterns[content_type])
            
            new_elements = []
            for element in elements:
                try:
                    # Get timestamp and username to create a unique identifier
                    timestamp = element.find_element('xpath', './/time').get_attribute('datetime')
                    username = element.find_element('xpath', ".//span[contains(@dir, 'auto')]").text
                    unique_id = f"{timestamp}_{username}"
                    
                    if unique_id not in processed_timestamps:
                        new_elements.append(element)
                        processed_timestamps.add(unique_id)
                except Exception as e:
                    print(f"Error getting identifier: {str(e)}")
                    continue
            
            if not new_elements:
                same_count_iterations += 1
                if same_count_iterations >= max_same_count:
                    break
            else:
                same_count_iterations = 0
            
            for element in new_elements:
                try:
                    soup_element = BeautifulSoup(element.get_attribute('outerHTML'), 'html.parser')
                    
                    # Extract data based on content type
                    content_data = None
                    if content_type == 'posts':
                        content_data = self.extract_post_data(soup_element)
                    elif content_type == 'replies':
                        content_data = self.extract_reply_data(soup_element)
                    else:  # reposts
                        content_data = self.extract_repost_data(soup_element)
                    
                    if content_data and content_data.get('text'):  # Only add if we have meaningful content
                        collected_content[f"{content_type[:-1]} {content_index}"] = content_data
                        content_index += 1
                        print(f"Added new {content_type[:-1]}: {content_data['text'][:100]}...")  # Debug print
                    
                except Exception as e:
                    print(f"Error processing element: {str(e)}")
            
            print(f"Found {len(collected_content)} {content_type} so far...")
            time.sleep(2)
        
        return collected_content
        
    def fetch_profile(self, username):
        url = f"{self.base_url}/@{username}"
        profile_data = {
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
        }
        self.driver.get(url)
        time.sleep(2)

        soup = BeautifulSoup(self.driver.page_source, 'html.parser')    
        
        name = soup.find('h1', {"dir": "auto"})
        if name:
            profile_data['name'] = name.get_text(strip=True)
        else:
            profile_data['name'] = "Name not found"
        
        
        profile_picture = soup.find('meta',{'property':'og:image'})
        if profile_picture:
            image_url = profile_picture.get('content')
            if image_url:
                profile_data['profile_picture'] = image_url
            else:
                profile_data['profile_picture'] = "Profile picture not found"
        else:
            profile_data['profile_picture'] = "Profile picture not found"
        
        
        bio = self.driver.find_element(By.XPATH, '(//span[@dir="auto"])[4]')
        if bio:
                profile_data['bio'] = bio.text.strip()
        else:
                profile_data['bio'] = "Bio not found"
        
        
        followers = self.driver.find_element(By.XPATH, '(//span[@dir="auto"])[5]')
        if followers:
                profile_data['followers'] = followers.text.strip().replace('followers', '').strip()
        else:
                profile_data['followers'] = "Followers not found"
        
        
        external_links = soup.find_all('link', {"rel": "me"}) 
        if external_links:
                profile_data['external_links'] = [link.get('href') for link in external_links]
        else:
                profile_data['external_links'] = "External links not found"
        
        try:
            instagram = self.driver.find_element(By.XPATH, '//a[contains(@href, "threads.net") and contains(@href, "instagram.com")]')
            if instagram:
                instagram_url = instagram.get_attribute('href')
                if 'u=' in instagram_url:
                    parsed_url = urlparse(instagram_url)
                    query_params = parse_qs(parsed_url.query)
                    instagram_url = query_params.get('u', [None])[0]
                    if instagram_url:
                        profile_data['instagram'] = unquote(instagram_url)
                    else:
                        profile_data['instagram'] = "Instagram URL not found in 'u' parameter"
                else:
                    profile_data['instagram'] = instagram_url
        except Exception as e:
            print(f"Instagram link not found: {str(e)}")
            profile_data['instagram'] = "Instagram link not found"
        '''
         # Collect posts
        print("Collecting posts...")
        posts = self.scroll_and_collect_content('posts')
        profile_data["posts"] = posts
        profile_data["posts_count"] = len(posts)
        '''
        # Collect replies
        print("Collecting replies...")
        self.driver.get(f"{url}/replies")
        time.sleep(2)
        replies = self.scroll_and_collect_content('replies')
        profile_data["replies"] = replies
        profile_data["replies_count"] = len(replies)
        '''
        # Collect reposts
        print("Collecting reposts...")
        self.driver.get(f"{url}/reposts")
        time.sleep(2)
        reposts = self.scroll_and_collect_content('reposts')
        profile_data["reposts"] = reposts
        profile_data["reposts_count"] = len(reposts)
        '''
        return {username: profile_data}