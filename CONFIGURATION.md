# threadsrecon Configuration Guide

Complete guide to configuring threadsrecon for optimal performance and security.

## Overview

The `settings.yaml` file contains all configuration parameters for threadsrecon. This guide explains each section in detail and provides platform-specific setup instructions.

---

## Configuration Sections

### 1. Credentials (Optional)

Controls authentication with Instagram/Threads. Anonymous access has limitations but works for basic scraping.

```yaml
Credentials:
  instagram_username: "your_username"  # Your Instagram username
  instagram_password: "your_password"  # Your Instagram password
```

**Options:**
- **With credentials**: Full access, higher rate limits, better success rates
- **Anonymous (empty)**: Limited access, may hit rate limits faster, some profiles inaccessible

**Security Notes:**
- Store credentials securely
- Use dedicated research account, not personal
- Consider app-specific passwords if 2FA enabled
- Never commit credentials to version control

---

### 2. ScraperSettings (Required)

Core scraping configuration and browser automation settings.

#### Base Configuration
```yaml
ScraperSettings:
  base_url: https://www.threads.net
  chromedriver: /usr/local/bin/chromedriver
  usernames:
    - target_username1
    - target_username2
```

**Platform-Specific ChromeDriver Paths:**
- **Ubuntu/Debian**: `/usr/bin/chromedriver` or `/usr/local/bin/chromedriver`
- **macOS (Homebrew)**: `/opt/homebrew/bin/chromedriver`
- **macOS (Manual)**: `/usr/local/bin/chromedriver`
- **Windows**: `C:\Program Files\chromedriver\chromedriver.exe`
- **Docker**: `/usr/local/bin/chromedriver`

#### Timing Configuration
```yaml
  timeouts:
    page_load: 20      # Maximum seconds to wait for page load
    element_wait: 10   # Maximum seconds to wait for elements
  retries:
    max_attempts: 3    # Number of retry attempts on failure
    initial_delay: 1   # Seconds to wait before first retry
  delays:
    min_wait: 1        # Minimum delay between requests (seconds)
    max_wait: 3        # Maximum delay between requests (seconds)
```

**Tuning Guidelines:**
- **Slow connections**: Increase `page_load` to 30-40 seconds
- **Rate limiting issues**: Increase `min_wait` and `max_wait`
- **Unstable targets**: Increase `max_attempts` to 5
- **Fast networks**: Decrease delays to 0.5-1 second

#### User Agent Rotation
```yaml
  user_agents:
    - 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    - 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    - 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36'
```

**Best Practices:**
- Use current browser versions (Chrome 120+)
- Match your actual OS in user agents
- Rotate between 3-5 different agents
- Update quarterly to stay current

#### Browser Options
```yaml
  browser_options:
    headless: true           # Hide browser window
    window_size:
      width: 1920           # Browser window width
      height: 1080          # Browser window height
    disabled_features:      # Chrome features to disable
      - gpu                 # GPU acceleration
      - sandbox             # Security sandbox
      - dev-shm-usage       # Shared memory usage
      - extensions          # Browser extensions
      - infobars            # Information bars
      - logging             # Console logging
      - popup-blocking      # Popup blocker
```

**Configuration for Different Scenarios:**
- **Debugging**: Set `headless: false` to watch browser
- **Docker**: Keep all disabled features for stability
- **Low memory**: Add `disable-background-timer-throttling`
- **High performance**: Remove `gpu` from disabled features

---

### 3. AnalysisSettings (Required)

Data processing and analysis configuration.

```yaml
AnalysisSettings:
  input_file: data/profiles.json           # Input from scraper
  archive_file: data/archived_profiles.json   # Backup storage
  output_file: data/analyzed_profiles.json    # Analysis results
  visualization_dir: data/visualizations      # Chart output directory
  keywords:                                # Keywords to highlight
    - keyword1
    - keyword2
    - brand_name
  date_range:                             # Filter by date
    start: "2024-01-01"                   # Start date (YYYY-MM-DD)
    end: "2024-12-31"                     # End date (YYYY-MM-DD)
```

**Keyword Strategy:**
- **Brand monitoring**: Company names, product names
- **Threat detection**: Security-related terms
- **Trend analysis**: Industry buzzwords, hashtags
- **Sentiment tracking**: Emotional indicators

**Date Range Usage:**
- **Recent activity**: Last 30-90 days
- **Historical analysis**: Longer ranges for trends
- **Event analysis**: Specific time windows around events
- **Null values**: Analyze all available data

---

### 4. WarningSystem (Optional)

Real-time Telegram notifications for important findings.

```yaml
WarningSystem:
  token: "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"  # Bot token
  chat_id: "987654321"                            # Your chat ID
  priority_keywords:
    HIGH:                    # Immediate alerts
      - "urgent"
      - "emergency" 
      - "critical"
      - "security breach"
    MEDIUM:                  # Important notifications
      - "important"
      - "attention"
      - "warning"
      - "incident"
    LOW:                     # General updates
      - "update"
      - "info"
      - "notice"
      - "announcement"
```

