#!/usr/bin/env python3
"""
Cross-platform Chrome launcher with remote debugging support.

This script launches Chrome with remote debugging enabled, working on:
- Windows (native)
- Linux (native)
- macOS
- WSL (Windows Subsystem for Linux)

Usage:
    python3 launch_chrome_debug.py [port]
    
Example:
    python3 launch_chrome_debug.py 9222
"""

import os
import sys
import time
import platform
import subprocess
import shutil
from pathlib import Path


def is_wsl() -> bool:
    """Detect if running in WSL."""
    try:
        with open('/proc/version', 'r') as f:
            content = f.read().lower()
            return 'microsoft' in content or 'wsl' in content
    except:
        return False


def get_chrome_executable() -> str:
    """Get Chrome executable path based on OS."""
    system = platform.system()
    
    if system == "Windows":
        # Windows paths
        possible_paths = [
            r"C:\Program Files\Google\Chrome\Application\chrome.exe",
            r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
        ]
        for path in possible_paths:
            if os.path.exists(path):
                return path
    
    elif system == "Linux":
        if is_wsl():
            # WSL - use Windows Chrome
            possible_paths = [
                "/mnt/c/Program Files/Google/Chrome/Application/chrome.exe",
                "/mnt/c/Program Files (x86)/Google/Chrome/Application/chrome.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
        else:
            # Native Linux
            chrome_commands = ['google-chrome', 'google-chrome-stable', 'chromium', 'chromium-browser']
            for cmd in chrome_commands:
                chrome_path = shutil.which(cmd)
                if chrome_path:
                    return chrome_path
    
    elif system == "Darwin":
        # macOS
        mac_path = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
        if os.path.exists(mac_path):
            return mac_path
    
    return None


def get_chrome_profile_path() -> str:
    """Get Chrome user data directory path."""
    system = platform.system()
    
    if system == "Windows":
        username = os.environ.get('USERNAME', os.environ.get('USER', 'user'))
        return f"C:\\Users\\{username}\\AppData\\Local\\Google\\Chrome\\User Data"
    
    elif system == "Linux":
        if is_wsl():
            # WSL - get Windows profile
            if os.path.exists("/mnt/c/Users"):
                try:
                    users = os.listdir("/mnt/c/Users")
                    for username in users:
                        if username not in ['Public', 'Default', 'Default User']:
                            profile_path = f"/mnt/c/Users/{username}/AppData/Local/Google/Chrome/User Data"
                            if os.path.exists(profile_path):
                                return profile_path
                except:
                    pass
        
        # Native Linux
        home = os.path.expanduser("~")
        return f"{home}/.config/google-chrome"
    
    elif system == "Darwin":
        # macOS
        home = os.path.expanduser("~")
        return f"{home}/Library/Application Support/Google/Chrome"
    
    return None


def kill_existing_chrome():
    """Kill any existing Chrome processes."""
    system = platform.system()
    
    print("🛑 Closing existing Chrome instances...")
    try:
        if system == "Windows":
            subprocess.run(["taskkill", "/F", "/IM", "chrome.exe"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Linux":
            if is_wsl():
                # Kill Windows Chrome from WSL
                subprocess.run(["taskkill.exe", "/F", "/IM", "chrome.exe"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            else:
                subprocess.run(["pkill", "-f", "chrome"], 
                             stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        elif system == "Darwin":
            subprocess.run(["pkill", "-f", "Google Chrome"], 
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        time.sleep(2)  # Wait for processes to close
        print("✅ Chrome processes closed")
    except Exception as e:
        print(f"⚠️  Could not close Chrome: {e}")


def launch_chrome_debug(port: int = 9222, profile: str = "Default"):
    """Launch Chrome with remote debugging enabled."""
    
    # Detect environment
    system = platform.system()
    in_wsl = is_wsl()
    
    print("=" * 60)
    print("🚀 CHROME DEBUG LAUNCHER")
    print("=" * 60)
    print(f"🖥️  System: {system}")
    if in_wsl:
        print("🐧 Running in WSL (Windows Subsystem for Linux)")
    print(f"🔌 Debug Port: {port}")
    print(f"👤 Profile: {profile}")
    print("=" * 60)
    print()
    
    # Get Chrome executable
    chrome_path = get_chrome_executable()
    if not chrome_path:
        print("❌ ERROR: Chrome executable not found!")
        print()
        print("📥 Install Chrome:")
        if system == "Windows" or in_wsl:
            print("   → https://www.google.com/chrome/")
        elif system == "Linux":
            print("   → sudo apt-get install google-chrome-stable")
        elif system == "Darwin":
            print("   → brew install --cask google-chrome")
        sys.exit(1)
    
    print(f"✅ Found Chrome: {chrome_path}")
    
    # Get profile path
    user_data_dir = get_chrome_profile_path()
    if user_data_dir and os.path.exists(user_data_dir):
        print(f"✅ Found Profile: {user_data_dir}")
    else:
        print(f"⚠️  Profile not found, using fresh profile")
        user_data_dir = None
    
    print()
    
    # Kill existing Chrome
    kill_existing_chrome()
    
    # Build command
    cmd = [
        chrome_path,
        f"--remote-debugging-port={port}",
        "--no-first-run",
        "--no-default-browser-check",
    ]
    
    if user_data_dir:
        cmd.append(f"--user-data-dir={user_data_dir}")
        cmd.append(f"--profile-directory={profile}")
    
    print("🚀 Launching Chrome with remote debugging...")
    print(f"📝 Command: {' '.join(cmd[:3])}...")
    print()
    
    try:
        # Launch Chrome
        if system == "Windows" or (system == "Linux" and in_wsl):
            if system == "Windows":
                subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_PROCESS_GROUP)
            else:
                # WSL
                subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            # Linux/macOS
            subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, 
                           start_new_session=True)
        
        print("✅ Chrome launched successfully!")
        print()
        print("=" * 60)
        print("📋 NEXT STEPS:")
        print("=" * 60)
        print(f"1. Chrome is now running with debugging on port {port}")
        print("2. Login to Swiggy/Zomato/Blinkit in this Chrome window")
        print("3. Run your automation script:")
        print("   python3 run_agent.py")
        print()
        print(f"🔗 Debug endpoint: http://localhost:{port}")
        print(f"🔍 Check debug connection: http://localhost:{port}/json")
        print("=" * 60)
        
    except Exception as e:
        print(f"❌ Failed to launch Chrome: {e}")
        sys.exit(1)


if __name__ == "__main__":
    # Get port from command line argument
    port = 9222
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            print(f"❌ Invalid port: {sys.argv[1]}")
            print("Usage: python3 launch_chrome_debug.py [port]")
            sys.exit(1)
    
    # Get profile name from environment or use default
    profile = os.environ.get("CHROME_PROFILE_NAME", "Default")
    
    launch_chrome_debug(port, profile)
