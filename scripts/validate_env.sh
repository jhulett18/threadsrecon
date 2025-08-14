#!/bin/sh
#
# validate_env.sh - Environment validation for threadsrecon
# Checks chromedriver, wkhtmltopdf, and data directory write access
# POSIX shell compatible
#

check_chromedriver() {
    if command -v chromedriver >/dev/null 2>&1; then
        echo "PASS: ChromeDriver found at $(command -v chromedriver)"
        return 0
    elif [ -f "/usr/local/bin/chromedriver" ]; then
        echo "PASS: ChromeDriver found at /usr/local/bin/chromedriver"
        return 0
    elif [ -f "./chromedriver" ]; then
        echo "PASS: ChromeDriver found at ./chromedriver"
        return 0
    else
        echo "FAIL: ChromeDriver not found in PATH or standard locations"
        return 1
    fi
}

check_wkhtmltopdf() {
    if command -v wkhtmltopdf >/dev/null 2>&1; then
        echo "PASS: wkhtmltopdf found at $(command -v wkhtmltopdf)"
        return 0
    elif [ -f "/usr/bin/wkhtmltopdf" ]; then
        echo "PASS: wkhtmltopdf found at /usr/bin/wkhtmltopdf"
        return 0
    else
        echo "FAIL: wkhtmltopdf not found in PATH or /usr/bin/"
        return 1
    fi
}

check_data_access() {
    if [ ! -d "data" ]; then
        if mkdir "data" 2>/dev/null; then
            echo "PASS: Created data/ directory with write access"
            return 0
        else
            echo "FAIL: Cannot create data/ directory"
            return 1
        fi
    fi
    
    test_file="data/.write_test_$$"
    if echo "test" > "$test_file" 2>/dev/null; then
        rm -f "$test_file"
        echo "PASS: data/ directory has write access"
        return 0
    else
        echo "FAIL: data/ directory is not writable"
        return 1
    fi
}

main() {
    echo "threadsrecon Environment Validation"
    echo "=================================="
    
    exit_code=0
    
    check_chromedriver || exit_code=1
    check_wkhtmltopdf || exit_code=1
    check_data_access || exit_code=1
    
    echo ""
    if [ $exit_code -eq 0 ]; then
        echo "✅ All environment checks passed"
    else
        echo "❌ Some environment checks failed"
        echo ""
        echo "Installation hints:"
        echo "- ChromeDriver: https://googlechromelabs.github.io/chrome-for-testing/"
        echo "- wkhtmltopdf: https://wkhtmltopdf.org/downloads.html"
        echo "- Data directory: chmod 755 data/"
    fi
    
    exit $exit_code
}

main "$@"