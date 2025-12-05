"""Check if browser automation is ready."""
import sys
import os
import subprocess
from pathlib import Path

print("\n" + "="*60)
print("🔍 BROWSER AUTOMATION DIAGNOSTIC")
print("="*60 + "\n")

# Check 1: Python version
print("1. Python Version:")
print(f"   {sys.version}")
print(f"   ✅ Python {sys.version_info.major}.{sys.version_info.minor}\n")

# Check 2: Required packages
print("2. Checking required packages...")
required = ['selenium', 'webdriver_manager']
missing = []

for package in required:
    try:
        __import__(package)
        print(f"   ✅ {package} installed")
    except ImportError:
        print(f"   ❌ {package} NOT installed")
        missing.append(package)

if missing:
    print(f"\n   Install missing packages:")
    print(f"   pip install {' '.join(missing)}\n")
else:
    print()

# Check 3: Chrome installation
print("3. Checking Chrome installation...")

chrome_paths = [
    # Linux/WSL
    "/usr/bin/google-chrome",
    "/usr/bin/google-chrome-stable",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    # Windows
    "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
    "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe",
    # macOS
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
]

chrome_found = False
for path in chrome_paths:
    if os.path.exists(path):
        print(f"   ✅ Chrome found: {path}")
        chrome_found = True
        
        # Try to get version
        try:
            if path.endswith('.exe'):
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=2)
            else:
                result = subprocess.run([path, '--version'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                print(f"   📌 Version: {result.stdout.strip()}")
        except:
            pass
        break

if not chrome_found:
    print("   ❌ Chrome NOT found in common locations")
    print("\n   💡 Install Chrome:")
    
    # Detect OS
    if sys.platform.startswith('linux'):
        print("   Linux/WSL: sudo apt-get update && sudo apt-get install google-chrome-stable")
    elif sys.platform == 'darwin':
        print("   macOS: brew install --cask google-chrome")
    elif sys.platform == 'win32':
        print("   Windows: Download from https://www.google.com/chrome/")
    print()

# Check 4: Test ChromeDriver
print("4. Testing ChromeDriver setup...")

if not missing:
    try:
        from selenium import webdriver
        from selenium.webdriver.chrome.service import Service
        from selenium.webdriver.chrome.options import Options
        from webdriver_manager.chrome import ChromeDriverManager
        
        print("   🔧 Attempting to initialize ChromeDriver...")
        
        chrome_options = Options()
        chrome_options.add_argument("--headless=new")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        
        print("   ✅ ChromeDriver initialized successfully!")
        
        driver.quit()
        print("   ✅ Browser automation is READY! 🎉\n")
        
    except Exception as e:
        print(f"   ❌ ChromeDriver test failed!")
        print(f"   Error: {str(e)}\n")
        
        error_str = str(e).lower()
        
        if "chrome" in error_str and "not found" in error_str:
            print("   💡 Solution: Install Chrome browser first")
            if sys.platform.startswith('linux'):
                print("      sudo apt-get install google-chrome-stable")
        
        elif "driver" in error_str or "executable" in error_str:
            print("   💡 Solution: ChromeDriver issue")
            print("      Try: pip install --upgrade webdriver-manager")
        
        print()
else:
    print("   ⏭️  Skipped (missing required packages)\n")

# Check 5: Display/X11 for GUI (Linux/WSL)
if sys.platform.startswith('linux'):
    print("5. Checking display server (for non-headless mode)...")
    display = os.environ.get('DISPLAY')
    
    if display:
        print(f"   ✅ DISPLAY set to: {display}")
    else:
        print("   ⚠️  No DISPLAY set (GUI mode won't work)")
        print("   💡 For WSL: Install X server (VcXsrv/Xming) or use headless mode")
        print("      Set HEADLESS_MODE=true in .env file")
    print()

# Summary
print("="*60)
print("📊 SUMMARY")
print("="*60)

if chrome_found and not missing:
    print("✅ Everything looks good! Browser automation should work.")
    print("\n💡 If automation still fails:")
    print("   - Run in headless mode: Set HEADLESS_MODE=true in .env")
    print("   - Run on Windows (not WSL) for GUI mode")
    print("   - Check Chrome version matches ChromeDriver")
else:
    print("❌ Issues detected. Fix the problems above.")
    
    if not chrome_found:
        print("\n🔧 Critical: Install Google Chrome first!")
    
    if missing:
        print(f"\n🔧 Critical: Install missing packages:")
        print(f"   pip install {' '.join(missing)}")

print("\n" + "="*60 + "\n")
