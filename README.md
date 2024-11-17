# threadsrecon
OSINT Tool for threads.net

## Requirements
- Google Chrome/Chromium with appropriate chromedriver version

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
```

## Running
```bash
python3 main.py
```