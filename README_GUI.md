# threadsrecon GUI

Local graphical interface for the threadsrecon CLI tool. Provides an easy-to-use web interface for non-technical users to run threads.net OSINT analysis without command-line knowledge.

## Prerequisites

### Required Software
- **Python 3.8+** with pip
- **Google Chrome/Chromium** (latest stable version)
- **ChromeDriver** matching your Chrome version
- **wkhtmltopdf** for PDF report generation

### Binary Locations
The GUI expects these binaries to be available:
- ChromeDriver: `/usr/local/bin/chromedriver` or in PATH
- wkhtmltopdf: `/usr/bin/wkhtmltopdf` or in PATH

## Installation

### Option 1: Virtual Environment (Recommended)

1. **Clone and setup:**
```bash
git clone https://github.com/offseq/threadsrecon.git
cd threadsrecon
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. **Install dependencies:**
```bash
pip install streamlit pyyaml
pip install -r requirements.txt
```

3. **Install system dependencies:**

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install chromium-browser chromium-chromedriver wkhtmltopdf
```

**macOS (via Homebrew):**
```bash
brew install chromedriver wkhtmltopdf
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

**Windows:**
- Download ChromeDriver from [Chrome for Testing](https://googlechromelabs.github.io/chrome-for-testing/)
- Download wkhtmltopdf from [official site](https://wkhtmltopdf.org/downloads.html)
- Add both to your PATH

4. **Create configuration:**
```bash
cp settings.yaml.example settings.yaml
nano settings.yaml  # Edit with your settings
```

5. **Launch GUI:**
```bash
streamlit run ui_app.py
```

The interface will open in your browser at `http://localhost:8501`

### Option 2: Docker Compose

1. **Add GUI service to docker-compose.yml:**
```yaml
services:
  threadsrecon:
    # existing service configuration...
  
  threadsrecon-gui:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./settings.yaml:/app/settings.yaml:ro
      - ./data:/app/data
      - /dev/shm:/dev/shm  # Required for Chrome stability
    environment:
      - PYTHONUNBUFFERED=1
    command: streamlit run ui_app.py --server.address=0.0.0.0
    depends_on:
      - threadsrecon
```

2. **Update Dockerfile to include Streamlit:**
```dockerfile
# Add to existing Dockerfile
RUN pip install streamlit pyyaml
EXPOSE 8501
```

3. **Launch:**
```bash
docker-compose up threadsrecon-gui
```

Access at `http://localhost:8501`

## Usage

### 1. Environment Check
- Green checkmarks indicate all prerequisites are met
- Red X marks show missing dependencies with installation hints
- The Run button is disabled until all checks pass

### 2. Configure Settings
- **Settings tab**: Edit settings.yaml directly in the GUI
- Validate YAML syntax before saving
- All threadsrecon configuration options are supported

### 3. Quick Run
- **Sidebar**: Enter target usernames (comma-separated)
- Select pipeline stage: All Stages, Scrape Only, Analyze Only, etc.
- Toggle "Run in Background" to hide browser window
- Click "▶ Run Pipeline"

### 4. Monitor Progress
- **Run tab**: View live logs during execution
- Real-time stdout/stderr streaming
- Exit code and completion status displayed

### 5. Review Results
- **Artifacts tab**: Preview generated data
- JSON viewers for profiles and analysis results
- Image gallery for visualizations
- Direct links to PDF reports

## Configuration

The GUI uses the same `settings.yaml` as the CLI tool. Key sections:

```yaml
ScraperSettings:
  chromedriver: /usr/local/bin/chromedriver
  usernames:
    - target_username1
    - target_username2
  browser_options:
    headless: true

ReportGeneration:
  path_to_wkhtmltopdf: /usr/bin/wkhtmltopdf
  output_path: data/reports/report.pdf
```

**Note:** Usernames entered in the GUI will automatically update the `ScraperSettings.usernames` list in your YAML file.

## Troubleshooting

### Common Issues

**ChromeDriver version mismatch:**
```
Error: "ChromeDriver only supports Chrome version XX"
Solution: Download matching version from chrome-for-testing
```

**Permission denied on data directory:**
```
Error: "Cannot write to data/ directory"
Solution: chmod 755 data/ or check file ownership
```

**wkhtmltopdf not found:**
```
Error: "wkhtmltopdf not found at [path]"
Solution: Install wkhtmltopdf and update path in settings.yaml
```

**Invalid YAML syntax:**
```
Error: "Invalid YAML syntax on line X"
Solution: Use YAML validator or restore from backup
```

**Streamlit port already in use:**
```
Error: "Port 8501 is already in use"
Solution: streamlit run ui_app.py --server.port 8502
```

**Docker shared memory issues:**
```
Error: "Chrome crashed"
Solution: Add shm_size: '2gb' to docker-compose.yml
```

### Performance Tips
- Use headless mode for faster scraping
- Close browser tabs to free memory
- Run on system with 2GB+ RAM
- Use SSD storage for better I/O performance

### Debug Mode
To troubleshoot scraping issues:
1. Uncheck "Run in Background"
2. Run "Scrape Only" stage
3. Watch browser automation in real-time

## Security Notes

- **Local only**: GUI runs on localhost, no external network access except threads.net
- **Credential storage**: Settings.yaml contains sensitive data - do not commit to version control
- **Data privacy**: All scraped data stays on your local machine
- **Anonymous access**: Tool can run without Instagram credentials (limited functionality)

## Environment Variables

- `THREADSRECON_HEADLESS`: Set by GUI based on "Run in Background" toggle
- `STREAMLIT_SERVER_PORT`: Change default port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Bind address (default: localhost)

## File Structure

```
threadsrecon/
├── ui_app.py              # GUI application
├── settings.yaml          # Configuration file
├── data/                  # Generated artifacts
│   ├── profiles.json      # Scraped profiles
│   ├── analyzed_profiles.json
│   ├── visualizations/    # PNG charts
│   └── reports/          # PDF reports
└── main.py               # CLI entry point
```

## Support

For GUI-specific issues:
1. Check this README first
2. Verify environment validation passes
3. Review logs in the Run tab
4. Test CLI functionality: `python main.py scrape`

For core threadsrecon issues, see main README.md