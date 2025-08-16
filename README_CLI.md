# threadsrecon CLI - Enhanced Command Line Interface

**OSINT Tool for threads.net with Professional CLI Experience**

Gone are the days of editing YAML files for simple operations. The enhanced threadsrecon CLI provides a modern, user-friendly command line interface for all your threads.net OSINT investigations.

## 🚀 Quick Start

```bash
# Clone and setup
git clone https://github.com/offseq/threadsrecon.git
cd threadsrecon

# Install dependencies (one-time setup)
./install.sh

# Start investigating immediately
./threadsrecon scrape -u target_username
```

## 📋 Installation

### Prerequisites
- **Python 3.8+**
- **Google Chrome/Chromium** browser
- **ChromeDriver** matching your Chrome version
- **wkhtmltopdf** for PDF report generation

### Quick Installation
```bash
# Run the installation script
./install.sh

# Or install dependencies manually
pip install beautifulsoup4 requests PyYAML selenium pandas numpy matplotlib plotly networkx nltk textblob
```

## 🎯 Basic Usage

### Simple Profile Investigation
```bash
# Scrape a single user
./threadsrecon scrape -u username

# Scrape multiple users
./threadsrecon scrape -u user1 user2 user3

# Complete investigation (scrape + analyze + visualize + report)
./threadsrecon all -u target_username
```

### Custom Output Directory
```bash
# Organize investigations by case
./threadsrecon all -u suspect --output-dir /cases/investigation_2024_001
./threadsrecon scrape -u target --output-dir /tmp/quick_check
```

### Browser Control
```bash
# Run invisibly (headless mode)
./threadsrecon scrape -u username --headless

# Show browser window (debugging)
./threadsrecon scrape -u username --no-headless
```

## 📖 Complete Command Reference

### Commands
```bash
./threadsrecon COMMAND [OPTIONS]

Commands:
  scrape      Collect data from threads.net
  analyze     Process and analyze collected data
  visualize   Generate charts and network graphs
  report      Create comprehensive PDF report
  all         Run complete pipeline (scrape→analyze→visualize→report)
```

### Essential Options
```bash
# Target Selection
-u, --usernames USER1 USER2    Target usernames (space-separated)

# Output Control
--output-dir DIR               Custom output directory for all files
--config FILE                  Use custom settings YAML file

# Browser Options
--headless                     Run browser invisibly (faster)
--no-headless                  Show browser window (debugging)
--chromedriver PATH            Custom chromedriver location

# Performance Tuning
--timeout SECONDS              Page load timeout (default: 20)
--element-timeout SECONDS      Element wait timeout (default: 10)
--max-retries COUNT            Max retry attempts (default: 3)
--min-delay SECONDS            Min delay between requests
--max-delay SECONDS            Max delay between requests

# Analysis Options
--keywords WORD1 WORD2         Keywords for content analysis

# Authentication (Optional)
--instagram-username USER      Instagram username for auth
--instagram-password PASS      Instagram password for auth

# Report Options
--wkhtmltopdf PATH             Custom wkhtmltopdf location

# Telegram Notifications
--telegram-token TOKEN         Telegram bot token
--telegram-chat-id ID          Telegram chat ID

# Output Control
--quiet, -q                    Suppress non-error output
--verbose, -v                  Enable detailed output
```

## 🔍 Investigation Workflows

### Quick Profile Check
```bash
# Fast profile overview
./threadsrecon scrape -u target_user --headless --quiet
```

### Deep Investigation
```bash
# Complete analysis with custom keywords
./threadsrecon all -u suspect \
  --keywords "crypto scam phishing fraud" \
  --output-dir /investigations/case_001 \
  --verbose
```

### Multi-Target Investigation
```bash
# Investigate connected accounts
./threadsrecon all -u main_suspect accomplice1 accomplice2 \
  --output-dir /cases/organized_crime \
  --headless
```

### Stealth Mode Investigation
```bash
# Anonymous investigation with delays
./threadsrecon scrape -u target \
  --headless \
  --min-delay 2 \
  --max-delay 5 \
  --timeout 30
```

## 📁 Output Structure

### Default Organization
```
data/
├── profiles.json              # Raw scraped data
├── analyzed_profiles.json     # Enhanced with analysis
├── visualizations/            # Charts and graphs
│   ├── network_graph.png     # Follower/following networks
│   ├── sentiment_chart.png   # Sentiment analysis results
│   ├── activity_timeline.png # Activity patterns
│   └── hashtag_frequency.png # Popular hashtags
└── reports/
    └── report_TIMESTAMP.pdf  # Complete investigation report
```

### Custom Directory Structure
```bash
./threadsrecon all -u target --output-dir /investigations/case_001

# Results in:
/investigations/case_001/
├── profiles.json
├── analyzed_profiles.json
├── visualizations/
└── reports/report_TIMESTAMP.pdf
```

## 📊 Data Collection Capabilities

### Profile Information
- ✅ **Display name and username**
- ✅ **Profile picture URL**
- ✅ **Bio/description text**
- ✅ **External links in bio**
- ✅ **Follower count and follower usernames**
- ✅ **Following count and following usernames**
- ✅ **Instagram account link** (if connected)

