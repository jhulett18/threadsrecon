# threadsrecon GUI - Quick Start Guide

Get up and running with the threadsrecon GUI in 5 minutes.

## 🎯 Prerequisites Checklist

Before starting, ensure you have:
- [ ] **Python 3.8+** installed
- [ ] **Google Chrome** or Chromium browser
- [ ] **Terminal/Command Prompt** access
- [ ] **Internet connection** for downloads

## 🚀 5-Minute Setup

### Step 1: Install System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install python3-venv chromium-chromedriver wkhtmltopdf
```

**macOS:**
```bash
brew install chromedriver wkhtmltopdf
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

**Windows:**
- Download ChromeDriver from [chrome-for-testing](https://googlechromelabs.github.io/chrome-for-testing/)
- Download wkhtmltopdf from [official site](https://wkhtmltopdf.org/downloads.html)
- Add both to your PATH

### Step 2: Get the Code
```bash
git clone https://github.com/jhulett18/threadsrecon-gui.git
cd threadsrecon-gui
```

### Step 3: Setup Python Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate it
source venv/bin/activate  # Linux/macOS
# OR
venv\Scripts\activate     # Windows

# Install GUI dependencies
pip install streamlit pyyaml
```

### Step 4: Quick Configuration
```bash
# The GUI includes a default settings.yaml template
# You can edit it directly in the GUI or use your text editor

# For immediate testing, the default settings work with public usernames
```

### Step 5: Launch GUI
```bash
streamlit run ui_app.py
```

**🎉 Success!** The GUI should open at `http://localhost:8501`

## ⚡ First Run

### 1. Environment Check
- Look for **green checkmarks** in the sidebar
- If you see red X marks, install the missing dependencies

### 2. Quick Test
1. Enter a public username (e.g., `zuck`)
2. Select **"Scrape Only"** stage
3. Check **"Run in Background"**
4. Click **"▶ Run Pipeline"**

### 3. Watch the Logs
- Switch to the **"Run"** tab
- Watch real-time logs stream
- Wait for completion message

### 4. View Results
- Go to **"Artifacts"** tab
- Expand JSON data to see scraped profiles
- Check for generated visualizations

## 🔧 Troubleshooting

### GUI Won't Start
```bash
# Check Python version
python3 --version  # Should be 3.8+

# Reinstall Streamlit
pip install --upgrade streamlit

# Try different port
streamlit run ui_app.py --server.port 8502
```

### Environment Validation Fails
```bash
# Run validation script
./scripts/validate_env.sh

# Check specific issues:
which chromedriver
which wkhtmltopdf
ls -la data/  # Check write permissions
```

### ChromeDriver Issues
```bash
# Check Chrome version
google-chrome --version

# Download matching ChromeDriver
# From: https://googlechromelabs.github.io/chrome-for-testing/
```

## 📚 Next Steps

Once you have the GUI running:

1. **📖 Read [CONFIGURATION.md](CONFIGURATION.md)** - Comprehensive setup guide
2. **🔧 Configure settings.yaml** - Add your target usernames and preferences  
3. **🧪 Run [tests_gui.md](tests_gui.md)** - Verify all features work
4. **🛡️ Review security settings** - Protect credentials and data

## 💡 Pro Tips

- **Start with "Scrape Only"** to test connectivity
- **Use public usernames** for initial testing
- **Enable headless mode** for faster scraping
- **Check logs** if anything fails
- **Save settings** before running pipelines

## 🆘 Need Help?

- **Installation issues**: See [INSTALLATION.md](INSTALLATION.md)
- **Configuration problems**: See [CONFIGURATION.md](CONFIGURATION.md)  
- **GUI not working**: See [tests_gui.md](tests_gui.md) for debugging steps
- **Core functionality**: Check main threadsrecon documentation

---

**🎯 Goal**: Get from zero to working GUI in under 5 minutes!
**✅ Success criteria**: GUI loads, environment validates, test scrape completes