#!/usr/bin/env python3
"""Simple .env checker"""
import os
from pathlib import Path

print("\n" + "="*60)
print("CHECKING .ENV FILE")
print("="*60 + "\n")

# Step 1: Check if file exists
env_file = Path(".env")
print(f"1. Checking if .env exists...")
if env_file.exists():
    print(f"   ✅ Found at: {env_file.absolute()}")
else:
    print(f"   ❌ NOT FOUND at: {env_file.absolute()}")
    exit(1)

# Step 2: Read the file
print(f"\n2. Reading .env file...")
try:
    with open(env_file, 'r') as f:
        lines = f.readlines()
    print(f"   ✅ File has {len(lines)} lines")
except Exception as e:
    print(f"   ❌ Error reading file: {e}")
    exit(1)

# Step 3: Find GEMINI_API_KEY
print(f"\n3. Looking for GEMINI_API_KEY...")
found_key = None
for line in lines:
    line = line.strip()
    if line.startswith("GEMINI_API_KEY"):
        found_key = line
        break

if found_key:
    print(f"   ✅ Found line: {found_key[:30]}...")
    
    # Parse the key
    if "=" in found_key:
        key_value = found_key.split("=", 1)[1].strip()
        
        # Remove quotes if present
        if key_value.startswith('"') and key_value.endswith('"'):
            print(f"   ⚠️  Key has double quotes - removing them")
            key_value = key_value[1:-1]
        elif key_value.startswith("'") and key_value.endswith("'"):
            print(f"   ⚠️  Key has single quotes - removing them")
            key_value = key_value[1:-1]
        
        print(f"   Key length: {len(key_value)} chars")
        print(f"   Starts with AIza: {key_value.startswith('AIza')}")
else:
    print(f"   ❌ GEMINI_API_KEY not found in file!")
    print("   Add this line to .env:")
    print("   GEMINI_API_KEY=your_api_key_here")
    exit(1)

# Step 4: Load with python-dotenv
print(f"\n4. Loading with python-dotenv...")
try:
    from dotenv import load_dotenv
    load_dotenv(override=True)
    loaded_key = os.getenv("GEMINI_API_KEY", "")
    
    if loaded_key:
        print(f"   ✅ Loaded successfully")
        print(f"   Length: {len(loaded_key)} chars")
    else:
        print(f"   ❌ Failed to load (got empty string)")
except Exception as e:
    print(f"   ❌ Error: {e}")
    exit(1)

# Step 5: Test with Gemini
print(f"\n5. Testing with Google Gemini...")
try:
    import google.generativeai as genai
    genai.configure(api_key=loaded_key.strip())
    
    model = genai.GenerativeModel('gemini-2.0-flash')
    response = model.generate_content("Say 'OK'")
    
    print(f"   ✅✅✅ SUCCESS! ✅✅✅")
    print(f"   Response: {response.text}")
    print(f"\n🎉 Your setup is working!")
    
except Exception as e:
    error_msg = str(e)
    print(f"   ❌ FAILED: {error_msg}")
    
    if "400" in error_msg or "invalid" in error_msg.lower():
        print(f"\n❌ THE API KEY IS INVALID!")
        print(f"\n💡 SOLUTION:")
        print(f"   1. Go to: https://aistudio.google.com/apikey")
        print(f"   2. Click 'Create API Key'")
        print(f"   3. Copy the ENTIRE key (starts with AIza)")
        print(f"   4. Open .env file")
        print(f"   5. Replace the key on this line:")
        print(f"      GEMINI_API_KEY=your_new_key_here")
        print(f"   6. Save and run again")

print("\n" + "="*60 + "\n")
