# threadsrecon Enhanced CLI - Installation Fix

## ✅ Quick Solution for Installation Errors

The setuptools error you encountered is common with complex Python packages. Here's the working solution:

### Option 1: Use the Direct Script (Recommended)

```bash
# 1. Install dependencies without package installation
pip install beautifulsoup4 requests PyYAML selenium pandas numpy matplotlib plotly networkx nltk

# 2. Use the direct executable script
./threadsrecon scrape -u username1 username2
```

### Option 2: Use the Enhanced Python Script

```bash
# Run with enhanced CLI directly
python3 main.py scrape -u username1 username2 --headless --timeout 30
```

## 🚀 New Enhanced CLI Features

### Before (Old Way):
```bash
# Had to edit settings.yaml first
nano settings.yaml  # Edit usernames manually
python main.py scrape
```

### After (New Way):
```bash
# Everything via command line
./threadsrecon scrape -u username1 username2 --headless
./threadsrecon all -u target_user --output-dir /custom/path
./threadsrecon analyze --keywords "crypto bitcoin scam"
```

## 📁 Download Paths & Data Packaging

### Default Structure:
```
data/
├── profiles.json              # Raw scraped data (names, images, videos, posts)
├── analyzed_profiles.json     # Processed data with sentiment analysis
├── visualizations/            # PNG charts and graphs
│   ├── network_graph.png
│   ├── sentiment_chart.png
│   └── engagement_stats.png
└── reports/
    └── report_TIMESTAMP.pdf   # Complete PDF report
```

### Custom Output Directory:
```bash
# Everything goes to custom location
./threadsrecon scrape -u username --output-dir /home/user/investigation1

# Results in:
# /home/user/investigation1/profiles.json
# /home/user/investigation1/visualizations/
# /home/user/investigation1/reports/report.pdf
```

## 🎯 What Data Gets Collected

### From Target Profile:
- ✅ **Names**: Display name, username
- ✅ **Images**: Profile picture URLs, post media URLs  
- ✅ **Videos**: Video URLs from posts (if any)
- ✅ **Posts**: Full text content with timestamps
- ✅ **Followers/Following**: Lists and counts
- ✅ **Bio**: Description and external links
- ⚠️ **Emails**: Only if mentioned in bio text (not directly accessible)

### Enhanced Analysis:
- Sentiment analysis of posts
- Keyword matching and frequency
- Activity patterns and timing
- Network relationship mapping
- Engagement metrics

## 🔧 All CLI Options

```bash
./threadsrecon COMMAND [OPTIONS]

Commands:
  scrape      # Collect data from threads.net
  analyze     # Process collected data
  visualize   # Generate charts and graphs
  report      # Create PDF report
  all         # Run complete pipeline

Key Options:
  -u, --usernames USER1 USER2    # Target usernames (multiple allowed)
  --output-dir DIR               # Custom output directory
  --headless / --no-headless     # Browser visibility
  --timeout SECONDS              # Page load timeout
  --keywords WORD1 WORD2         # Analysis keywords
  --chromedriver PATH            # Custom chromedriver path
  --config FILE                  # Custom settings file

Examples:
  ./threadsrecon scrape -u target_user --headless
  ./threadsrecon all -u user1 user2 --output-dir /tmp/case1
  ./threadsrecon analyze --keywords "crypto scam phishing"
  ./threadsrecon report --output-dir /home/user/investigation
```

## 🛠️ Troubleshooting

### If `./threadsrecon` doesn't work:
```bash
# Use Python directly
python3 main.py scrape -u username --headless

# Or activate virtual environment first
source venv/bin/activate
python3 main.py scrape -u username
```

### If you get permission errors:
```bash
chmod +x threadsrecon
chmod +x install.sh
```

### Missing Dependencies:
```bash
# Install step by step
pip install selenium beautifulsoup4 requests
pip install pandas numpy matplotlib
pip install PyYAML nltk textblob
```

## 🎉 Benefits of New CLI

1. **No YAML editing required** for common operations
2. **Custom output directories** for organized investigations  
3. **Multiple usernames** in single command
4. **Real-time configuration** via command line
5. **Professional CLI experience** with `--help` support
6. **Backward compatible** with existing workflows

The enhanced CLI eliminates the friction of editing configuration files while maintaining all the powerful OSINT capabilities of threadsrecon!