#!/bin/bash
# Create GitHub Release Script
# This script creates a GitHub release with built artifacts

set -e  # Exit on error

echo "========================================="
echo "PasteMD Release Creation Script"
echo "========================================="

# Get version from installer.iss
VERSION=$(grep -oP '#define MyAppVersion "\K[^"]+' installer.iss 2>/dev/null || echo "0.1.6.3")
TAG="v${VERSION}"

echo "Creating release for version: $VERSION"

# Check if gh CLI is installed
if ! command -v gh &> /dev/null; then
    echo "Error: GitHub CLI (gh) is not installed."
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Check if release directory exists
if [ ! -d "release" ]; then
    echo "Error: release directory not found. Run build script first."
    exit 1
fi

# Create release notes
cat > release_notes.md << EOF
## PasteMD ${VERSION}

### Features
- Markdown to Word/WPS conversion
- Markdown table to Excel
- HTML rich text support
- System tray integration
- Multi-language support (中文/English)

### Installation

#### Windows
1. Download \`PasteMD_pandoc-Setup_v${VERSION}.exe\`
2. Run the installer
3. Make sure Pandoc is installed: https://pandoc.org/installing.html

#### macOS
1. Download \`PasteMD_macOS_v${VERSION}\` (if available)
2. Make it executable: \`chmod +x PasteMD_macOS_v${VERSION}\`
3. Run the application
4. Install Pandoc: \`brew install pandoc\`

### Requirements
- Pandoc 2.0+ (required)
- Python 3.12+ (for development only)

### Changelog
See full changelog in the repository.

---
**Note**: This is an automated release. Please report any issues on GitHub.
EOF

# Create release
echo "Creating GitHub release..."
gh release create "$TAG" \
    release/* \
    --title "PasteMD ${VERSION}" \
    --notes-file release_notes.md \
    --draft

echo "Release created as draft. Review at:"
echo "https://github.com/$(gh repo view --json nameWithOwner -q .nameWithOwner)/releases"
echo ""
echo "To publish the release, run:"
echo "gh release edit $TAG --draft=false"

# Clean up
rm -f release_notes.md
