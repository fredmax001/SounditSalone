#!/bin/bash
# Sound It CLI Installation Script

set -e

echo "=================================="
echo "  Sound It CLI Installer"
echo "=================================="
echo ""

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.8"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then 
    echo "Error: Python 3.8 or higher is required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✓ Python version: $PYTHON_VERSION"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "Error: pip3 is not installed"
    exit 1
fi

echo "✓ pip3 found"

# Install the CLI
echo ""
echo "Installing Sound It CLI..."
pip3 install -e .

# Verify installation
if command -v soundit &> /dev/null; then
    echo ""
    echo "=================================="
    echo "  Installation Complete!"
    echo "=================================="
    echo ""
    echo "Usage:"
    echo "  soundit --help"
    echo "  soundit auth login"
    echo "  soundit admin stats"
    echo ""
    echo "For more info: soundit --help"
else
    echo ""
    echo "Warning: soundit command not found in PATH"
    echo "You may need to add Python's bin directory to your PATH"
    echo "Try: export PATH=\"\$PATH:\$(python3 -m site --user-base)/bin\""
fi
