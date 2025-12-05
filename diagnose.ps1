# BUTLER Quick Diagnostic Script
# Run this to check your setup

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "  BUTLER - Quick Diagnostic" -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Check Python
Write-Host "[1/3] Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python not found!" -ForegroundColor Red
    Write-Host "Please install Python 3.10 or higher" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "`n[2/3] Checking dependencies..." -ForegroundColor Yellow
$depCheck = python -c "import google.generativeai" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "`nWARNING: Dependencies not installed!" -ForegroundColor Yellow
    Write-Host "Installing required packages...`n" -ForegroundColor Yellow
    pip install -r requirements.txt
    Write-Host ""
} else {
    Write-Host "Dependencies OK" -ForegroundColor Green
}

Write-Host "`n[3/3] Running API key diagnostic...`n" -ForegroundColor Yellow
python check_api_key.py

Write-Host "`n================================================" -ForegroundColor Cyan
Write-Host "`nWhat to do next:" -ForegroundColor Yellow
Write-Host "`nIf you saw SUCCESS above:" -ForegroundColor Green
Write-Host "  - Run: " -NoNewline
Write-Host "python run_agent.py" -ForegroundColor Cyan

Write-Host "`nIf you saw an error:" -ForegroundColor Red
Write-Host "  1. Get API key from: " -NoNewline
Write-Host "https://aistudio.google.com/apikey" -ForegroundColor Blue
Write-Host "  2. Run: " -NoNewline
Write-Host "python setup_api_key.py" -ForegroundColor Cyan
Write-Host "  3. Follow the wizard"

Write-Host "`n================================================`n" -ForegroundColor Cyan

Read-Host "Press Enter to exit"
