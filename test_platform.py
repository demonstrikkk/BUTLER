#!/usr/bin/env python3
"""Test cross-platform Chrome detection and launching."""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.automation.base_automator import BaseAutomator
import platform


def test_environment_detection():
    """Test environment detection."""
    print("=" * 60)
    print("🧪 TESTING CROSS-PLATFORM DETECTION")
    print("=" * 60)
    
    automator = BaseAutomator()
    
    # Test OS detection
    print(f"\n🖥️  Operating System: {platform.system()}")
    
    # Test WSL detection
    is_wsl = automator._is_wsl()
    if is_wsl:
        print("🐧 Running in WSL (Windows Subsystem for Linux)")
    else:
        print(f"📍 Running in native {platform.system()} environment")
    
    # Test Chrome executable detection
    print("\n🔍 Searching for Chrome executable...")
    chrome_path = automator._get_chrome_executable_path()
    if chrome_path:
        print(f"✅ Found Chrome: {chrome_path}")
        exists = os.path.exists(chrome_path)
        print(f"   File exists: {exists}")
    else:
        print("❌ Chrome executable not found")
    
    # Test Chrome profile detection
    print("\n📂 Searching for Chrome profile...")
    profile_path = automator._get_chrome_profile_path()
    if profile_path:
        print(f"✅ Found Profile: {profile_path}")
        exists = os.path.exists(profile_path)
        print(f"   Directory exists: {exists}")
        
        if exists:
            # List profiles
            try:
                profiles = [d for d in os.listdir(profile_path) 
                           if os.path.isdir(os.path.join(profile_path, d)) 
                           and (d.startswith('Profile') or d == 'Default')]
                print(f"   Available profiles: {', '.join(profiles)}")
            except Exception as e:
                print(f"   Could not list profiles: {e}")
    else:
        print("❌ Chrome profile not found")
    
    print("\n" + "=" * 60)
    print("✅ DETECTION TEST COMPLETE")
    print("=" * 60)
    print("\n💡 Next step: Run launch_chrome_debug.py to start Chrome")
    print("   Then run: python3 run_agent.py")


if __name__ == "__main__":
    try:
        test_environment_detection()
    except Exception as e:
        print(f"\n❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
