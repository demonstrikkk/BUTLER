# 🚀 Quick Start Guide - BUTLER

## Problem: "API key not valid" Error? 

**The issue is that your `.env` file has a placeholder API key instead of a real one!**

Follow these steps to fix it:

---

## ✅ Solution (3 Simple Steps)

### Step 1: Get Your FREE API Key

1. Open this link: **https://aistudio.google.com/apikey**
2. Sign in with your Google account
3. Click the **"Create API Key"** button
4. Select **"Create API key in new project"**
5. **COPY the entire key** (it will look like: `AIzaSyAaBbCcDdEe...`)

### Step 2: Update Your .env File

1. Open the `.env` file in this folder
2. Find this line:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```
3. Replace `your_gemini_api_key_here` with your actual key:
   ```
   GEMINI_API_KEY=AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq
   ```
4. **IMPORTANT**: 
   - NO quotes around the key
   - NO extra spaces
   - Just paste the key directly after the `=`
5. **Save the file**

### Step 3: Test It!

Run one of these commands to verify your setup:

```powershell
python check_api_key.py
```

Or use the interactive setup wizard:

```powershell
python setup_api_key.py
```

If you see "✅ SUCCESS!" - you're all set! 🎉

---

## 🏃 Running the Agent

Once your API key is set up:

```powershell
python run_agent.py
```

---

## 🔧 Common Issues

### Issue 1: "API key not found"
- **Problem**: .env file doesn't exist or is empty
- **Solution**: Run `python setup_api_key.py`

### Issue 2: "Invalid API key" or "400 error"
- **Problem**: The API key is wrong or expired
- **Solution**: 
  1. Go to https://aistudio.google.com/apikey
  2. Create a BRAND NEW API key
  3. Replace the old one in .env file

### Issue 3: "Module not found" errors
- **Problem**: Dependencies not installed
- **Solution**: 
  ```powershell
  pip install -r requirements.txt
  ```

### Issue 4: API key still shows as "your_gemini_api_key_here"
- **Problem**: You didn't replace the placeholder
- **Solution**: 
  1. Open .env file in a text editor
  2. Actually paste your real API key
  3. Save the file

---

## 📝 Example .env File (CORRECT)

```env
GEMINI_API_KEY=AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq
HEADLESS_MODE=false
BROWSER_TIMEOUT=30
```

## ❌ Example .env File (WRONG)

```env
# ❌ WRONG - Still has placeholder
GEMINI_API_KEY=your_gemini_api_key_here

# ❌ WRONG - Has quotes
GEMINI_API_KEY="AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq"

# ❌ WRONG - Has extra spaces
GEMINI_API_KEY= AIzaSyAaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQq 
```

---

## 🆘 Still Having Issues?

1. **Delete your .env file**
2. **Run**: `python setup_api_key.py`
3. **Follow the wizard** - it will guide you step-by-step

---

## ✨ What Changed?

We fixed several issues in your project:

1. ✅ Changed model from `gemini-2.0-flash` to `gemini-2.0-flash` (correct free tier model)
2. ✅ Added better error messages when API key is invalid
3. ✅ Added validation to catch placeholder API keys
4. ✅ Created setup wizard (`setup_api_key.py`) for easy configuration
5. ✅ Updated all test files to use correct model name

---

**Need the API key link again?** 
👉 https://aistudio.google.com/apikey
