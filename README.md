# threadsrecon
OSINT Tool for threads.net

## Requirements
- Google Chrome/Chromium with appropriate chromedriver version
- Telegram bot
- wkhtmltopdf installed

## Installation
### Generic
- Install [chromedriver](https://sites.google.com/chromium.org/driver/downloads) for your chrome version and OS.
### macOS (via [homebrew](https://brew.sh/))
```bash
brew install chromedriver
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```
- Install the required libraries for python:
```bash
python3 -m pip install -r requirements.txt
```
- Crate your [Telegram bot](https://core.telegram.org/bots/tutorial) and obtain your bot token and chat ID.
- Install [wkhtmltopdf](https://wkhtmltopdf.org/downloads.html) for your OS.
- Create `settings.yaml` file.
- Example configuration:
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
 hashtag_network_static: data/hashtag_network_static.png
 hashtag_network_interactive: data/hashtag_network_interactive.html 
 sentiment_plot: data/sentiment_plot.png
 engagement_plot: data/engagement_metrics.png
 mutual_followers_plot: data/mutual_followers.png
 hashtag_dist_plot: data/hashtag_distribution.png
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
```

## Running
```bash
python main.py all 
```
```bash
python main.py scrape 
```
```bash
python main.py analyze 
```
```bash
python main.py visualize 
```
```bash
python main.py report
```