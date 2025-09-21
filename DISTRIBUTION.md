# 📦 Distribution Guide - Canvas Grade Widget

## 🎯 For End Users (Simple Installation)

### Option 1: Download Executable (Recommended)

1. **Download** the `CanvasGradeWidget_Fixed.exe` from the releases page
2. **Create folder** for the app (e.g., `C:\CanvasGradeWidget\`)
3. **Copy files** to the folder:
   - `CanvasGradeWidget_Fixed.exe`
   - `config.example.py` (rename to `config.py`)
4. **Edit config.py** with your Canvas details:
   ```python
   CANVAS_BASE_URL = "https://your-school.instructure.com"
   API_TOKEN = "your_api_token_here"
   THEME = "auto"  # or "light", "dark", "nord"
   ```
5. **Run** `CanvasGradeWidget_Fixed.exe`

> ✨ **Latest Features**: This version includes enhanced UI with gradient themes, student profile integration with circular profile pictures, and improved control button styling.

## 🛠️ For Developers (Build from Source)

### Prerequisites

- Python 3.8+ installed
- Git installed
- Canvas LMS access with API token

### Quick Build

```bash
# Clone and setup
git clone https://github.com/your-username/canvas-grade-widget.git
cd canvas-grade-widget
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies and build
pip install -r requirements.txt
python build_executable.py
```

### Manual Build Steps

```bash
# PyInstaller is included in requirements.txt
# Create executable using the build script (recommended)
python build_executable.py

# OR create executable using spec file directly
pyinstaller canvas_grade_widget.spec --noconfirm

# OR create executable with PyInstaller directly
pyinstaller --onefile --windowed --name "CanvasGradeWidget_Fixed" canvas_grade_widget.py

# Find executable in dist/ folder
```

## 📁 File Structure After Build

```
dist/
├── CanvasGradeWidget.exe    # Main executable (Windows)
└── config.example.py        # Configuration template

build/                       # Build artifacts (can be deleted)
canvas_grade_widget.spec     # PyInstaller configuration
```

## 🔧 Build Configuration

The build process uses `canvas_grade_widget.spec` with these settings:

### Key Features

- **Single File**: Everything bundled in one .exe file
- **No Console**: GUI-only application (no command prompt window)
- **Hidden Imports**: All required modules included
- **Config Template**: Includes config.example.py for users

### Customization Options

- **Add Icon**: Set `icon='path/to/icon.ico'` in the spec file
- **Console Mode**: Set `console=True` for debugging
- **Optimization**: Adjust `optimize` level (0=none, 1=basic, 2=more)

## 🚀 Distribution Methods

### Method 1: GitHub Releases

1. Build executable: `python build_executable.py`
2. Create GitHub release
3. Upload `CanvasGradeWidget.exe` and `config.example.py`
4. Users download and follow setup guide

### Method 2: Portable Package

```bash
# Create distribution folder
mkdir CanvasGradeWidget-Portable
cp dist/CanvasGradeWidget.exe CanvasGradeWidget-Portable/
cp config.example.py CanvasGradeWidget-Portable/config.py
echo "Edit config.py with your Canvas details" > CanvasGradeWidget-Portable/README.txt

# Zip for distribution
zip -r CanvasGradeWidget-Portable.zip CanvasGradeWidget-Portable/
```

### Method 3: Installer (Future)

Consider using tools like:

- **Inno Setup** (Windows)
- **NSIS** (Windows)
- **WiX Toolset** (Windows MSI)

## 📋 User Instructions Template

```markdown
# Canvas Grade Widget Setup

## Step 1: Download

Download CanvasGradeWidget.exe from the releases page

## Step 2: Configure

1. Copy config.example.py to config.py
2. Edit config.py with your details:
   - Canvas URL: https://your-school.instructure.com
   - API Token: (from Canvas Account → Settings → New Access Token)
   - Theme: auto, light, dark, or nord

## Step 3: Run

Double-click CanvasGradeWidget.exe to start!

## Troubleshooting

- Windows may show security warning - click "Run anyway"
- If it doesn't start, run from command prompt to see errors
- Make sure config.py is in the same folder as the .exe
```

## 🔍 Testing Checklist

Before distributing:

- [ ] ✅ Executable runs without Python installed
- [ ] ✅ Config file is read correctly
- [ ] ✅ All themes work properly
- [ ] ✅ Canvas API connection works
- [ ] ✅ GUI displays correctly
- [ ] ✅ Thread cleanup works (no hanging processes)
- [ ] ✅ Settings dialog functions properly
- [ ] ✅ Auto-restart on theme change works

## 📈 Advanced Build Options

### Cross-Platform Builds

- **Windows**: Use PyInstaller on Windows
- **macOS**: Use PyInstaller on macOS (creates .app bundle)
- **Linux**: Use PyInstaller on Linux (creates binary)

### Size Optimization

```bash
# Use UPX compression
pyinstaller --upx-dir=/path/to/upx canvas_grade_widget.spec

# Exclude unnecessary modules
pyinstaller --exclude-module tkinter canvas_grade_widget.spec
```

### Debug Build

```bash
# Console version for debugging
pyinstaller --console canvas_grade_widget.py
```

---

**Happy Building! 🎉**
