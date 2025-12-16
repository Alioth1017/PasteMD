# Build and Release Scripts

This directory contains scripts for building and releasing PasteMD.

## Scripts

### build_macos.sh
Builds the macOS application using PyInstaller.

**Usage:**
```bash
./scripts/build_macos.sh
```

**Output:**
- `dist/PasteMD.app` - macOS application bundle
- `dist/PasteMD` - Standalone executable
- `release/PasteMD_macOS_v{version}` - Release binary

**Requirements:**
- Python 3.10+
- All dependencies from requirements.txt
- PyInstaller (installed automatically)

### build.sh
Builds the Windows application using Nuitka.

**Usage:**
```bash
./scripts/build.sh
```

**Output:**
- `nuitka/main.dist/` - Windows distribution directory
- After running Inno Setup: `Output/PasteMD_pandoc-Setup_v{version}.exe`

**Requirements:**
- Python 3.12+
- All dependencies from requirements.txt
- Nuitka (installed automatically)
- Inno Setup (for creating installer)

### create_release.sh
Creates a GitHub release with built artifacts.

**Usage:**
```bash
./scripts/create_release.sh
```

**Prerequisites:**
1. Build the application first (using build.sh or build_macos.sh)
2. Install GitHub CLI: `brew install gh` (macOS) or download from https://cli.github.com/
3. Authenticate: `gh auth login`

**What it does:**
1. Extracts version from installer.iss
2. Creates release notes
3. Creates a draft GitHub release
4. Uploads all files from `release/` directory

**Note:** The release is created as a draft, allowing you to review before publishing.

## Automated Release (GitHub Actions)

For automated releases, see [.github/workflows/build-release.yml](../.github/workflows/build-release.yml).

### Trigger Release via Tag
```bash
git tag v0.1.6.3
git push origin v0.1.6.3
```

### Trigger Release Manually
1. Go to GitHub → Actions → "Build and Release"
2. Click "Run workflow"
3. Enter version number
4. Click "Run workflow"

## Build Process Overview

### macOS Build Steps
1. Clean previous builds
2. Install dependencies
3. Build with PyInstaller
4. Create standalone executable
5. Optionally create DMG (if create-dmg installed)

### Windows Build Steps
1. Clean previous builds
2. Install dependencies
3. Build with Nuitka (onedir mode)
4. Use Inno Setup to create installer

## Troubleshooting

### macOS: "PyInstaller not found"
```bash
pip install pyinstaller
```

### macOS: "create-dmg not found" (optional)
```bash
brew install create-dmg
```

### Windows: Nuitka compilation errors
- Ensure you have Visual Studio Build Tools installed
- Use Python 3.12+ for best compatibility

### GitHub CLI errors
```bash
# Install
brew install gh  # macOS
# or download from https://cli.github.com/

# Authenticate
gh auth login
```

## Platform-Specific Dependencies

The `requirements.txt` file uses platform markers to handle platform-specific dependencies:

```txt
pywin32; sys_platform == 'win32'  # Windows only
```

This ensures that Windows-only packages are not installed on macOS/Linux.
