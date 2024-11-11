# threadsrecon
OSINT Tool for threads.net

## Requirements

- Latest Google Chrome/Chromium version, you can find it with this:
```bash
chrome://settings/help
```

## Installation
- Install [chromedriver](https://sites.google.com/chromium.org/driver/downloads) for your chrome version and OS.
- Install the required libraries for python:
```bash
pip3 install -r requirements.txt
```
- Create settings.yaml file.
- Add the text below to the .yaml file:
```bash
Credentials:
  instagram_username: exampleusername
  instagram_password: examplepassword

ScraperSettings:
  base_url: https://www.threads.net
  usernames:
    - exampleusername
    - exampleusername2
```
- Change Instagram credentials to log in to your desired account.
- Change/add/remove target usernames to scrape.

## Running
- Simply run main.py in your IDE of choice
- In Linux:
```bash
python3 main.py
```