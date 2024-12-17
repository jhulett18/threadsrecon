# threadsrecon
OSINT Tool for threads.net

## Introduction
This tool is designed to scrape, analyze, visualize data, and generate reports from threads.net. It is built using Python and leverages several open source Python libraries.

## Features
- **Profile Analysis**: Detailed user profile information and statistics
- **Content Scraping**: Automated collection of posts, replies, and media
- **Engagement Analytics**: Track likes, replies, and interaction patterns
- **Sentiment Analysis**: Analyze emotional tone and content sentiment
- **Network Visualization**: Map connections and hashtag relationships
- **Alert System**: Real-time monitoring with Telegram notifications
- **Custom Reporting**: Generate comprehensive PDF reports
- **Data Export**: Export findings in JSON format


## Requirements
- Python 3.8+
- 2GB RAM minimum
- Unix-based OS or Windows 10+
- Google Chrome/Chromium with appropriate chromedriver version 90+
- Telegram bot.
- wkhtmltopdf installed.

## Installation
### Generic
Install [chromedriver](https://sites.google.com/chromium.org/driver/downloads) for your chrome version and OS.
### macOS (via [homebrew](https://brew.sh/))
```bash
brew install chromedriver
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```
Install the required libraries for python:
```bash
python3 -m pip install -r requirements.txt
```
Crate your [Telegram bot](https://core.telegram.org/bots/tutorial) and obtain your bot token and chat ID.
Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) for your OS.

### Docker Installation
Install Docker.
Build the container.
```bash
docker build -t threadsrecon .
```
Run the container.
```bash
docker run -v $(pwd)/data:/app/data threadsrecon
```
## Configuration
### Settings File Structure
The `settings.yaml` file contains all configuration parameters. Key sections include:
- **Credentials**: Authentication details
- **ScraperSettings**: Scraping parameters and browser configuration
- **AnalysisSettings**: Data processing and output preferences
- **WarningSystem**: Alert configuration
- **ReportGeneration**: Report generation settings
Create `settings.yaml` file in the root directory.
Example configuration:
```bash
Credentials:  # if not set, anonymous access will be used
  instagram_username: your_username
  instagram_password: your_password

ScraperSettings:
  base_url: https://www.threads.net
  chromedriver: ./chromedriver  # path to chromedriver
  usernames:
    - target_username
    - target_username2
  timeouts:
    page_load: 20
    element_wait: 10
  retries:
    max_attempts: 3
    initial_delay: 1
  delays:
    min_wait: 1
    max_wait: 3
  user_agents:
    - 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    - 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Safari/537.36'
    - 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.0.0 Safari/537.36'
  browser_options:
    headless: false
    window_size:
      width: 1920
      height: 1080
    disabled_features:
      - gpu
      - sandbox
      - dev-shm-usage
      - extensions
      - infobars
      - logging
      - popup-blocking
      
AnalysisSettings:
 input_file: data/profiles.json
 archive_file: data/archived_profiles.json
 output_file: data/analyzed_profiles.json
 hashtag_network_static: data/visualizations/hashtag_network_static.png
 hashtag_network_interactive: data/visualizations/hashtag_network_interactive.html 
 sentiment_plot: data/visualizations/sentiment_plot.png
 engagement_plot: data/visualizations/engagement_metrics.png
 mutual_followers_plot: data/visualizations/mutual_followers.png
 hashtag_dist_plot: data/visualizations/hashtag_distribution.png
 keywords: 
  - keyword1
  - keyword2
 date_range: 
  start: null  # or "2024-01-01"
  end: null    # or "2024-12-31"

WarningSystem:
  token: your_telegram_bot_token
  chat_id: your_chat_id
  priority_keywords:
    HIGH:
      - "urgent"
      - "emergency"
      - "critical"
    MEDIUM:
      - "important"
      - "attention"
      - "warning"
    LOW:
      - "update"
      - "info"
      - "notice"

ReportGeneration:
 path_to_wkhtmltopdf: your\path\to\wkhtmltopdf.exe # Example location: C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
 output_path: data/reports/report.pdf
```

## Running
Run complete pipeline.
```bash
python main.py all 
```
Only scrape data.
```bash
python main.py scrape  
```
Only analyze existing data.
```bash
python main.py analyze 
```
Generate visualizations.
```bash
python main.py visualize 
```
Create PDF report.
```bash
python main.py report  
```

## Output Structure
```
data/
├── profiles.json           # Raw scraped data
├── analyzed_profiles.json  # Processed data
├── archived_profiles.json  # Archived data
├── visualizations/
│   ├── hashtag_network.png
│   ├── sentiment_plot.png
│   └── engagement_metrics.png
└── reports/
    └── report_YYYY-MM-DD.pdf
```
## Security Considerations
- This tool respects threads.net's robots.txt
- Data collected should be used in accordance with local privacy laws
- Consider using a VPN and running in a virtual environment when collecting sensitive data.
- Credential information is stored securely in settings.yaml

## Troubleshooting
Common issues and solutions:

  1. ChromeDriver version mismatch
    ```bash
    Error: "ChromeDriver only supports Chrome version XX"
    Solution: Download matching ChromeDriver version from https://sites.google.com/chromium.org/driver/downloads
    ```

  2. Authentication Issues
    ```bash
    Error: "Account requires additional verification"
    Solution: Log into Instagram manually first and complete verification
    
    Error: "Suspicious login attempt detected"
    Solution: Verify your account manually and try again
    
    Error: "Account has been temporarily blocked"
    Solution: Wait for the block to expire or use anonymous access
    ```

  3. Network and Connection Issues
    ```bash
    Error: "Connection timed out while accessing threads.net"
    Solution: Check your internet connection and try again
    
    Error: "Could not resolve the host name"
    Solution: Verify the URL and DNS settings
    
    Error: "Connection refused by threads.net"
    Solution: The server might be down or blocking requests. Try using a VPN
    
    Error: "Proxy connection failed"
    Solution: Check your proxy settings or disable proxy
    ```

  4. Scraping Issues
    ```bash
    Error: "Required element not found"
    Solution: The page structure might have changed. Update selectors
    
    Error: "Element is no longer attached to the DOM"
    Solution: Page was updated during scraping. Increase wait times
    
    Error: "Could not interact with element"
    Solution: Element might be covered. Try running in non-headless mode
    ```

  5. Data Processing Issues
    ```bash
    Error: "Module not found"
    Solution: Run `pip install -r requirements.txt`
    
    Error: "Failed to process sentiment analysis"
    Solution: Run `python -c "import nltk; nltk.download('vader_lexicon')"`
    ```

  6. Report Generation Issues
    ```bash
    Error: "wkhtmltopdf not found"
    Solution: Install wkhtmltopdf and update path in settings.yaml
    
    Error: "Failed to generate PDF"
    Solution: Check write permissions in output directory
    ```

  7. Warning System Issues
    ```bash
    Error: "Failed to send Telegram alert"
    Solution: Verify bot token and chat ID in settings.yaml
    
    Error: "Message too long"
    Solution: Alerts are automatically truncated to 200 characters
    ```

  8. Configuration Issues
    ```bash
    Error: "Invalid settings"
    Solution: Validate settings.yaml against example configuration
    
    Error: "Missing required field"
    Solution: Check all required fields are present in settings.yaml
    ```

  For persistent issues:
  1. Check the logs in the `data` directory
  2. Try running in non-headless mode for debugging
  3. Clear browser cache and cookies
  4. Verify all dependencies are installed correctly
  5. Ensure you have the latest version of Chrome installed

  If issues persist, please open an issue on GitHub with:
  - Full error message
  - Configuration file (with sensitive data removed)
  - Steps to reproduce
  - Chrome and ChromeDriver versions

