# -------------------------------------------------
# Setup script for API Sync Orchestrator (Windows)
# -------------------------------------------------
# 1. Check Rust (required for Pydantic v2 build)
# 2. Check Python 3.12+ and pip
# 3. Create/activate virtual environment
# 4. Upgrade pip and install dependencies
# 5. Copy .env.example to .env if missing
# 6. Run dry-run test
# -------------------------------------------------

# --------------------------
# Step 0: Define variables
# --------------------------
$VenvDir = ".venv312"  # 3.12 venv
$RequirementsFile = "requirements.txt"
$EnvExample = ".env.example"
$EnvFile = ".env"

# --------------------------
# Step 1: Check Rust (must come first for Pydantic v2 build)
# --------------------------
if (!(Get-Command rustc -ErrorAction SilentlyContinue)) {
    Write-Host "🦀 Rust not found — installing via winget..." -ForegroundColor Yellow
    try {
        winget install -e --id Rustlang.Rustup --silent --accept-source-agreements --accept-package-agreements
        Write-Host "✅ Rust installed. Restart PowerShell for PATH..." -ForegroundColor Green
        Write-Host "Please re-run this script after restart." -ForegroundColor Yellow
        exit 0
    } catch {
        Write-Host "❌ Failed to install Rust via winget. Manual install: https://rustup.rs" -ForegroundColor Red
        exit 1
    }
} else {
    Write-Host "✅ Rust already installed." -ForegroundColor Green
}

# --------------------------
# Step 2: Ensure Python 3.12+ and Pip
# --------------------------
$pythonVersion = python --version 2>$null
if (!$pythonVersion -or $pythonVersion -notlike "*3.12*") {
    Write-Host "❌ Python 3.12+ not found. Install from https://python.org/downloads/release/python-3127/" -ForegroundColor Red
    exit 1
}
Write-Host "✅ Python 3.12+ found." -ForegroundColor Green

if (!(Get-Command pip -ErrorAction SilentlyContinue)) {
    Write-Host "❌ pip not found. Run 'python -m ensurepip' or reinstall Python." -ForegroundColor Red
    exit 1
}
Write-Host "✅ pip found." -ForegroundColor Green

# --------------------------
# Step 3: Create and activate virtual environment
# --------------------------
if (!(Test-Path $VenvDir)) {
    Write-Host "🧱 Creating virtual environment (3.12)..." -ForegroundColor Yellow
    python -m venv $VenvDir
} else {
    Write-Host "Virtual environment already exists." -ForegroundColor Green
}

Write-Host "🔌 Activating virtual environment..." -ForegroundColor Yellow
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
} else {
    Write-Host "ERROR: Activation script not found!" -ForegroundColor Red
    exit 1
}

# --------------------------
# Step 4: Upgrade pip and install dependencies
# --------------------------
Write-Host "⬆️ Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

if (Test-Path $RequirementsFile) {
    Write-Host "📦 Installing dependencies from $RequirementsFile..." -ForegroundColor Yellow
    pip install -r $RequirementsFile
} else {
    Write-Host "WARNING: $RequirementsFile not found. Skipping dependency installation." -ForegroundColor Yellow
}

# --------------------------
# Step 5: Create .env from example if missing
# --------------------------
if (-Not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host ".env file created from .env.example. Remember to update your API keys!" -ForegroundColor Yellow
} else {
    Write-Host ".env file already exists." -ForegroundColor Green
}

# --------------------------
# Step 6: Dry-run test
# --------------------------
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
Write-Host "python main.py" -ForegroundColor Cyan