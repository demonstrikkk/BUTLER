# 🎯 USE YOUR EXISTING CHROME - SETUP GUIDE

## ✅ What This Does

The automation will now control **YOUR CURRENTLY OPEN Chrome browser** - the one you're using right now! No new windows, uses your logged-in session.

---

## 🚀 QUICK SETUP (3 Steps)

### Step 1: Close ALL Chrome Windows

First, **completely close Chrome**:
- Close all Chrome windows
- Check Task Manager - no Chrome processes should be running

### Step 2: Start Chrome with Remote Debugging

**Windows (PowerShell):**
```powershell
# Start Chrome with remote debugging enabled
& "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
```

**Or create a shortcut:**
1. Right-click on Desktop → New → Shortcut
2. Location: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222`
3. Name it: "Chrome (Debug Mode)"
4. Use this shortcut to open Chrome from now on

**Linux/WSL:**
```bash
google-chrome --remote-debugging-port=9222 &
```

**macOS:**
```bash
/Applications/Google\ Chrome.app/Contents/MacOS/Google\ Chrome --remote-debugging-port=9222 &
```

### Step 3: Run the Agent

After Chrome is running with debugging enabled:

```bash
python3 run_agent.py
```

That's it! The automation will connect to your open Chrome.

---

## 🎬 What Happens

**Before:**
```
❌ Opens new Chrome window (not logged in)
```

**Now:**
```
✅ Connects to YOUR open Chrome
✅ Uses your logged-in session
✅ Opens new tab in your existing window
✅ Automates the order in that tab
```

---

## 🖥️ Quick Start Script

Save this as `start_chrome_debug.bat` (Windows):

```batch
@echo off
echo Closing any existing Chrome instances...
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 /nobreak >nul

echo Starting Chrome with remote debugging...
start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222

echo.
echo ✅ Chrome started in debug mode!
echo 💡 Now you can run: python run_agent.py
echo.
pause
```

**Usage:**
1. Double-click `start_chrome_debug.bat`
2. Chrome opens (use it normally, login to Swiggy)
3. Run `python run_agent.py`
4. Order food - automation happens in your Chrome!

---

## 🔧 Alternative: Chrome Shortcut (Permanent)

Create a special Chrome shortcut you always use:

### Windows:
1. Find Chrome: `C:\Program Files\Google\Chrome\Application\chrome.exe`
2. Right-click → Create Shortcut
3. Right-click shortcut → Properties
4. In "Target", add at the end: ` --remote-debugging-port=9222`
5. Should look like: `"C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222`
6. Click OK
7. **Always use this shortcut to open Chrome**

### Linux:
Add to `~/.bashrc`:
```bash
alias chrome-debug='google-chrome --remote-debugging-port=9222 &'
```

Then: `chrome-debug` to start Chrome

### macOS:
Add to `~/.zshrc`:
```bash
alias chrome-debug='open -a "Google Chrome" --args --remote-debugging-port=9222'
```

---

## ✅ Verify It's Working

After starting Chrome with debugging:

1. Open Chrome as instructed above
2. Go to: `http://localhost:9222/json`
3. You should see JSON with Chrome tabs info
4. If you see this, remote debugging is working! ✅

---

## 🎯 Complete Workflow

### Daily Usage:

1. **Start Chrome (with debug mode):**
   ```powershell
   & "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
   ```

2. **Use Chrome normally:**
   - Browse, check emails, etc.
   - Make sure you're logged in to Swiggy/Zomato

3. **Run the agent:**
   ```bash
   python3 run_agent.py
   ```

4. **Order food:**
   ```
   You: Order chole kulche from King Kulcha on Swiggy
   ```

5. **Watch the magic:**
   - New tab opens in YOUR Chrome
   - Already logged in
   - Automates the order
   - Stops at payment

---

## 🔍 Troubleshooting

### "Could not connect to existing Chrome"

**Cause:** Chrome not running with remote debugging

**Solution:**
1. Close ALL Chrome windows
2. Start Chrome with: `chrome.exe --remote-debugging-port=9222`
3. Verify: Open `http://localhost:9222/json` in Chrome
4. Try running agent again

### Port Already in Use

**Cause:** Another app using port 9222

**Solution:** Use different port:
1. Update `.env`: `CHROME_DEBUGGER_PORT=9223`
2. Start Chrome: `chrome.exe --remote-debugging-port=9223`

### Chrome Opens But Can't Connect

**Cause:** Firewall or permissions

**Solution:**
- Run PowerShell as Administrator
- Add Chrome to Windows Firewall exceptions
- Try port 9222, 9223, or 9224

---

## 📊 Connection Modes

The script tries in this order:

1. **Connect to existing Chrome** (port 9222)
   - ✅ Best option - uses your open browser
   - ✅ Already logged in
   - ✅ All your sessions active

2. **Launch Chrome with profile** (fallback)
   - ⚠️ Opens new Chrome instance
   - ✅ Uses your profile data (logged in)
   - ⚠️ Separate from your main Chrome

3. **Fresh Chrome** (last resort)
   - ❌ Not logged in anywhere
   - ❌ No saved data

---

## 🎮 What You'll See

When connecting to existing Chrome:

```
🌐 Initializing browser for Swiggy automation...
   🔧 Setting up Chrome browser...
   🔗 Attempting to connect to existing Chrome on port 9222...
   🔍 Installing/updating ChromeDriver...
   🚀 Connecting to your existing Chrome browser...
   ✅ Connected to existing Chrome successfully!
   📱 Using your logged-in session!

[Opens new tab in YOUR Chrome window]
[Navigates to Swiggy]
[Already logged in!]
[Automates the order]
```

---

## 💡 Pro Tips

1. **Keep Chrome Debug Mode Always On:**
   - Use the shortcut method
   - Always start Chrome with `--remote-debugging-port=9222`
   - Agent can connect anytime

2. **Multiple Users:**
   - Each user needs their own port
   - User 1: Port 9222
   - User 2: Port 9223

3. **Security:**
   - Debug port only accepts local connections
   - Not exposed to internet
   - Safe to keep enabled

4. **Bookmarks:**
   - Keep Swiggy/Zomato tabs open
   - Agent will use existing tabs or open new ones

---

## ✨ Summary

**To use your existing Chrome:**

1. Start Chrome: `chrome.exe --remote-debugging-port=9222`
2. Login to Swiggy (if not already)
3. Run agent: `python3 run_agent.py`
4. Order food naturally
5. Automation happens in YOUR Chrome! 🎉

**Benefits:**
- ✅ No new windows
- ✅ Already logged in
- ✅ Uses your session
- ✅ Seamless experience

**One-time setup, permanent convenience!** 🚀
