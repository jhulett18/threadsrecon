#!/bin/bash

# threadsrecon Installation Script
# This script sets up threadsrecon with the enhanced CLI interface

set -e

echo "🚀 threadsrecon Installation Script"
echo "=================================="

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Virtual environment detected: $VIRTUAL_ENV"
    USE_VENV=true
else
    echo "⚠️  No virtual environment detected"
    echo "   Creating one for you..."
    python3 -m venv venv
    source venv/bin/activate
    echo "✅ Virtual environment created and activated"
    USE_VENV=false
fi

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install --upgrade pip
pip install setuptools wheel

# Install dependencies one by one to avoid conflicts
echo "Installing core dependencies..."
pip install beautifulsoup4 requests PyYAML selenium

echo "Installing analysis dependencies..."
pip install pandas numpy scipy nltk textblob

echo "Installing visualization dependencies..."
pip install matplotlib plotly networkx

echo "Installing additional dependencies..."
pip install json2html pdfkit python-telegram-bot urllib3 kaleido

# Create a symbolic link for easy access
echo ""
echo "🔧 Setting up threadsrecon CLI..."
SCRIPT_PATH="$(pwd)/threadsrecon"

if [[ ":$PATH:" != *":$(pwd):"* ]]; then
    echo "Adding current directory to PATH for this session..."
    export PATH="$PATH:$(pwd)"
fi

# Test the installation
echo ""
echo "🧪 Testing installation..."
if [[ -x "$SCRIPT_PATH" ]]; then
    echo "✅ threadsrecon script is ready!"
    echo ""
    echo "🎯 Usage Examples:"
    echo "  ./threadsrecon scrape -u username1 username2"
    echo "  ./threadsrecon all -u target_user --headless"
    echo "  ./threadsrecon analyze --keywords 'crypto bitcoin'"
    echo "  ./threadsrecon report --output-dir /custom/path"
    echo ""
    echo "📖 For full help: ./threadsrecon --help"
    echo "📖 For command help: ./threadsrecon scrape --help"
    echo ""
    echo "💡 Alternative usage (from anywhere):"
    echo "   cd $(pwd)"
    echo "   python3 main.py scrape -u username"
else
    echo "❌ Installation may have failed."
fi

echo ""
echo "🎉 Installation complete!"

if [[ "$USE_VENV" == false ]]; then
    echo ""
    echo "💡 To use threadsrecon in the future:"
    echo "   source venv/bin/activate"
    echo "   ./threadsrecon scrape -u your_target_username"
fi

echo ""
echo "🔗 Optional: Add to your ~/.bashrc for global access:"
echo "   echo 'export PATH=\"\$PATH:$(pwd)\"' >> ~/.bashrc"