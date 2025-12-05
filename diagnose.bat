@echo off
echo.
echo ================================================
echo   BUTLER - Quick Diagnostic
echo ================================================
echo.

REM Check if Python is available
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found!
    echo Please install Python 3.10 or higher
    pause
    exit /b 1
)

echo [1/3] Checking Python installation...
python --version
echo.

echo [2/3] Checking if dependencies are installed...
python -c "import google.generativeai" >nul 2>&1
if errorlevel 1 (
    echo.
    echo WARNING: Dependencies not installed!
    echo Installing required packages...
    echo.
    pip install -r requirements.txt
    echo.
)

echo [3/3] Running API key diagnostic...
echo.
python check_api_key.py

echo.
echo ================================================
echo.
echo What to do next:
echo.
echo If you saw SUCCESS above:
echo   - Run: python run_agent.py
echo.
echo If you saw an error:
echo   1. Get API key from: https://aistudio.google.com/apikey
echo   2. Run: python setup_api_key.py
echo   3. Follow the wizard
echo.
echo ================================================
echo.
pause
