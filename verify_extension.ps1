# BUTLER Extension - File Verification Script
# Run this to verify all required files are present

Write-Host "🔍 BUTLER Extension File Verification" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

$extensionPath = "$PSScriptRoot\browser-extension"
$allGood = $true

# Required files
$requiredFiles = @(
    "manifest.json",
    "background.js",
    "popup.html",
    "popup.js",
    "sidepanel.html",
    "sidepanel.js",
    "options.html",
    "options.js",
    "devtools.html",
    "devtools.js",
    "styles/popup.css",
    "styles/sidepanel.css",
    "styles/options.css",
    "services/gemini-service.js",
    "services/chrome-mcp.js",
    "services/automation-orchestrator.js",
    "content/swiggy-content.js",
    "content/zomato-content.js",
    "content/blinkit-content.js",
    "icons/icon16.svg",
    "icons/icon48.svg",
    "icons/icon128.svg"
)

Write-Host "Checking required files..." -ForegroundColor Yellow
Write-Host ""

foreach ($file in $requiredFiles) {
    $fullPath = Join-Path $extensionPath $file
    if (Test-Path $fullPath) {
        Write-Host "✅ $file" -ForegroundColor Green
    } else {
        Write-Host "❌ $file - MISSING!" -ForegroundColor Red
        $allGood = $false
    }
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan

if ($allGood) {
    Write-Host "✅ ALL FILES PRESENT!" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next steps:" -ForegroundColor Cyan
    Write-Host "1. Open Chrome and go to: chrome://extensions/" -ForegroundColor White
    Write-Host "2. Enable 'Developer mode' (top right)" -ForegroundColor White
    Write-Host "3. Click 'Load unpacked'" -ForegroundColor White
    Write-Host "4. Select folder: $extensionPath" -ForegroundColor White
    Write-Host ""
    Write-Host "📖 See INSTALLATION_GUIDE.md for complete setup instructions" -ForegroundColor Yellow
} else {
    Write-Host "❌ SOME FILES ARE MISSING!" -ForegroundColor Red
    Write-Host "Please check the errors above." -ForegroundColor Red
}

Write-Host ""
