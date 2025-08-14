# threadsrecon Installation Guide

Complete step-by-step installation guide for all platforms and deployment methods.

## Quick Start Checklist

- [ ] Python 3.8+ installed
- [ ] ChromeDriver installed and in PATH
- [ ] wkhtmltopdf installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] settings.yaml configured
- [ ] Environment validation passed

---

## Platform-Specific Installation

### Ubuntu/Debian Systems

#### 1. System Prerequisites
```bash
# Update package list
sudo apt update

# Install Python and development tools
sudo apt install python3 python3-pip python3-venv python3-full

# Install system dependencies
sudo apt install chromium-browser chromium-chromedriver wkhtmltopdf

# Install additional dependencies for GUI
sudo apt install xvfb  # For headless display (optional)
```

#### 2. Verify Installation
```bash
# Check versions
python3 --version          # Should be 3.8+
chromedriver --version     # Should match Chrome version
wkhtmltopdf --version      # Should show version info
```

#### 3. Setup Project
```bash
# Clone repository
git clone https://github.com/jhulett18/threadsrecon-gui.git
cd threadsrecon-gui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt
pip install streamlit pyyaml

# Validate environment
./scripts/validate_env.sh
```

### macOS Systems

#### 1. Install Homebrew (if not installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

#### 2. Install Dependencies
```bash
# Install Python
brew install python

# Install ChromeDriver and wkhtmltopdf
brew install chromedriver wkhtmltopdf

# Remove quarantine from ChromeDriver (security requirement)
xattr -d com.apple.quarantine /opt/homebrew/bin/chromedriver
```

#### 3. Setup Project
```bash
# Clone and setup
git clone https://github.com/jhulett18/threadsrecon-gui.git
cd threadsrecon-gui

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install streamlit pyyaml

# Validate installation
./scripts/validate_env.sh
```

### Windows Systems

