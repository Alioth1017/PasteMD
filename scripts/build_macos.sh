#!/bin/bash
# PasteMD macOS Build Script
# This script builds the macOS application bundle

set -e  # Exit on error

echo "========================================="
echo "PasteMD macOS Build Script"
echo "========================================="

# Get version from main file
VERSION="0.1.6.3"
echo "Building version: $VERSION"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build/
rm -rf dist/
rm -rf release/

# Create release directory
mkdir -p release

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install pyinstaller

# Verify PyInstaller installation
if ! command -v pyinstaller &> /dev/null; then
    echo "Error: PyInstaller installation failed"
    exit 1
fi

# Build with PyInstaller
echo "Building with PyInstaller..."
pyinstaller \
    --name=PasteMD \
    --windowed \
    --onefile \
    --icon=assets/icons/logo.png \
    --add-data="pastemd/lua:pastemd/lua" \
    --add-data="pastemd/i18n/locales:pastemd/i18n/locales" \
    --add-data="assets/icons:assets/icons" \
        --hidden-import=tkinter \
    --hidden-import=pastemd.platforms.macos.app_detector \
    --hidden-import=pastemd.platforms.macos.clipboard \
    --hidden-import=pastemd.platforms.macos.hotkey \
    --hidden-import=pastemd.platforms.macos.notification \
    --hidden-import=pastemd.platforms.macos.document_inserter \
        --hidden-import=pystray._appkit \
        --hidden-import=PIL._tkinter_finder \
    pastemd/__main__.py

# Copy to release directory
echo "Copying to release directory..."
cp dist/PasteMD release/PasteMD_macOS_v${VERSION}

# Create DMG (if create-dmg is available)
if command -v create-dmg &> /dev/null; then
    echo "Creating DMG..."
    create-dmg \
        --volname "PasteMD $VERSION" \
        --volicon "assets/icons/logo.png" \
        --window-pos 200 120 \
        --window-size 600 300 \
        --icon-size 100 \
        --app-drop-link 425 120 \
        release/PasteMD_macOS_v${VERSION}.dmg \
        dist/
fi

echo "Build completed successfully!"
echo "Output directory: release/"
