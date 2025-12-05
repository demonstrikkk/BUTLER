# 🎯 Using Your Chrome Profile - COMPLETE GUIDE

## ✅ What Changed

The automation now uses **YOUR existing Chrome profile** instead of opening a blank browser!

### Benefits:
- ✅ **Already logged in** to Swiggy/Zomato/Blinkit
- ✅ **Saved addresses** already there
- ✅ **Payment methods** saved
- ✅ **No need to enter location** manually
- ✅ **Browser opens visibly** so you can watch and verify

---

## 🚀 How to Use

### 1. Make sure `.env` is configured:

Your `.env` file should have:
```env
HEADLESS_MODE=false           # Show browser window
USE_CHROME_PROFILE=true       # Use your Chrome profile
CHROME_PROFILE_NAME=Default   # Your profile name
```

### 2. Run the agent:

**From Windows PowerShell (RECOMMENDED):**
```powershell
cd C:\Users\asus\Downloads\order_adk_agent
python run_agent.py
```

**From WSL (if Chrome installed in WSL):**
```bash
python3 run_agent.py
```

### 3. Order naturally:
```
You: Order chole kulche from King Kulcha on Swiggy
AI: *opens YOUR Chrome browser with your profile*
    *already logged in to Swiggy*
    *uses your saved location*
    *automates the ordering*
```

---

## 🔍 Finding Your Chrome Profile Name

If `Default` doesn't work, find your actual profile name:

### Method 1: Chrome Settings
1. Open Chrome
2. Type in address bar: `chrome://version/`
3. Look for **"Profile Path"**
4. Example: `C:\Users\asus\AppData\Local\Google\Chrome\User Data\Default`
   - Profile name is the **last part**: `Default`
5. Update `.env` with that name

### Method 2: Check Folders
1. Open File Explorer
2. Go to: `C:\Users\asus\AppData\Local\Google\Chrome\User Data`
3. You'll see folders like:
   - `Default` (main profile)
   - `Profile 1` (second profile)
   - `Profile 2` (third profile)
4. Use the name of the folder where you're logged in to Swiggy

### Method 3: Multiple Profiles
If you use multiple Chrome profiles:
- Click your profile icon in Chrome (top right)
- Note which profile you use for food ordering
- That determines the folder name:
  - First profile → `Default`
  - Second profile → `Profile 1`
  - Third profile → `Profile 2`

---

## 📂 File Locations by OS

### Windows:
```
C:\Users\<username>\AppData\Local\Google\Chrome\User Data
```

### WSL (accessing Windows Chrome):
```
/mnt/c/Users/<username>/AppData/Local/Google/Chrome/User Data
```

### Linux (native):
```
~/.config/google-chrome
```

### macOS:
```
~/Library/Application Support/Google/Chrome
```

---

## 🎬 What You'll See

When you order now:

```
🌐 Initializing browser for Swiggy automation...
   🔧 Setting up Chrome browser...
   👤 Using existing Chrome profile: C:\Users\asus\AppData\Local\Google\Chrome\User Data
   📂 Profile: Default
   ✅ You'll be logged in to all your accounts!
   🖥️ Running in GUI mode (required for profile)
   🔍 Installing/updating ChromeDriver...
   🚀 Launching Chrome browser...
   ✅ Browser initialized successfully!

[Browser window opens with YOUR profile - already logged in!]

🏪 Searching for restaurant...
✅ Found restaurant
🛒 Adding to cart...
✅ Proceeding to checkout...
🔒 Ready for payment - YOU complete this step!
```

---

## ⚙️ Configuration Options

### Option 1: Use Your Profile (Recommended)
```env
USE_CHROME_PROFILE=true
HEADLESS_MODE=false
CHROME_PROFILE_NAME=Default
```
**Best for:** Actual ordering, already logged in

### Option 2: Fresh Browser
```env
USE_CHROME_PROFILE=false
HEADLESS_MODE=false
```
**Best for:** Testing, no login info

### Option 3: Headless (Background)
```env
USE_CHROME_PROFILE=false
HEADLESS_MODE=true
```
**Best for:** Server/automation without GUI
**Note:** Can't use profile in headless mode!

---

## 🔧 Troubleshooting

### Issue: "Profile in use" error
**Solution:** Close all Chrome windows first, then run the script

### Issue: Wrong profile opens
**Solution:** Check `chrome://version/` and update `CHROME_PROFILE_NAME` in `.env`

### Issue: Not logged in to Swiggy
**Solution:** 
1. Make sure you're using the right profile
2. Open Chrome normally and verify you're logged in to Swiggy
3. Note the profile name from `chrome://version/`
4. Update `.env` with that profile name

### Issue: Multiple Chrome windows open
**Solution:** This is normal - automation opens in a new window using your profile data

---

## 🎯 Quick Test

1. **Update `.env`:**
   ```env
   HEADLESS_MODE=false
   USE_CHROME_PROFILE=true
   CHROME_PROFILE_NAME=Default
   ```

2. **Run the agent:**
   ```bash
   python3 run_agent.py
   ```

3. **Try ordering:**
   ```
   You: Order pizza from Dominos on Swiggy
   ```

4. **Watch the magic:**
   - Chrome opens with YOUR profile
   - Already logged in to Swiggy
   - Already has your location
   - Automates the entire order
   - Stops at payment for you!

---

## ✨ Summary

**Before:** 
- ❌ Blank browser
- ❌ Not logged in
- ❌ No saved location
- ❌ Hard to automate

**Now:**
- ✅ YOUR Chrome profile
- ✅ Already logged in
- ✅ Location pre-filled
- ✅ Smooth automation!

Just make sure:
1. `USE_CHROME_PROFILE=true` in `.env`
2. `HEADLESS_MODE=false` in `.env`
3. Correct `CHROME_PROFILE_NAME` in `.env`
4. Run from **Windows PowerShell** for best results

**Ready to order! 🎉**