#### 1. Install Python
- Download Python 3.8+ from [python.org](https://www.python.org/downloads/)
- **Important**: Check "Add Python to PATH" during installation
- Verify: Open Command Prompt and run `python --version`

#### 2. Install ChromeDriver
```powershell
# Option 1: Manual installation
# 1. Check Chrome version: chrome://version/
# 2. Download matching ChromeDriver from https://googlechromelabs.github.io/chrome-for-testing/
# 3. Extract to C:\Program Files\chromedriver\
# 4. Add C:\Program Files\chromedriver\ to PATH

# Option 2: Using Chocolatey (if installed)
choco install chromedriver

# Verify installation
chromedriver --version
```

#### 3. Install wkhtmltopdf
```powershell
# Download from https://wkhtmltopdf.org/downloads.html
# Install to default location: C:\Program Files\wkhtmltopdf\
# Add C:\Program Files\wkhtmltopdf\bin\ to PATH

# Verify installation
wkhtmltopdf --version
```

#### 4. Setup Project
```powershell
# Clone repository
git clone https://github.com/jhulett18/threadsrecon-gui.git
cd threadsrecon-gui

# Create virtual environment
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
pip install streamlit pyyaml

# Update settings.yaml paths for Windows
# Edit settings.yaml and set:
# chromedriver: C:\Program Files\chromedriver\chromedriver.exe
# path_to_wkhtmltopdf: C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe
```

---

## Docker Installation

### Docker Compose (Recommended)

#### 1. Prerequisites
```bash
# Install Docker and Docker Compose
sudo apt install docker.io docker-compose

# Add user to docker group (Ubuntu)
sudo usermod -aG docker $USER
# Log out and back in for group changes to take effect
```

#### 2. Docker Setup
```bash
# Clone repository
git clone https://github.com/jhulett18/threadsrecon-gui.git
cd threadsrecon-gui

# Create docker-compose.yml for GUI
cat > docker-compose-gui.yml << EOF
version: '3.8'

services:
  threadsrecon-gui:
    build: .
    ports:
      - "8501:8501"
    volumes:
      - ./settings.yaml:/app/settings.yaml:ro
      - ./data:/app/data
      - /dev/shm:/dev/shm
    environment:
      - PYTHONUNBUFFERED=1
      - DISPLAY=:99
    command: streamlit run ui_app.py --server.address=0.0.0.0
    shm_size: '2gb'  # Important for Chrome stability
EOF

# Update Dockerfile to include Streamlit
echo "RUN pip install streamlit pyyaml" >> Dockerfile
echo "EXPOSE 8501" >> Dockerfile
```

#### 3. Build and Run
```bash
# Build container
docker-compose -f docker-compose-gui.yml build

# Run GUI
docker-compose -f docker-compose-gui.yml up

# Access at http://localhost:8501
```

### Docker Standalone

```bash
# Build image
docker build -t threadsrecon-gui .

# Run container
docker run -d \
  --name threadsrecon-gui \
  -p 8501:8501 \
  -v $(pwd)/settings.yaml:/app/settings.yaml:ro \
  -v $(pwd)/data:/app/data \
  --shm-size=2g \
  threadsrecon-gui streamlit run ui_app.py --server.address=0.0.0.0
```

---

## Cloud Deployment

### AWS EC2

#### 1. Launch Instance
```bash
# Use Ubuntu 22.04 LTS AMI
# Instance type: t3.medium (minimum for Chrome)
# Security group: Allow port 8501 from your IP
```

#### 2. Setup on Instance
```bash
# Connect via SSH
ssh -i your-key.pem ubuntu@your-instance-ip

# Install dependencies
sudo apt update
sudo apt install python3-pip python3-venv chromium-browser chromium-chromedriver wkhtmltopdf

# Clone and setup project
git clone https://github.com/jhulett18/threadsrecon-gui.git
cd threadsrecon-gui
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install streamlit pyyaml

# Configure settings.yaml
# Run with public access
streamlit run ui_app.py --server.address=0.0.0.0 --server.port=8501
```

### Google Cloud Platform

#### 1. Cloud Run Deployment
```bash
# Create Dockerfile for Cloud Run
cat > Dockerfile.cloudrun << EOF
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \\
    chromium \\
    chromium-driver \\
    wkhtmltopdf \\
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install streamlit pyyaml

COPY . .

EXPOSE 8080
CMD streamlit run ui_app.py --server.address=0.0.0.0 --server.port=8080
EOF

# Deploy to Cloud Run
gcloud run deploy threadsrecon-gui --source . --port 8080
```

---

## Troubleshooting Installation Issues

### Common ChromeDriver Issues

#### Version Mismatch
```bash
# Check Chrome version
google-chrome --version
# or
chromium-browser --version

# Download matching ChromeDriver
# From: https://googlechromelabs.github.io/chrome-for-testing/
```

#### Permission Issues (Linux/macOS)
```bash
# Make ChromeDriver executable
chmod +x /usr/local/bin/chromedriver

# Fix ownership
sudo chown root:root /usr/local/bin/chromedriver
```

#### PATH Issues (Windows)
```powershell
# Check if ChromeDriver is in PATH
where chromedriver

# Add to PATH if missing
setx PATH "%PATH%;C:\Program Files\chromedriver"
# Restart Command Prompt after adding to PATH
```

### Python Environment Issues

#### Virtual Environment Creation Fails
```bash
# Ubuntu: Install python3-venv
sudo apt install python3-venv

# Alternative: Use conda
conda create -n threadsrecon python=3.9
conda activate threadsrecon
```

#### Package Installation Fails
```bash
# Upgrade pip first
pip install --upgrade pip

# Install with verbose output for debugging
pip install -v streamlit pyyaml

# Clear pip cache if issues persist
pip cache purge
```

### Memory and Performance Issues

#### Docker Memory Issues
```yaml
# Increase shared memory in docker-compose.yml
services:
  threadsrecon-gui:
    shm_size: '2gb'  # Increase if Chrome crashes
    
# Alternative: Use tmpfs mount
tmpfs:
  - /tmp
  - /var/tmp
```

#### System Resource Requirements
```bash
# Minimum requirements:
# - 2GB RAM
# - 1GB free disk space
# - 2 CPU cores (recommended)

# Check available resources
free -h        # Memory
df -h         # Disk space
nproc         # CPU cores
```

### Network and Firewall Issues

#### Port Access Issues
```bash
# Check if port 8501 is available
netstat -tulpn | grep 8501

# Kill process using port if needed
sudo kill -9 $(lsof -t -i:8501)

# Alternative port
streamlit run ui_app.py --server.port 8502
```

#### Firewall Configuration
```bash
# Ubuntu: Allow port through UFW
sudo ufw allow 8501

# CentOS/RHEL: Allow port through firewalld
sudo firewall-cmd --permanent --add-port=8501/tcp
sudo firewall-cmd --reload
```

---

## Verification and Testing

### Installation Verification
```bash
# Run environment validation
./scripts/validate_env.sh

# Expected output:
# ✅ All environment checks passed
```

### GUI Testing
```bash
# Start GUI
streamlit run ui_app.py

# Open browser to http://localhost:8501
# Verify:
# - Environment status shows green checkmarks
# - Settings tab loads YAML content
# - All tabs are accessible
```

### End-to-End Testing
```bash
# Test with minimal configuration
# 1. Enter test username in GUI
# 2. Select "scrape" stage
# 3. Run pipeline
# 4. Check for successful execution
# 5. Verify artifacts are generated
```

---

## Next Steps After Installation

1. **Configure settings.yaml** - See [CONFIGURATION.md](CONFIGURATION.md)
2. **Run validation script** - `./scripts/validate_env.sh`
3. **Test with sample data** - Use public usernames for testing
4. **Review security settings** - Ensure credentials are protected
5. **Set up monitoring** - Configure Telegram alerts if needed

For detailed configuration options, see [CONFIGURATION.md](CONFIGURATION.md).
For testing procedures, see [tests_gui.md](tests_gui.md).