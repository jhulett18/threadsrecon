"""
Threads Scraper Module

This module provides functionality for scraping data from Threads.net.
Features:
- Error handling with custom exceptions
- Rate limiting and retry logic
- Configurable browser options
- Session management and authentication
- Anonymous access support
"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import (
    TimeoutException, 
    NoSuchElementException, 
    ElementClickInterceptedException,
    StaleElementReferenceException,
    WebDriverException
)
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs, unquote
from datetime import datetime
import time
import random
import os
import requests
from urllib3.exceptions import MaxRetryError
from requests.exceptions import RequestException
from concurrent.futures import ThreadPoolExecutor
from config.config_manager import ConfigManager


class ThreadsScraperException(Exception):
    """
    Custom exception class for handling Threads.net scraping errors
    
    Provides detailed error messages for different types of failures:
    - Network errors (timeouts, connection issues)
    - Authentication errors
    - Page structure changes
    - Element interaction failures
    """
    
    def handle_http_error(self, url, error):
        """
        Handle HTTP-related errors with specific error messages
        
        Args:
            url (str): The URL being accessed when the error occurred
            error (Exception): The original exception that was raised
            
        Raises:
            ThreadsScraperException: With a detailed error message based on the error type
            
        Note:
            Handles various network-related errors including:
            - Timeouts
            - DNS resolution failures
            - Connection refusals
            - Proxy errors
            - Redirect loops
        """
        error_msg = str(error)
        
        if isinstance(error, TimeoutException):
            raise ThreadsScraperException(
                f"Timeout while accessing {url}. The server took too long to respond."
            )
        elif isinstance(error, WebDriverException):
            # Handle different types of network errors
            if "net::ERR_CONNECTION_TIMED_OUT" in error_msg:
                raise ThreadsScraperException(
                    f"Connection timed out while accessing {url}. Please check your internet connection."
                )
            elif "net::ERR_NAME_NOT_RESOLVED" in error_msg:
                raise ThreadsScraperException(
                    f"Could not resolve the host name for {url}. Please check the URL."
                )
            elif "net::ERR_CONNECTION_REFUSED" in error_msg:
                raise ThreadsScraperException(
                    f"Connection refused by {url}. The server might be down or blocking requests."
                )
            elif "net::ERR_PROXY_CONNECTION_FAILED" in error_msg:
                raise ThreadsScraperException(
                    f"Proxy connection failed while accessing {url}. Please check your proxy settings."
                )
            elif "net::ERR_TOO_MANY_REDIRECTS" in error_msg:
                raise ThreadsScraperException(
                    f"Too many redirects while accessing {url}. The page might be in a redirect loop."
                )
        elif isinstance(error, NoSuchElementException):
            raise ThreadsScraperException(
                f"Required element not found on {url}. The page structure might have changed."
            )
        elif isinstance(error, ElementClickInterceptedException):
            raise ThreadsScraperException(
                f"Could not interact with element on {url}. Element might be obscured or not clickable."
            )
        elif isinstance(error, StaleElementReferenceException):
            raise ThreadsScraperException(
                f"Element is no longer attached to the DOM at {url}. Page might have been updated."
            )
        
        raise ThreadsScraperException(f"Unexpected error while accessing {url}: {error_msg}")
    
    def check_connection(self, url):
        """
        Check if the website is accessible
        
        Args:
            url (str): URL to check
            
        Returns:
            bool: True if the website is accessible
            
        Raises:
            ThreadsScraperException: If the website cannot be accessed
            
        Note:
            Uses configured timeouts and waits for body element
        """
        try:
            self.driver.get(url)
            self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            return True
        except Exception as e:
            self.handle_http_error(url, e)
    
    def rate_limit(self):
        """
        Implement rate limiting between requests
        
        Uses configured delays to:
        - Prevent detection as a bot
        - Respect server rate limits
        - Add randomization to request timing
        """
        delays = self.config.get_delays()
        delay = random.uniform(delays['min_wait'], delays['max_wait'])
        time.sleep(delay)

    def retry_with_backoff(self, func, *args):
        """
        Retry a function with exponential backoff
        
        Args:
            func (callable): Function to retry
            *args: Arguments to pass to the function
            
        Returns:
            Any: Result of the successful function call
            
        Note:
            - Uses exponential backoff between retries
            - Configurable maximum attempts and initial delay
            - Handles specific exceptions for retry logic
        """
        retries = self.config.get_retries()
        for attempt in range(retries['max_attempts']):
            try:
                return func(*args)
            except (TimeoutException, WebDriverException) as e:
                if attempt == retries['max_attempts'] - 1:
                    self.handle_http_error(args[0] if args else "unknown URL", e)
                delay = retries['initial_delay'] * (2 ** attempt)
                print(f"Attempt {attempt + 1} failed, retrying in {delay} seconds...")
                time.sleep(delay)
    pass

class ThreadsScraper:
    """
    Main scraper class for Threads.net
    
    Handles:
    - Browser initialization and configuration
    - Authentication and session management
    - Content scraping and parsing
    - Rate limiting and retry logic
    
    Attributes:
        base_url (str): Base URL for Threads.net
        chrome_options (Options): Configured Chrome browser options
        is_logged_in (bool): Current login status
        config (ConfigManager): Configuration manager instance
    """
    
    def __init__(self, base_url, chromedriver_path, browser_path=None, debug=False):
        """
        Initialize the ThreadsScraper
        
        Args:
            base_url (str): Base URL for Threads.net
            chromedriver_path (str): Path to chromedriver executable
            browser_path (str, optional): Path to Chrome browser executable
            debug (bool): Enable detailed debug output
            
        Note:
            - Loads configuration from ConfigManager
            - Sets up browser options including:
                - Window size
                - Incognito mode
                - User agent rotation
                - Feature toggles
        """
        self.config = ConfigManager()
        self.base_url = base_url
        self.debug = debug
        self.chrome_options = Options()
        self.chrome_options.add_argument('--no-sandbox')
        self.chrome_options.add_argument('--headless=new')
        self.chrome_options.add_argument('--disable-dev-shm-usage')
        self.chrome_options.add_argument('--disable-gpu')
        self.chrome_options.add_argument('--disable-software-rasterizer')
        self.chrome_options.add_argument('--remote-debugging-port=9222')
        self.chrome_options.add_argument('--disable-setuid-sandbox')
        self.chrome_options.add_argument('--window-size=1920,1080')
        
        # Suppress Chrome debug output unless debug mode is enabled
        if not debug:
            self.chrome_options.add_argument('--log-level=3')  # Only fatal errors
            self.chrome_options.add_argument('--silent')
            self.chrome_options.add_argument('--disable-logging')
            self.chrome_options.add_argument('--disable-gpu-logging')
            self.chrome_options.add_argument('--disable-extensions-http-throttling')
            self.chrome_options.add_argument('--disable-background-timer-throttling')
            self.chrome_options.add_argument('--disable-renderer-backgrounding')
            self.chrome_options.add_argument('--disable-backgrounding-occluded-windows')
            self.chrome_options.add_experimental_option('excludeSwitches', ['enable-logging'])
            self.chrome_options.add_experimental_option('useAutomationExtension', False)
            
        # Additional Chrome performance options
        self.chrome_options.add_argument('--disable-web-security')
        self.chrome_options.add_argument('--disable-features=TranslateUI')
        self.chrome_options.add_argument('--disable-iframes-during-redirect')
        if browser_path:
            self.chrome_options.binary_location = browser_path
        self.is_logged_in = False
        
        # Get browser options from config
        browser_options = self.config.get_browser_options()
        window_size = browser_options.get('window_size', {'width': 1920, 'height': 1080})
        
        # Enable incognito mode for clean sessions
        self.chrome_options.add_argument('--incognito')
        
        # Set window size for consistent rendering
        self.chrome_options.add_argument(f'--window-size={window_size["width"]},{window_size["height"]}')
        
        # Disable specified features for better performance
        for feature in browser_options.get('disabled_features', []):
            if feature not in ['sandbox', 'dev-shm-usage', 'gpu']:  # Skip if already added
                self.chrome_options.add_argument(f'--disable-{feature}')
        
        # Rotate user agents to avoid detection
        user_agents = self.config.get_user_agents()
        if user_agents:
            self.chrome_options.add_argument(f'--user-agent={random.choice(user_agents)}')
            
        # Initialize WebDriver with configured timeouts
        timeouts = self.config.get_timeouts()
        
        # Show user-friendly connection message
        if not debug:
            print("🌐 Connecting to browser...")
            
        # Use automatic ChromeDriver management (Selenium 4 feature)
        if not chromedriver_path or chromedriver_path.lower() in ['auto', 'automatic', '']:
            # Let Selenium 4 automatically manage ChromeDriver
            self.driver = webdriver.Chrome(options=self.chrome_options)
        else:
            try:
                # Try using configured chromedriver path first
                self.driver = webdriver.Chrome(service=Service(chromedriver_path), options=self.chrome_options)
            except Exception as e:
                if debug:
                    print(f"ChromeDriver path failed, falling back to automatic management: {e}")
                # Fall back to automatic management
                self.driver = webdriver.Chrome(options=self.chrome_options)
        
        if not debug:
            print("✅ Browser connected successfully")
        self.wait = WebDriverWait(self.driver, timeouts['element_wait'])
        
    def login(self, username, password, skip_consent=False):
        """
        Log into Threads using Instagram credentials or handle anonymous access
        
        Args:
            username (str, optional): Instagram username
            password (str, optional): Instagram password
            
        Returns:
            bool: True if login successful, False otherwise
            
        Note:
            - Handles both authenticated and anonymous access
            - Manages cookie consent popups
            - Provides detailed error handling
            - Saves screenshots on failure for debugging
        """
        if self.is_logged_in:
            return True

        try:
            # Handle cookies popup with retry logic
            def handle_cookies():
                """
                Handle the cookie consent popup
                
                Attempts to find and click the accept button with:
                - Explicit wait for button presence
                - JavaScript click fallback
                - Screenshot capture on failure
                """
                if skip_consent:
                    print("Skipping cookie consent handling as requested")
                    return
                    
                try:
                    print("Looking for the Accept Cookies button...")
                    accept_cookies_button = self.wait.until(
                        EC.element_to_be_clickable((By.XPATH, "//div[text()='Allow all cookies']"))
                    )
                    self.driver.execute_script("arguments[0].click();", accept_cookies_button)
                    print("Accepted cookies")
                except TimeoutException:
                    if skip_consent:
                        print("Cookie consent timeout, but skip_consent is enabled - continuing")
                        return
                    raise ThreadsScraperException(
                        "Timeout while waiting for cookies popup. The page may not have loaded properly."
                    )
                except Exception as e:
                    if skip_consent:
                        print(f"Cookie consent error, but skip_consent is enabled - continuing: {str(e)}")
                        return
                    print(f"Could not find or click the Accept Cookies button: {str(e)}")
                    self.driver.save_screenshot("accept_cookies_error.png")

            # Handle anonymous access if no credentials provided
            if username is None or password is None:
                print("Attempting anonymous access...")
                try:
                    # Go directly to main page for anonymous browsing
                    self.driver.get(self.base_url)
                except WebDriverException as e:
                    raise ThreadsScraperException().handle_http_error(self.base_url, e)

                time.sleep(3)  # Allow page to stabilize
                handle_cookies()

                # Verify we can access the site anonymously
                try:
                    # Check if we successfully loaded the main page
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    print("Successfully accessed Threads anonymously")
                    self.is_logged_in = False
                    return True
                except TimeoutException:
                    raise ThreadsScraperException(
                        "Timeout while loading Threads main page. The site may be unavailable."
                    )
                except Exception as e:
                    print(f"Failed to access Threads anonymously: {str(e)}")
                    self.driver.save_screenshot("anonymous_access_error.png")
                    return False

            # Handle authenticated login
            print("Attempting to log in...")
            try:
                self.driver.get(self.base_url + "/login/?show_choice_screen=false")
            except WebDriverException as e:
                raise ThreadsScraperException().handle_http_error(self.base_url + "/login/", e)

            time.sleep(2)  # Allow page to stabilize
            handle_cookies()

            # Navigate through login form
            try:
                login_div = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//div[contains(text(), 'Log in')]")))
                self.driver.execute_script("arguments[0].scrollIntoView(true);", login_div)
                self.driver.execute_script("arguments[0].click();", login_div)
                print("Clicked login div, redirecting to login page...")
            except TimeoutException:
                raise ThreadsScraperException(
                    "Timeout while waiting for login button. The server might be slow or unresponsive."
                )
            except ElementClickInterceptedException:
                raise ThreadsScraperException(
                    "Could not click the login button. It might be covered by another element."
                )

            # Fill in login credentials
            try:
                print("Waiting for login form...")
                username_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Username, phone or email']"))
                )
                print("Found username input")
                username_input.clear()
                username_input.send_keys(username)
                time.sleep(1)  # Allow input to register
            except TimeoutException:
                raise ThreadsScraperException(
                    "Timeout while waiting for username input. The login form may not have loaded properly."
                )

            # Fill in password
            try:
                print("Entering password...")
                password_input = self.wait.until(
                    EC.presence_of_element_located((By.XPATH, "//input[@placeholder='Password']"))
                )
                password_input.clear()
                password_input.send_keys(password + Keys.RETURN)
                time.sleep(2)
            except TimeoutException:
                raise ThreadsScraperException(
                    "Timeout while waiting for password input. The login form may not have loaded properly."
                )
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
                # Check for specific error conditions
                if "checkpoint_required" in self.driver.current_url:
                    raise ThreadsScraperException(
                        "Account requires additional verification. Please log in manually first."
                    )
                elif "login_challenge" in self.driver.current_url:
                    raise ThreadsScraperException(
                        "Suspicious login attempt detected. Please verify your account manually."
                    )
                elif "blocked" in self.driver.current_url:
                    raise ThreadsScraperException(
                        "Account has been temporarily blocked. Please try again later."
                    )
                else:
                    raise ThreadsScraperException(
                        "Login failed. Please check your credentials and try again."
                    )

        except ThreadsScraperException as e:
            print(f"Login error: {str(e)}")
            self.driver.save_screenshot("login_error.png")
            raise
        except Exception as e:
            print(f"Unexpected error during login: {str(e)}")
            self.driver.save_screenshot("login_unexpected_error.png")
            raise ThreadsScraperException(f"Unexpected error during login: {str(e)}")

        return False
    
    def fetch_multiple_profiles(self, usernames, max_workers=5):
        """
        Fetch data for multiple profiles concurrently
        
        Args:
            usernames (list): List of usernames to fetch
            max_workers (int): Maximum number of concurrent workers
            
        Returns:
            dict: Combined profile data from all usernames
        """
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            results = executor.map(self.fetch_profile, usernames)
        return {k: v for result in results for k, v in result.items()}
    
    def extract_post_data(self, post_element):
        """
        Extract data from a post element
        
        Args:
            post_element (bs4.element.Tag): BeautifulSoup element representing a post
            
        Returns:
            dict: Extracted post data including:
                - Text content
                - Date posted
                - Metadata
        """
        try:
            # Find the main text container without relying on specific class names
            text_container = post_element.find('div', recursive=False)


            post_cleaned, post_metadata = self.clean_and_extract_metadata(text_container)

                # Extract the date from the `time` element
            date_element = post_element.find('time')
            date_posted = date_element.get('datetime') if date_element else ""

            # Extract media URLs from the post
            media_urls = self.extract_media_urls(post_element)

            return {
                "text": post_cleaned,
                "date_posted": date_posted,
                "metadata": post_metadata,
                "media_urls": media_urls
            }
        except Exception as e:
            error_msg = f"Error extracting post data: {str(e)}"
            print(error_msg)
            if self.debug:
                import traceback
                print(f"   └── Debug: {traceback.format_exc()}")
            return None

    def extract_reply_data(self, reply_element):
        """
        Extract data from a reply element including both original post and reply
        
        Args:
            reply_element (bs4.element.Tag): BeautifulSoup element representing a reply
            
        Returns:
            dict: Extracted reply data including:
                - Original post data
                - Reply data
        """
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
            error_msg = f"Error extracting reply data: {str(e)}"
            print(error_msg)
            if self.debug:
                import traceback
                print(f"   └── Debug: {traceback.format_exc()}")
            return None

    def extract_repost_data(self, repost_element):
        """
        Extract data from a repost element
        
        Args:
            repost_element (bs4.element.Tag): BeautifulSoup element representing a repost
            
        Returns:
            dict: Extracted repost data including:
                - Text content
                - Date posted
                - Metadata
        """
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

    def extract_follower_data(self, follower_element):
        """
        Extract username and display name from a follower element using robust selectors
        
        Args:
            follower_element (bs4.element.Tag): BeautifulSoup element representing a follower
            
        Returns:
            dict: Extracted follower data including:
                - Username
                - Display name
        """
        try:
            # Find link with role="link" and get the username from href
            link = follower_element.find('a', attrs={'role': 'link'})
            if not link:
                return None
            username = link['href'].strip('/@')
            
            # Find the display name by looking for the last span with dir="auto"
            spans = follower_element.find_all('span', attrs={'dir': 'auto'})
            name = None
            for span in spans:
                # Look for the span that has text and doesn't contain the username
                span_text = span.get_text(strip=True)
                if span_text and span_text != username:
                    name = span_text
                    break
            
            if username and name:
                return {
                    "username": username,
                    "name": name
                }
            return None
            
        except Exception as e:
            print(f"Error extracting follower data: {str(e)}")
            return None

    def clean_and_extract_metadata(self, text_element):
        """
        Cleans text and extracts metadata
        
        Args:
            text_element (bs4.element.Tag): BeautifulSoup element representing text to clean
            
        Returns:
            tuple: Cleaned text and extracted metadata
        """
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
    
    def extract_media_urls(self, element):
        """
        Extract image and video URLs from a post element using simple DOM parsing
        
        Args:
            element (bs4.element.Tag): BeautifulSoup element to extract media from
            
        Returns:
            list: List of media URLs found in the element
        """
        media_urls = []
        
        try:
            # Find all img tags
            images = element.find_all('img')
            for img in images:
                src = img.get('src')
                if src and self.is_valid_media_url(src, 'image'):
                    media_urls.append(src)
            
            # Find all video tags and their sources
            videos = element.find_all('video')
            for video in videos:
                src = video.get('src')
                if src and self.is_valid_media_url(src, 'video'):
                    media_urls.append(src)
                
                # Check for source tags within video
                sources = video.find_all('source')
                for source in sources:
                    src = source.get('src')
                    if src and self.is_valid_media_url(src, 'video'):
                        media_urls.append(src)
            
            # Look for background images in style attributes
            elements_with_style = element.find_all(attrs={'style': True})
            for elem in elements_with_style:
                style = elem.get('style', '')
                if 'background-image' in style:
                    # Extract URL from background-image: url(...)
                    import re
                    matches = re.findall(r'background-image:\s*url\(["\']?([^"\']+)["\']?\)', style)
                    for match in matches:
                        if self.is_valid_media_url(match, 'image'):
                            media_urls.append(match)
                            
        except Exception as e:
            print(f"Error extracting media URLs: {e}")
        
        return media_urls
    
    def is_valid_media_url(self, url, media_type):
        """
        Check if a URL is a valid media URL
        
        Args:
            url (str): URL to check
            media_type (str): 'image' or 'video'
            
        Returns:
            bool: True if valid media URL
        """
        if not url or url.startswith('data:') or url.startswith('#'):
            return False
        
        # Common image extensions
        image_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp']
        video_extensions = ['.mp4', '.webm', '.mov', '.avi']
        
        url_lower = url.lower()
        
        if media_type == 'image':
            return any(ext in url_lower for ext in image_extensions) or 'image' in url_lower
        elif media_type == 'video':
            return any(ext in url_lower for ext in video_extensions) or 'video' in url_lower
        
        return False
    
    def create_user_media_folder(self, username):
        """
        Create folder structure for storing user media
        
        Args:
            username (str): Username to create folders for
            
        Returns:
            tuple: (images_folder, videos_folder)
        """
        base_folder = os.path.join("data", "users", username)
        images_folder = os.path.join(base_folder, "images")
        videos_folder = os.path.join(base_folder, "videos")
        
        # Create directories if they don't exist
        os.makedirs(images_folder, exist_ok=True)
        os.makedirs(videos_folder, exist_ok=True)
        
        return images_folder, videos_folder
    
    def download_media_file(self, url, folder, filename_prefix="media"):
        """
        Download a media file using requests
        
        Args:
            url (str): URL to download
            folder (str): Destination folder
            filename_prefix (str): Prefix for the filename
            
        Returns:
            str: Path to downloaded file or None if failed
        """
        try:
            # Generate filename from URL
            parsed_url = urlparse(url)
            original_filename = os.path.basename(parsed_url.path)
            
            # If no filename or extension, generate one
            if not original_filename or '.' not in original_filename:
                if 'image' in url.lower() or any(ext in url.lower() for ext in ['.jpg', '.png', '.gif']):
                    extension = '.jpg'
                else:
                    extension = '.mp4'
                original_filename = f"{filename_prefix}_{hash(url) % 10000}{extension}"
            
            file_path = os.path.join(folder, original_filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                return {
                    'status': 'exists',
                    'filename': original_filename,
                    'path': file_path,
                    'url': url
                }
            
            # Download the file
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            
            return {
                'status': 'success',
                'filename': original_filename,
                'path': file_path,
                'url': url
            }
            
        except Exception as e:
            error_msg = str(e)
            if self.debug:
                import traceback
                error_msg = f"{error_msg}\n{traceback.format_exc()}"
                
            return {
                'status': 'failed',
                'filename': original_filename if 'original_filename' in locals() else 'unknown',
                'error': error_msg,
                'url': url
            }
    
    def collect_and_download_media(self, username, posts_data):
        """
        Collect and download all media from posts data
        
        Args:
            username (str): Username for folder organization
            posts_data (dict): Posts data containing media URLs
            
        Returns:
            dict: Summary of downloaded media
        """
        print(f"🎬 Starting media collection for {username}")
        
        # Create folders
        images_folder, videos_folder = self.create_user_media_folder(username)
        
        # Track download results
        download_results = {
            'success': {'images': [], 'videos': []},
            'exists': {'images': [], 'videos': []},
            'failed': {'images': [], 'videos': []}
        }
        
        for post_key, post_data in posts_data.items():
            media_urls = post_data.get('media_urls', [])
            
            for url in media_urls:
                if self.is_valid_media_url(url, 'image'):
                    result = self.download_media_file(url, images_folder, f"post_{post_key}_image")
                    if isinstance(result, dict):
                        media_type = 'images'
                        if result['status'] == 'success':
                            download_results['success'][media_type].append(result['path'])
                        elif result['status'] == 'exists':
                            download_results['exists'][media_type].append(result['path'])
                        elif result['status'] == 'failed':
                            download_results['failed'][media_type].append(result)
                    else:
                        # Legacy support - if result is a path string
                        if result:
                            download_results['success']['images'].append(result)
                            
                elif self.is_valid_media_url(url, 'video'):
                    result = self.download_media_file(url, videos_folder, f"post_{post_key}_video")
                    if isinstance(result, dict):
                        media_type = 'videos'
                        if result['status'] == 'success':
                            download_results['success'][media_type].append(result['path'])
                        elif result['status'] == 'exists':
                            download_results['exists'][media_type].append(result['path'])
                        elif result['status'] == 'failed':
                            download_results['failed'][media_type].append(result)
                    else:
                        # Legacy support - if result is a path string
                        if result:
                            download_results['success']['videos'].append(result)
        
        # Calculate totals
        total_images = len(download_results['success']['images']) + len(download_results['exists']['images'])
        total_videos = len(download_results['success']['videos']) + len(download_results['exists']['videos'])
        
        # Show summary
        print(f"📊 Media collection complete for {username}:")
        
        # Successful downloads
        success_images = len(download_results['success']['images'])
        success_videos = len(download_results['success']['videos'])
        if success_images > 0 or success_videos > 0:
            print(f"   ✅ Downloads Completed: {success_images} images, {success_videos} videos")
        
        # Files that already existed
        exists_images = len(download_results['exists']['images'])
        exists_videos = len(download_results['exists']['videos'])
        if exists_images > 0 or exists_videos > 0:
            print(f"   📁 Files Already Exist: {exists_images} images, {exists_videos} videos")
        
        # Failed downloads
        failed_images = len(download_results['failed']['images'])
        failed_videos = len(download_results['failed']['videos'])
        if failed_images > 0 or failed_videos > 0:
            print(f"   ❌ Download Failures: {failed_images} images, {failed_videos} videos")
            if self.debug:
                for failed in download_results['failed']['images'] + download_results['failed']['videos']:
                    print(f"      └── {failed['filename']}: {failed['error']}")
        
        summary = {
            'images_downloaded': total_images,
            'videos_downloaded': total_videos,
            'images_folder': images_folder,
            'videos_folder': videos_folder,
            'image_files': download_results['success']['images'] + download_results['exists']['images'],
            'video_files': download_results['success']['videos'] + download_results['exists']['videos'],
            'download_stats': download_results
        }
        
        return summary

    def scroll_and_collect_content(self, content_type='posts'):
        """Scroll and collect content with progress tracking
        
        Args:
            content_type (str): Type of content to collect ('posts', 'replies', 'reposts', 'followers', 'following')
            
        Returns:
            dict: Collected content including:
                - Post data
                - Reply data
                - Repost data
                - Follower data
                - Following data
        """
        print(f"📝 Collecting {content_type}...")
        previous_content_count = 0
        same_count_iterations = 0
        max_same_count = 3
        collected_content = {}
        content_index = 1
        
        # Progress tracking
        last_progress_count = 0
        progress_threshold = 5  # Only show progress every 5 new items

        # Need to optimize somehow
        while True:
            if content_type == 'followers' or content_type == 'following':
                try:
                    # Find the main dialog container
                    dialog = self.driver.find_element("css selector", "div[role='dialog']")
                    if dialog:
                        # Find the scrollable container using the class from your HTML
                        scrollable_div = dialog.find_element("xpath", ".//div[starts-with(@class, 'xb57i2i')]")
                        
                        # Scroll down the container
                        self.driver.execute_script("""
                            arguments[0].scrollTo({
                                top: arguments[0].scrollHeight
                            });
                        """, scrollable_div)
                except Exception as e:
                    print(f"Scrolling error: {e}")
                    break
            else:
                # Original scrolling for other content types
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

                
            time.sleep(2)

            soup = BeautifulSoup(self.driver.page_source, 'html.parser')
            #Need to change from class names
            
            if content_type == 'posts':
                elements = soup.find_all('div', class_='x78zum5 xdt5ytf')
                for element in elements[len(collected_content):]:
                    post_data = self.extract_post_data(element)
                    if post_data:
                        collected_content[f"post {content_index}"] = post_data
                        content_index += 1

            elif content_type == 'replies':
                elements = soup.find_all('div', class_='x78zum5 xdt5ytf')
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
                        
            #May not find all followers
            elif content_type == 'followers':
                elements = soup.find_all('div', class_='x78zum5 xdt5ytf x5kalc8 xl56j7k xeuugli x1sxyh0')
                for element in elements[len(collected_content):]:
                    follower_data = self.extract_follower_data(element)
                    if follower_data:
                        collected_content[f"follower {content_index}"] = follower_data
                        content_index += 1

            elif content_type == 'following':
                elements = soup.find_all('div', class_='x78zum5 xdt5ytf x5kalc8 xl56j7k xeuugli x1sxyh0')
                for element in elements[len(collected_content):]:
                    following_data = self.extract_follower_data(element)
                    if following_data:
                        collected_content[f"following {content_index}"] = following_data
                        content_index += 1

            current_content_count = len(elements)
            
            # Show progress only when significant progress is made or in debug mode
            collected_count = len(collected_content)
            if self.debug or collected_count - last_progress_count >= progress_threshold:
                if collected_count > 0:
                    print(f"   📊 Progress: {collected_count} {content_type} collected")
                    last_progress_count = collected_count

            if current_content_count == previous_content_count:
                same_count_iterations += 1
                if same_count_iterations >= max_same_count:
                    break
            else:
                same_count_iterations = 0

            previous_content_count = current_content_count
            time.sleep(1)

        # Final summary
        final_count = len(collected_content)
        if final_count > 0:
            print(f"   ✅ Completed: {final_count} {content_type} collected")
        else:
            print(f"   ℹ️  No {content_type} found")
            if self.debug:
                print(f"      └── This might be due to privacy settings or empty content")

        return collected_content

    def fetch_profile(self, username):
        """
        Fetch profile data for a given username
        
        Args:
            username (str): Username to fetch
            
        Returns:
            dict: Profile data including:
                - Basic info (bio, name, etc.)
                - Post data
                - Follower/following counts
                - Engagement metrics
        """ 
        url = f"{self.base_url}/@{username}"
        profile_data = {
            "username": username,
            "name": "",
            "profile_picture": "",
            "bio": "",
            "external_links": "",
            "instagram": "",
            "followers_count": "",
            "followers":{},
            "following_count": "",
            "following":{},
            "posts_count": 0,
            "posts": {},
            "replies_count": 0,
            "replies": {},
            "reposts_count": 0,
            "reposts": {},
            "is_private": False
        }
        try:
            # Add retry logic
            max_retries = 3
            retry_count = 0
            
            while retry_count < max_retries:
                try:
                    self.driver.get(url)
                    # Wait for the page to load
                    self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
                    break
                except TimeoutException:
                    retry_count += 1
                    if retry_count == max_retries:
                        self.handle_http_error(url, TimeoutException("Page load timeout"))
                    print(f"Attempt {retry_count} failed, retrying...")
                    time.sleep(2 * retry_count)  # Exponential backoff
                    
            # Check for 404 or other error pages
            if "Page not found" in self.driver.title or "Error" in self.driver.title:
                raise ThreadsScraperException(f"Profile not found or unavailable: {username}")
            soup = BeautifulSoup(self.driver.page_source, 'html.parser')    
             # Check if profile is private
            try:
                private_message = self.driver.find_element(By.XPATH, "//span[contains(text(), 'This profile is private.')]")
                if private_message:
                    print(f"Profile {username} is private. Skipping detailed data collection.")
                    profile_data["is_private"] = True
                    
                    # Still collect basic profile info that's visible
                    soup = BeautifulSoup(self.driver.page_source, 'html.parser')    
                    
                    # Get name if available
                    name = soup.find('h1', {"dir": "auto"})
                    if name:
                        profile_data['name'] = name.get_text(strip=True)
                    
                    # Get profile picture if available
                    profile_picture = soup.find('meta',{'property':'og:image'})
                    if profile_picture:
                        image_url = profile_picture.get('content')
                        if image_url:
                            profile_data['profile_picture'] = image_url
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
                        error_msg = f"Instagram link not found: {str(e)}"
                        print(error_msg)
                        if self.debug:
                            import traceback
                            print(f"   └── Debug: {traceback.format_exc()}")
                        profile_data['instagram'] = "Instagram link not found"
                    
                
                    followers_count_elem = self.driver.find_element(By.XPATH, '//span[@dir="auto"][contains(text(), " followers")]')
                    profile_data['followers_count'] = followers_count_elem.text.strip().replace('followers', '').strip()
                    
                    return {username: profile_data}


            except NoSuchElementException:
                # Profile is not private, continue with normal scraping
                pass
                
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
            
            #Collect followers
            if self.is_logged_in:
                try:
                    # First try to get the count from the profile page
                    followers_count_elem = self.driver.find_element(By.XPATH, '//span[@dir="auto"][contains(text(), " followers")]')
                    displayed_followers_count = followers_count_elem.text.strip().replace('followers', '').strip()
                    
                    # Click to open followers window
                    followers_count_elem.click()
                    time.sleep(2)
                    
                    # Collect followers data
                    followers = self.scroll_and_collect_content('followers')
                    actual_followers_count = len(followers)
                    
                    # Use the actual count from collected data
                    profile_data['followers_count'] = str(actual_followers_count)
                    profile_data['followers'] = followers
                    
                    # Log if there's a discrepancy
                    if actual_followers_count != int(displayed_followers_count.replace(',', '')):
                        print(f"Warning: Followers count mismatch - Display: {displayed_followers_count}, Actual: {actual_followers_count}")

                    #Collect following
                    try:
                        # First try to get the count from the profile page
                        following_container = self.driver.find_element(By.XPATH,'//span[@dir="auto"][contains(text(), "Following")]')
                        following_count_elem = self.driver.find_element(By.XPATH, '//div[@aria-label="Following"]//span[@title]')
                        displayed_following_count = following_count_elem.get_attribute('title')
                        
                        # Click to open following window
                        following_container.click()
                        time.sleep(2)
                        
                        # Collect following data
                        following = self.scroll_and_collect_content('following')
                        actual_following_count = len(following)
                        
                        # Use the actual count from collected data
                        profile_data['following_count'] = str(actual_following_count)
                        profile_data['following'] = following
                        
                        # Log if there's a discrepancy
                        if actual_following_count != int(displayed_following_count.replace(',', '')):
                            print(f"Warning: Following count mismatch - Display: {displayed_following_count}, Actual: {actual_following_count}")
                        
                    except Exception as e:
                        print(f"Error collecting following data: {str(e)}")
                        profile_data['following_count'] = "Following count not found"
                        profile_data['following'] = {}

                    # Try multiple methods to close the window
                    try:
                        # Method 1: ActionChains
                        actions = ActionChains(self.driver)
                        actions.send_keys(Keys.ESCAPE).perform()
                        time.sleep(1) 
                        
                        # If that didn't work, try Method 2: Direct to body
                        if len(self.driver.find_elements(By.XPATH, "//div[contains(@role, 'dialog')]")) > 0:
                            self.driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.ESCAPE)
                            time.sleep(1)
                            
                        # If still open, try Method 3: Click close button if it exists
                        if len(self.driver.find_elements(By.XPATH, "//div[contains(@role, 'dialog')]")) > 0:
                            close_button = self.driver.find_element(By.XPATH, "//button[@aria-label='Close' or contains(@class, 'close')]")
                            close_button.click()
                            
                    except Exception as e:
                        print(f"Error closing window: {e}")

                except Exception as e:
                    print(f"Error collecting followers data: {str(e)}")
                    profile_data['followers_count'] = "Followers not found"
                    profile_data['followers'] = {}
            else:
                print("Skipping followers/following collection - not logged in")
                profile_data['followers_count'] = "Login required"
                profile_data['following_count'] = "Login required"
                profile_data['followers'] = {}
                profile_data['following'] = {}
            
                
            
            # Collect posts
            print("Collecting posts...")
            posts = self.scroll_and_collect_content('posts')
            profile_data["posts"] = posts
            profile_data["posts_count"] = len(posts)

            
            # Collect replies
            print("Collecting replies...")
            self.driver.get(f"{url}/replies")
            time.sleep(2)
            replies = self.scroll_and_collect_content('replies')
            profile_data["replies"] = replies
            profile_data["replies_count"] = len(replies)
            
            # Collect reposts
            print("Collecting reposts...")
            self.driver.get(f"{url}/reposts")
            time.sleep(2)
            reposts = self.scroll_and_collect_content('reposts')
            profile_data["reposts"] = reposts
            profile_data["reposts_count"] = len(reposts)
            
            # Collect and download media from all posts
            all_posts = {}
            all_posts.update(posts)
            all_posts.update(replies)
            all_posts.update(reposts)
            
            if all_posts:
                media_summary = self.collect_and_download_media(username, all_posts)
                profile_data["media_summary"] = media_summary
            
        except ThreadsScraperException as e:
            error_msg = f"Scraping error: {str(e)}"
            print(error_msg)
            if self.debug:
                import traceback
                print(f"   └── Debug: {traceback.format_exc()}")
            return {username: {"error": str(e)}}
        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            print(error_msg)
            if self.debug:
                import traceback
                print(f"   └── Debug: {traceback.format_exc()}")
            return {username: {"error": f"An unexpected error occurred: {str(e)}"}}
        
        return {username: profile_data}
    