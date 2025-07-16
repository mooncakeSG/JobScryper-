#!/usr/bin/env python3
"""
Setup script for Auto Apply for Tech Jobs application
This script helps users install dependencies and set up the application.
"""

import subprocess
import sys
import os
import platform

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"🔧 {description}")
    print(f"{'='*50}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully!")
        if result.stdout:
            print(f"Output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed!")
        print(f"Error: {e.stderr}")
        return False

def check_python_version():
    """Check if Python version is compatible"""
    print("🔍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported!")
        print("Please upgrade to Python 3.8 or higher.")
        return False
    else:
        print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible!")
        return True

def install_dependencies():
    """Install Python dependencies"""
    print("\n📦 Installing Python dependencies...")
    
    # Upgrade pip first
    run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip")
    
    # Install requirements
    if os.path.exists("requirements.txt"):
        success = run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing requirements")
        if not success:
            print("⚠️ Some packages may have failed to install. Try installing them manually.")
    else:
        print("❌ requirements.txt not found!")
        return False
    
    return True

def install_playwright():
    """Install Playwright browsers"""
    print("\n🌐 Installing Playwright browsers...")
    
    # Install Playwright
    success1 = run_command(f"{sys.executable} -m pip install playwright", "Installing Playwright")
    
    # Install browsers
    success2 = run_command("playwright install", "Installing Playwright browsers")
    
    if not success2:
        print("⚠️ Playwright browser installation failed. Try running 'playwright install' manually.")
        return False
    
    return success1 and success2

def create_directories():
    """Create necessary directories"""
    print("\n📁 Creating directories...")
    
    directories = ["assets"]
    
    for directory in directories:
        try:
            os.makedirs(directory, exist_ok=True)
            print(f"✅ Created directory: {directory}")
        except Exception as e:
            print(f"❌ Failed to create directory {directory}: {e}")
            return False
    
    return True

def test_installation():
    """Test if the installation works"""
    print("\n🧪 Testing installation...")
    
    try:
        # Test imports
        import streamlit
        import requests
        import bs4
        import pandas
        print("✅ Core packages imported successfully!")
        
        # Test Playwright
        try:
            from playwright.sync_api import sync_playwright
            print("✅ Playwright imported successfully!")
        except Exception as e:
            print(f"⚠️ Playwright import failed: {e}")
            return False
        
        return True
        
    except ImportError as e:
        print(f"❌ Import test failed: {e}")
        return False

def show_next_steps():
    """Show user what to do next"""
    print("\n" + "="*50)
    print("🎉 Setup Complete!")
    print("="*50)
    
    print("\nTo run the application:")
    print("1. Open your terminal/command prompt")
    print("2. Navigate to this directory")
    print("3. Run: streamlit run app.py")
    print("4. The app will open in your browser at http://localhost:8501")
    
    print("\n📋 Usage Tips:")
    print("• Upload your resume in PDF or DOCX format")
    print("• Start with broader job titles like 'IT Support' or 'Helpdesk'")
    print("• Use 'Remote' for location if you want remote jobs")
    print("• Sample data is provided if scraping fails")
    print("• LinkedIn auto-apply requires your LinkedIn credentials")
    
    print("\n🔧 If you encounter issues:")
    print("• Check the troubleshooting section in the app")
    print("• Try running 'playwright install' again")
    print("• Make sure you have a stable internet connection")

def main():
    """Main setup function"""
    print("🚀 Auto Apply for Tech Jobs - Setup Script")
    print("="*50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Get system info
    print(f"💻 System: {platform.system()} {platform.release()}")
    print(f"🐍 Python: {sys.version}")
    
    # Create directories
    if not create_directories():
        print("❌ Failed to create directories!")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("❌ Failed to install dependencies!")
        sys.exit(1)
    
    # Install Playwright
    if not install_playwright():
        print("⚠️ Playwright installation had issues, but continuing...")
    
    # Test installation
    if not test_installation():
        print("⚠️ Installation test had issues, but setup is likely complete.")
    
    # Show next steps
    show_next_steps()

if __name__ == "__main__":
    main() 