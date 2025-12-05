@echo off
echo.
echo ========================================================
echo   Starting Chrome with Remote Debugging
echo ========================================================
echo.

echo [1/3] Closing any existing Chrome instances...
taskkill /F /IM chrome.exe 2>nul
timeout /t 2 /nobreak >nul

echo [2/3] Starting Chrome with remote debugging enabled...
echo        Port: 9222
echo.

REM Try different Chrome installation paths
if exist "C:\Program Files\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
    goto :started
)

if exist "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" (
    start "" "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe" --remote-debugging-port=9222
    goto :started
)

echo ERROR: Chrome not found in standard locations!
echo Please install Chrome or update the path in this script.
pause
exit /b 1

:started
echo [3/3] Waiting for Chrome to start...
timeout /t 3 /nobreak >nul

echo.
echo ========================================================
echo   Chrome Started Successfully!
echo ========================================================
echo.
echo ✅ Chrome is running in debug mode
echo 🔌 Remote debugging port: 9222
echo.
echo 📋 Next steps:
echo    1. Use Chrome normally (browse, login to Swiggy)
echo    2. Open a new terminal/PowerShell
echo    3. Run: python run_agent.py
echo    4. Start ordering food!
echo.
echo 💡 Tip: Verify debug mode is working:
echo    Open in Chrome: http://localhost:9222/json
echo.
echo ========================================================
echo.
echo Press any key to exit (Chrome will keep running)
pause >nul
