"""Simple API key test."""
import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY", "")

print("API Key Check:")
print("-" * 50)

if not api_key:
    print("❌ NO API KEY FOUND!")
    print("\nYour .env file should contain:")
    print("GEMINI_API_KEY=your_actual_key_here")
else:
    # Mask the key for security
    masked = api_key[:6] + "*" * (len(api_key) - 10) + api_key[-4:]
    print(f"✅ Key found: {masked}")
    print(f"   Length: {len(api_key)} chars")
    
    # Check format
    if api_key.startswith("AIza"):
        print("✅ Format looks correct (starts with AIza)")
    else:
        print("⚠️  Unusual format (should start with AIza)")
    
    # Test with Gemini
    print("\nTesting connection...")
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key.strip())
        
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("Say hello")
        
        print("✅ SUCCESS! API key works!")
        print(f"Response: {response.text}")
    except Exception as e:
        print(f"❌ FAILED: {e}")
        print("\nGet a new key from:")
        print("https://aistudio.google.com/apikey")
