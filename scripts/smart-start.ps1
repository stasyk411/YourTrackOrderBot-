# scripts/smart-start.ps1
# AI runs this script at the start of each chat for automatic setup

Write-Host ""
Write-Host "🚀 SMART-START: AUTOMATIC PROJECT SETUP" -ForegroundColor Cyan
Write-Host "=" * 60
Write-Host ""

# ========================
# 1. PROJECT STANDARD CHECK
# ========================
Write-Host "🔍 1. Checking project standard..." -ForegroundColor Yellow

if (Test-Path "docs/PROJECT_GUIDE.md") {
    Write-Host "   ✅ Found: docs/PROJECT_GUIDE.md" -ForegroundColor Green
    
    # Show first 3 lines of the guide
    $guideLines = Get-Content "docs/PROJECT_GUIDE.md" -TotalCount 3 -Encoding UTF8
    Write-Host "   📋 Standard exists" -ForegroundColor Cyan
} else {
    Write-Host "   ⚠️  WARNING: docs/PROJECT_GUIDE.md not found!" -ForegroundColor Red
    Write-Host "      Project works WITHOUT standard!" -ForegroundColor Yellow
}

Write-Host ""

# ========================
# 2. VIRTUAL ENVIRONMENT CHECK
# ========================
Write-Host "🔍 2. Checking virtual environment..." -ForegroundColor Yellow

if (Test-Path ".venv") {
    Write-Host "   ✅ .venv found in project" -ForegroundColor Green
    
    # Check if .venv is active
    $isVenvActive = $false
    
    # Method 1: Check environment variable
    if ($env:VIRTUAL_ENV) {
        $isVenvActive = $true
    }
    
    # Method 2: Check Python path
    $pythonPath = (Get-Command python -ErrorAction SilentlyContinue).Source
    if ($pythonPath -and $pythonPath -match "\.venv") {
        $isVenvActive = $true
    }
    
    if ($isVenvActive) {
        Write-Host "   ✅ .venv is ACTIVE" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  .venv is NOT active!" -ForegroundColor Yellow
        Write-Host "      Activation command:" -ForegroundColor Gray
        Write-Host "      .venv\Scripts\activate" -ForegroundColor White
        Write-Host "      After activation you should see: (.venv) PS ...>" -ForegroundColor Gray
    }
} else {
    Write-Host "   ❌ CRITICAL ERROR: .venv not found!" -ForegroundColor Red
    Write-Host "      Project will use SYSTEM Python" -ForegroundColor Yellow
    Write-Host "      This violates basic development rules!" -ForegroundColor Yellow
    Write-Host "      Create .venv: python -m venv .venv" -ForegroundColor Gray
}

Write-Host ""

# ========================
# 3. ENCODING SETUP
# ========================
Write-Host "🔍 3. Setting up encoding..." -ForegroundColor Yellow

try {
    [System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8
    Write-Host "   ✅ Encoding set to: UTF-8" -ForegroundColor Green
} catch {
    Write-Host "   ⚠️  Failed to set UTF-8 encoding" -ForegroundColor Yellow
}

Write-Host ""

# ========================
# 4. BASIC PROJECT CHECK
# ========================
Write-Host "🔍 4. Basic project check..." -ForegroundColor Yellow

# Check important files
$importantFiles = @("requirements.txt", ".gitignore", "README.md")
foreach ($file in $importantFiles) {
    if (Test-Path $file) {
        Write-Host "   ✅ $file found" -ForegroundColor Green
    } else {
        Write-Host "   ⚠️  $file missing" -ForegroundColor Gray
    }
}

Write-Host ""

# ========================
# 5. INSTRUCTIONS FOR DEVELOPER
# ========================
Write-Host "🎯 5. INSTRUCTIONS FOR DEVELOPER:" -ForegroundColor Magenta
Write-Host "   • Check if you see (.venv) at start of line" -ForegroundColor Gray
Write-Host "   • If not, run: .venv\Scripts\activate" -ForegroundColor Gray
Write-Host "   • If text is garbled, run:" -ForegroundColor Gray
Write-Host "     [System.Console]::OutputEncoding = [System.Text.Encoding]::UTF8" -ForegroundColor Gray

Write-Host ""

# ========================
# 6. INSTRUCTIONS FOR AI
# ========================
Write-Host "🤖 6. INSTRUCTIONS FOR AI:" -ForegroundColor Blue
Write-Host "   • Follow docs/PROJECT_GUIDE.md if exists" -ForegroundColor Gray
Write-Host "   • Give commands with explanation" -ForegroundColor Gray
Write-Host "   • Wait for execution before next step" -ForegroundColor Gray
Write-Host "   • One command = one action" -ForegroundColor Gray
Write-Host "   • Check imports before making changes" -ForegroundColor Gray

Write-Host ""
Write-Host "=" * 60
Write-Host "✅ SMART-START COMPLETED" -ForegroundColor Green
Write-Host "📋 Project checked, ready to work" -ForegroundColor Cyan
Write-Host ""

# Return success status
exit 0