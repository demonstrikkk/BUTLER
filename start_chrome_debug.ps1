# Start Chrome with Remote Debugging
Write-Host "`n========================================================" -ForegroundColor Cyan
Write-Host "  Starting Chrome with Remote Debugging" -ForegroundColor Cyan
Write-Host "========================================================`n" -ForegroundColor Cyan

Write-Host "[1/3] Closing any existing Chrome instances..." -ForegroundColor Yellow
Stop-Process -Name chrome -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2

Write-Host "[2/3] Starting Chrome with remote debugging enabled..." -ForegroundColor Yellow
Write-Host "       Port: 9222`n"

# Find Chrome installation
$chromePaths = @(
    "C:\Program Files\Google\Chrome\Application\chrome.exe",
    "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
    "$env:LOCALAPPDATA\Google\Chrome\Application\chrome.exe"
)

$chromePath = $null
foreach ($path in $chromePaths) {
    if (Test-Path $path) {
        $chromePath = $path
        break
    }
}

if ($chromePath) {
    Start-Process -FilePath $chromePath -ArgumentList "--remote-debugging-port=9222"
    
    Write-Host "[3/3] Waiting for Chrome to start..." -ForegroundColor Yellow
    Start-Sleep -Seconds 3
    
    Write-Host "`n========================================================" -ForegroundColor Green
    Write-Host "  Chrome Started Successfully!" -ForegroundColor Green
    Write-Host "========================================================`n" -ForegroundColor Green
    
    Write-Host "✅ Chrome is running in debug mode" -ForegroundColor Green
    Write-Host "🔌 Remote debugging port: 9222`n"
    
    Write-Host "📋 Next steps:" -ForegroundColor Yellow
    Write-Host "   1. Use Chrome normally (browse, login to Swiggy)"
    Write-Host "   2. Open a new terminal/PowerShell"
    Write-Host "   3. Run: " -NoNewline
    Write-Host "python run_agent.py" -ForegroundColor Cyan
    Write-Host "   4. Start ordering food!`n"
    
    Write-Host "💡 Tip: Verify debug mode is working:" -ForegroundColor Yellow
    Write-Host "   Open in Chrome: " -NoNewline
    Write-Host "http://localhost:9222/json" -ForegroundColor Blue
    
    Write-Host "`n========================================================`n" -ForegroundColor Cyan
    
} else {
    Write-Host "`n❌ ERROR: Chrome not found!" -ForegroundColor Red
    Write-Host "   Please install Chrome from: https://www.google.com/chrome/`n"
    Read-Host "Press Enter to exit"
    exit 1
}