**Telegram Bot Setup:**
1. Message @BotFather on Telegram
2. Create new bot: `/newbot`
3. Get bot token from BotFather
4. Start chat with your bot
5. Get chat ID: `https://api.telegram.org/bot<TOKEN>/getUpdates`

**Alert Strategy:**
- **HIGH**: Security incidents, urgent brand mentions
- **MEDIUM**: Important updates, competitive intelligence
- **LOW**: General monitoring, trend updates

---

### 5. ReportGeneration (Required)

PDF report generation settings.

```yaml
ReportGeneration:
  path_to_wkhtmltopdf: /usr/bin/wkhtmltopdf     # Path to wkhtmltopdf binary
  output_path: data/reports/report.pdf          # Output file location
```

**Platform-Specific wkhtmltopdf Paths:**
- **Ubuntu/Debian**: `/usr/bin/wkhtmltopdf`
- **macOS (Homebrew)**: `/opt/homebrew/bin/wkhtmltopdf`
- **Windows**: `C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe`
- **Docker**: `/usr/bin/wkhtmltopdf`

---

## Environment-Specific Configurations

### Development Environment
```yaml
ScraperSettings:
  browser_options:
    headless: false        # Watch browser for debugging
  delays:
    min_wait: 0.5         # Faster for testing
    max_wait: 1
  timeouts:
    page_load: 10         # Shorter timeouts
```

### Production Environment
```yaml
ScraperSettings:
  browser_options:
    headless: true        # Always headless in production
  delays:
    min_wait: 2           # Conservative delays
    max_wait: 5
  retries:
    max_attempts: 5       # More retries for reliability
```

### Docker Environment
```yaml
ScraperSettings:
  chromedriver: /usr/local/bin/chromedriver
  browser_options:
    headless: true
    disabled_features:
      - gpu
      - sandbox
      - dev-shm-usage     # Critical for Docker stability

ReportGeneration:
  path_to_wkhtmltopdf: /usr/bin/wkhtmltopdf
```

---

## Validation and Troubleshooting

### Configuration Validation
```bash
# Check environment
./scripts/validate_env.sh

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('settings.yaml'))"

# Test configuration in GUI
streamlit run ui_app.py
```

### Common Issues

#### ChromeDriver Issues
```
Error: "ChromeDriver only supports Chrome version X"
```
**Solution**: Download matching ChromeDriver version
- Check Chrome version: `google-chrome --version`
- Download from: https://googlechromelabs.github.io/chrome-for-testing/

#### Permission Issues
```
Error: "Permission denied: data/"
```
**Solution**: Fix directory permissions
```bash
chmod 755 data/
mkdir -p data/{visualizations,reports}
```

#### Memory Issues (Docker)
```
Error: "Chrome crashed"
```
**Solution**: Increase shared memory
```yaml
# docker-compose.yml
services:
  threadsrecon:
    shm_size: '2gb'
```

#### Authentication Issues
```
Error: "Account requires verification"
```
**Solutions**:
- Use anonymous access (remove credentials)
- Verify account manually first
- Use app-specific password
- Try different user agent

---

## Security Best Practices

### Credential Management
- **Never commit** settings.yaml with real credentials
- Use environment variables for sensitive data
- Rotate passwords regularly
- Use dedicated research accounts

### Data Privacy
- **Local storage only** - no cloud uploads
- Regular data cleanup
- Secure deletion of sensitive reports
- Compliance with local privacy laws

### Operational Security
- **VPN usage** for sensitive research
- **Virtual environments** for isolation
- **Regular updates** of dependencies
- **Monitoring** for unusual behavior

---

## Performance Optimization

### Memory Management
```yaml
ScraperSettings:
  browser_options:
    disabled_features:
      - extensions
      - plugins
      - background-sync
      - background-fetch
```

### Network Optimization
```yaml
ScraperSettings:
  delays:
    min_wait: 1           # Balance speed vs. detection
    max_wait: 2
  retries:
    max_attempts: 3       # Avoid excessive retries
```

### Storage Optimization
- **Regular cleanup** of old data files
- **Compression** for archived data
- **Selective analysis** using date ranges
- **Artifact management** in data/ directory

---

## Integration Examples

### CI/CD Pipeline
```yaml
# Automated monitoring configuration
ScraperSettings:
  usernames: ${TARGET_USERS}
  browser_options:
    headless: true

WarningSystem:
  token: ${TELEGRAM_TOKEN}
  chat_id: ${TELEGRAM_CHAT_ID}
```

### Research Workflow
```yaml
# Academic research configuration
AnalysisSettings:
  keywords:
    - ${RESEARCH_TERMS}
  date_range:
    start: ${STUDY_START_DATE}
    end: ${STUDY_END_DATE}
```

### Brand Monitoring
```yaml
# Corporate monitoring setup
WarningSystem:
  priority_keywords:
    HIGH:
      - ${BRAND_NAME}
      - "data breach"
      - "security incident"
    MEDIUM:
      - ${COMPETITOR_NAMES}
      - "product launch"
```

This configuration guide ensures optimal performance, security, and reliability for your threadsrecon deployment.