#!/bin/bash
# PasteMD Build Script
# This script builds the application using Nuitka and creates a release package

set -e  # Exit on error

echo "========================================="
echo "PasteMD Build Script"
echo "========================================="

# Get version from installer.iss
VERSION=$(grep -oP '#define MyAppVersion "\K[^"]+' installer.iss)
echo "Building version: $VERSION"

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf nuitka/
rm -rf build/
rm -rf dist/
rm -rf release/

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt
pip install nuitka ordered-set

# Build with Nuitka
echo "Building with Nuitka..."
python -m nuitka \
    --standalone \
    --output-dir=nuitka \
    --output-filename=PasteMD.exe \
    --windows-icon-from-ico=assets/icons/logo.ico \
    --company-name="RichQAQ" \
    --product-name="PasteMD" \
    --file-version="$VERSION" \
    --product-version="$VERSION" \
    --file-description="Markdown to Word/Excel clipboard tool" \
    --copyright="Copyright (c) 2024 RichQAQ" \
    --windows-console-mode=disable \
    --enable-plugin=tk-inter \
    --include-data-dir=pastemd/lua=pastemd/lua \
    --include-data-dir=pastemd/i18n/locales=pastemd/i18n/locales \
    --include-data-dir=assets/icons=assets/icons \
    --follow-imports \
    --assume-yes-for-downloads \
    pastemd/__main__.py

echo "Build completed successfully!"
echo "Output directory: nuitka/main.dist/"
