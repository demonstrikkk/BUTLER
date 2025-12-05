"""Quick diagnostic script to check API key setup."""
import os
from pathlib import Path
from dotenv import load_dotenv

print("🔍 Diagnosing API Key Setup\n")
print("=" * 60)

# Check if .env file exists
env_file = Path(".env")
if env_file.exists():
    print("✅ .env file found")
    print(f"   Location: {env_file.absolute()}")
else:
    print("❌ .env file NOT found!")
    print("   Please create .env file from .env.example")
    exit(1)

# Load environment variables
load_dotenv()

# Check API key
api_key = os.getenv("GEMINI_API_KEY", "")

print("\n" + "=" * 60)
print("API Key Check:")
print("=" * 60)

if not api_key:
    print("❌ GEMINI_API_KEY is empty or not set!")
    print("\nPlease check your .env file:")
    print("1. Open .env file")
    print("2. Make sure it has: GEMINI_API_KEY=your_actual_key")
    print("3. No quotes needed, no extra spaces")
    print("\nExample:")
    print("GEMINI_API_KEY=AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq")
    exit(1)

# Show API key info (partially masked)
if len(api_key) > 10:
    masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
else:
    masked_key = "*" * len(api_key)

print(f"✅ API Key found: {masked_key}")
print(f"   Length: {len(api_key)} characters")

# Check for common issues
issues = []

if api_key.strip() != api_key:
    issues.append("⚠️ API key has leading/trailing spaces")

if '"' in api_key or "'" in api_key:
    issues.append("⚠️ API key contains quotes (remove them)")

if not api_key.startswith('AIza'):
    issues.append("⚠️ API key doesn't start with 'AIza' (unusual for Gemini keys)")

if len(api_key) < 30:
    issues.append("⚠️ API key seems too short (Gemini keys are usually 39 chars)")

if issues:
    print("\n" + "=" * 60)
    print("⚠️ POTENTIAL ISSUES DETECTED:")
    print("=" * 60)
    for issue in issues:
        print(f"  {issue}")
    print("\nYour .env file should look like this:")
    print("GEMINI_API_KEY=AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq")
    print("(no quotes, no spaces)")
else:
    print("\n✅ API key format looks good!")

# Test the API key
print("\n" + "=" * 60)
print("Testing API Key with Gemini...")
print("=" * 60)

try:
    import google.generativeai as genai
    
    genai.configure(api_key=api_key.strip())
    
    # Try to list models (lightweight test)
    print("Attempting to connect to Gemini API...")
    
    # Try creating a simple model instance
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    # Try a simple generation
    response = model.generate_content("Say 'Hello' if you can read this.")
    
    print("✅ SUCCESS! API key is valid and working!")
    print(f"\n📝 Test response: {response.text}")
    print("\n🎉 Your setup is correct! You can now run: python run_agent.py")
    
except Exception as e:
    print(f"❌ API Key Test Failed!")
    print(f"\nError: {e}")
    print("\n" + "=" * 60)
    print("🔧 SOLUTIONS:")
    print("=" * 60)
    print("1. Get a NEW API key from: https://makersuite.google.com/app/apikey")
    print("2. Make sure you're using GEMINI API key (not other Google APIs)")
    print("3. Copy the entire key (usually starts with 'AIza')")
    print("4. Paste it in .env file: GEMINI_API_KEY=your_key")
    print("5. Save the file and run this script again")
    print("\n💡 Note: Using Gemini 1.5 Flash (free tier model)")
    print("   Model: gemini-2.0-flash")
