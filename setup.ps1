Write-Host "🚀 Starting API Sync Orchestrator setup..." -ForegroundColor Cyan

# Detect OS (for cross-platform notes)
$IsWindows = $true

# Step 1: Rust (must come first for Pydantic v2 build)
if (!(Get-Command rustc -ErrorAction SilentlyContinue)) {
    Write-Host "🦀 Rust not found — installing via winget..." -ForegroundColor Yellow
    try {
        winget install -e --id Rustlang.Rustup --silent --accept-source-agreements --accept-package-agreements
        Write-Host "✅ Rust installed. Restarting PowerShell for PATH..." -ForegroundColor Green
        Write-Host "Please re-run this script after restart." -ForegroundColor Yellow
        exit 0  # Success, but prompt restart
    } catch {
        Write-Host "❌ Failed to install Rust via winget. Manual install: https://rustup.rs" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Rust already installed." -ForegroundColor Green
}

# Step 2: Ensure Python and Pip (after Rust)
if (!(Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Python not found. Install Python 3.12+ from https://python.org" -ForegroundColor Red
    exit 1
}

if (!(Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "❌ pip not found. Run 'python -m ensurepip' or reinstall Python." -ForegroundColor Red
    exit 1
}

# Step 3: Create and activate virtual environment
if (!(Test-Path ".venv")) {
    Write-Host "🧱 Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
& .\.venv\Scripts\Activate.ps1

# Step 4: Upgrade pip (after Rust/Python ready)
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Yellow
pip install --upgrade pip

# Step 5: Install requirements (pips only after Rust)
Write-Host "📦 Installing requirements..." -ForegroundColor Yellow
pip install -r requirements.txt

# Step 6: Test run (verify flow)
Write-Host "🧪 Running dry-run test..." -ForegroundColor Yellow
try {
    python sync.py --dry-run
    Write-Host "✅ Test successful! Ready to use." -ForegroundColor Green
} catch {
    Write-Host "⚠️ Test failed—check logs, but setup is complete." -ForegroundColor Yellow
}

Write-Host "✅ Setup complete! Run:" -ForegroundColor Green
Write-Host "python sync.py --dry-run" -ForegroundColor Cyan
Write-Host "python scheduler.py" -ForegroundColor Cyan