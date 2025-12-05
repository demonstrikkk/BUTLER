"""Debug script to check .env loading."""
import os
import sys
from pathlib import Path

print("=" * 70)
print("🔍 DEBUGGING .env FILE LOADING")
print("=" * 70)

# Check current directory
print(f"\n📁 Current Directory: {os.getcwd()}")
print(f"📁 Script Location: {Path(__file__).parent.absolute()}")

# Check if .env exists
env_path = Path(".env")
print(f"\n🔍 Looking for .env at: {env_path.absolute()}")

if env_path.exists():
    print(f"✅ .env file EXISTS")
    print(f"   Size: {env_path.stat().st_size} bytes")
    
    # Try to read it
    try:
        with open(env_path, 'r') as f:
            content = f.read()
        
        print(f"   Lines: {len(content.splitlines())}")
        
        # Show the file content (masked)
        print("\n📄 .env File Content (API key masked):")
        print("-" * 70)
        for i, line in enumerate(content.splitlines(), 1):
            if line.strip() and not line.startswith('#'):
                if 'GEMINI_API_KEY' in line:
                    parts = line.split('=', 1)
                    if len(parts) == 2:
                        key = parts[1].strip()
                        masked = key[:6] + '*' * (len(key) - 10) + key[-4:] if len(key) > 10 else '*' * len(key)
                        print(f"Line {i}: GEMINI_API_KEY={masked}")
                        print(f"         Key length: {len(key)} chars")
                        print(f"         Starts with 'AIza': {key.startswith('AIza')}")
                        has_quotes = ('"' in key) or ("'" in key)
                        print(f"         Has quotes: {has_quotes}")
                        print(f"         Has spaces: {' ' in key}")
                    else:
                        print(f"Line {i}: {line}")
                else:
                    print(f"Line {i}: {line}")
        print("-" * 70)
        
    except Exception as e:
        print(f"❌ Error reading .env: {e}")
else:
    print(f"❌ .env file NOT FOUND!")

# Now test loading with python-dotenv
print("\n" + "=" * 70)
print("🔧 TESTING python-dotenv Loading")
print("=" * 70)

try:
    from dotenv import load_dotenv
    
    # Load .env
    result = load_dotenv(override=True, verbose=True)
    print(f"load_dotenv() returned: {result}")
    
    # Get the API key
    api_key = os.getenv("GEMINI_API_KEY", "")
    
    print(f"\n📊 After load_dotenv():")
    print(f"   GEMINI_API_KEY environment variable:")
    
    if api_key:
        masked = api_key[:6] + '*' * (len(api_key) - 10) + api_key[-4:] if len(api_key) > 10 else '*' * len(api_key)
        print(f"   ✅ Found: {masked}")
        print(f"   Length: {len(api_key)} chars")
        print(f"   Starts with 'AIza': {api_key.startswith('AIza')}")
        
        # Check for issues
        if api_key != api_key.strip():
            print("   ⚠️  HAS LEADING/TRAILING WHITESPACE!")
            api_key = api_key.strip()
            print(f"   After strip: {api_key[:6]}...{api_key[-4:]}")
        
        has_quotes_check = ('"' in api_key) or ("'" in api_key)
        if has_quotes_check:
            print("   ⚠️  HAS QUOTES!")
        
    else:
        print(f"   ❌ NOT FOUND (empty string)")
        print("\n🔍 All environment variables with 'GEMINI':")
        for key, value in os.environ.items():
            if 'GEMINI' in key.upper():
                print(f"   {key} = {value[:20]}..." if len(value) > 20 else f"   {key} = {value}")
    
except ImportError:
    print("❌ python-dotenv not installed!")
    print("   Run: pip install python-dotenv")
except Exception as e:
    print(f"❌ Error: {e}")

# Final test with Google Gemini
if api_key:
    print("\n" + "=" * 70)
    print("🧪 TESTING WITH GOOGLE GEMINI")
    print("=" * 70)
    
    try:
        import google.generativeai as genai
        
        # Configure with the loaded API key
        genai.configure(api_key=api_key.strip())
        
        print("✅ Configured Gemini API")
        
        # Try to create a model
        model = genai.GenerativeModel('gemini-2.0-flash')
        print("✅ Created model instance")
        
        # Try a simple generation
        print("📤 Sending test message...")
        response = model.generate_content("Reply with just the word 'SUCCESS'")
        
        print(f"✅ ✅ ✅ IT WORKS! ✅ ✅ ✅")
        print(f"\n📨 Response: {response.text}")
        print("\n🎉 Your API key is valid and working!")
        
    except Exception as e:
        print(f"❌ Gemini API Test Failed!")
        print(f"   Error: {e}")
        print("\n💡 This means:")
        print("   - The API key is being loaded")
        print("   - But it's invalid/expired")
        print("\n🔧 Solution:")
        print("   1. Go to https://aistudio.google.com/apikey")
        print("   2. Create a BRAND NEW API key")
        print("   3. Copy the ENTIRE key")
        print("   4. Replace in .env file")

print("\n" + "=" * 70)
