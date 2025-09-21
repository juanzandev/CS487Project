#!/usr/bin/env python3
"""
Build script for creating Canvas Grade Widget executable
"""

import os
import subprocess
import sys
import shutil


def clean_build():
    """Clean previous build artifacts"""
    print("🧹 Cleaning previous build artifacts...")

    directories_to_clean = ['build', 'dist', '__pycache__']
    for directory in directories_to_clean:
        if os.path.exists(directory):
            shutil.rmtree(directory)
            print(f"   ✓ Removed {directory}/")


def build_executable():
    """Build the executable using PyInstaller"""
    print("🔨 Building executable...")

    try:
        # Run PyInstaller with the spec file
        result = subprocess.run([
            sys.executable, '-m', 'PyInstaller',
            'canvas_grade_widget.spec'
        ], check=True, capture_output=True, text=True)

        print("   ✓ Build completed successfully!")
        return True

    except subprocess.CalledProcessError as e:
        print(f"   ❌ Build failed: {e}")
        print(f"   Error output: {e.stderr}")
        return False


def main():
    """Main build process"""
    print("🎓 Canvas Grade Widget - Build Script")
    print("=" * 40)

    # Check if PyInstaller is installed
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        print("❌ PyInstaller not found. Installing...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', 'pyinstaller'])

    # Clean previous builds
    clean_build()

    # Build executable
    if build_executable():
        print("\n🎉 Build Complete!")
        print(
            f"📁 Executable location: {os.path.abspath('dist/CanvasGradeWidget.exe')}")
        print("\n📋 Next steps:")
        print("   1. Copy config.example.py to config.py in the same folder as the .exe")
        print("   2. Edit config.py with your Canvas URL and API token")
        print("   3. Run CanvasGradeWidget.exe")
    else:
        print("\n❌ Build failed!")
        sys.exit(1)


if __name__ == '__main__':
    main()