### Content Analysis
- ✅ **All posts with timestamps**
- ✅ **Replies and conversations**
- ✅ **Shared/reposted content**
- ✅ **Media URLs** (images and videos)
- ✅ **Hashtags and mentions**
- ✅ **Engagement metrics** (likes, replies)

### Advanced Analytics
- ✅ **Sentiment analysis** of posts
- ✅ **Keyword frequency analysis**
- ✅ **Activity pattern detection**
- ✅ **Network relationship mapping**
- ✅ **Timeline visualization**

### Report Generation
- ✅ **Comprehensive PDF reports**
- ✅ **Embedded visualizations**
- ✅ **Executive summary**
- ✅ **Detailed findings**
- ✅ **Timestamped for evidence**

## ⚡ Performance Tips

### Faster Scraping
```bash
# Use headless mode
./threadsrecon scrape -u target --headless

# Reduce timeouts for known-working setups
./threadsrecon scrape -u target --timeout 15 --element-timeout 5
```

### Large Investigations
```bash
# Process one user at a time for better control
./threadsrecon scrape -u user1 --output-dir /case1/user1
./threadsrecon scrape -u user2 --output-dir /case1/user2

# Or use quiet mode for batch processing
./threadsrecon scrape -u user1 user2 user3 --quiet
```

### Resource Management
```bash
# Limit resource usage with delays
./threadsrecon scrape -u target --min-delay 3 --max-delay 6 --max-retries 2
```

## 🛠️ Troubleshooting

### Installation Issues
```bash
# If ./threadsrecon doesn't work, use Python directly
python3 main.py scrape -u username

# Check permissions
chmod +x threadsrecon
chmod +x install.sh

# Install dependencies manually
pip install -r requirements.txt
```

### ChromeDriver Issues
```bash
# Specify custom chromedriver location
./threadsrecon scrape -u target --chromedriver /usr/local/bin/chromedriver

# Check Chrome version compatibility
google-chrome --version
chromedriver --version
```

### Timeout Issues
```bash
# Increase timeouts for slow connections
./threadsrecon scrape -u target --timeout 60 --element-timeout 20

# Add delays for rate limiting
./threadsrecon scrape -u target --min-delay 2 --max-delay 4
```

### Debug Mode
```bash
# Show browser window to see what's happening
./threadsrecon scrape -u target --no-headless --verbose

# Use verbose output for detailed logging
./threadsrecon all -u target --verbose
```

## 🔐 Security & Privacy

### Anonymous Investigation
```bash
# No authentication required (limited access)
./threadsrecon scrape -u public_user --headless

# Use VPN and avoid personal accounts
./threadsrecon scrape -u target --headless --min-delay 3
```

### Data Protection
- All data stays on your local machine
- No external data transmission (except to threads.net)
- Configurable output directories for secure storage
- PDF reports include timestamps for evidence chain

### Rate Limiting
- Built-in delays to respect threads.net servers
- Configurable retry attempts
- User-agent rotation
- Respectful scraping practices

## 🎯 Use Cases

### Security Research
```bash
# Investigate suspicious accounts
./threadsrecon all -u suspicious_account \
  --keywords "phishing scam fraud" \
  --output-dir /security/investigation_001
```

### Digital Forensics
```bash
# Evidence collection with detailed reporting
./threadsrecon all -u subject \
  --verbose \
  --output-dir /evidence/case_2024_001 \
  --keywords "evidence keywords"
```

### Threat Intelligence
```bash
# Monitor threat actors
./threadsrecon scrape -u threat_actor \
  --headless \
  --output-dir /threat_intel/actor_profiles \
  --telegram-token YOUR_TOKEN --telegram-chat-id YOUR_ID
```

### Academic Research
```bash
# Social media analysis research
./threadsrecon all -u research_subject \
  --keywords "research topics" \
  --output-dir /research/study_001
```

## 📚 Advanced Configuration

### Custom Settings File
```bash
# Use different configuration
./threadsrecon scrape -u target --config custom_settings.yaml
```

### Environment Variables
```bash
# Set default behavior
export THREADSRECON_HEADLESS=true
export THREADSRECON_OUTPUT_DIR=/default/investigations
```

### Automation Integration
```bash
# Script-friendly quiet mode
./threadsrecon scrape -u target --quiet --output-dir /automated/run_001

# JSON output parsing
python3 -c "import json; data=json.load(open('data/profiles.json')); print(data.keys())"
```

## 📞 Support

### Getting Help
```bash
# General help
./threadsrecon --help

# Command-specific help
./threadsrecon scrape --help
./threadsrecon analyze --help
```

### Common Issues
- **Import errors**: Install missing dependencies with `pip install -r requirements.txt`
- **Permission errors**: Run `chmod +x threadsrecon install.sh`
- **ChromeDriver errors**: Download matching version from [chrome-for-testing](https://googlechromelabs.github.io/chrome-for-testing/)
- **Memory issues**: Use `--headless` mode and process fewer users at once

### Configuration Examples
See `settings.yaml.example` for complete configuration options and examples.

---

**⚠️ Legal Notice:** Use responsibly and in compliance with local laws and threads.net terms of service. This tool is for legitimate security research, digital forensics, and academic purposes only.

**🛡️ Security Focus:** threadsrecon is designed for defensive security research. Always follow responsible disclosure practices and respect privacy.