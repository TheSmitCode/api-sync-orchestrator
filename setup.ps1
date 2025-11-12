<#
.SYNOPSIS
    Setup script for API Sync Orchestrator (Windows).

.DESCRIPTION
    - Creates a Python virtual environment.
    - Installs dependencies from requirements.txt.
    - Copies .env.example to .env if it doesn't exist.
    - Runs a dry-run to verify setup.

.NOTES
    - Requires Python 3.8+
    - Ensure PowerShell execution policy allows scripts: Set-ExecutionPolicy RemoteSigned
#>

# --------------------------
# Step 0: Define variables
# --------------------------
$VenvDir = ".venv"
$RequirementsFile = "requirements.txt"
$EnvExample = ".env.example"
$EnvFile = ".env"

# --------------------------
# Step 1: Create virtual environment
# --------------------------
if (-Not (Test-Path $VenvDir)) {
    Write-Host "Creating virtual environment..."
    python -m venv $VenvDir
} else {
    Write-Host "Virtual environment already exists."
}

# --------------------------
# Step 2: Activate virtual environment
# --------------------------
Write-Host "Activating virtual environment..."
$ActivateScript = Join-Path $VenvDir "Scripts\Activate.ps1"
if (Test-Path $ActivateScript) {
    & $ActivateScript
} else {
    Write-Host "ERROR: Activation script not found!"
    exit 1
}

# --------------------------
# Step 3: Upgrade pip and install dependencies
# --------------------------
Write-Host "Upgrading pip..."
python -m pip install --upgrade pip

if (Test-Path $RequirementsFile) {
    Write-Host "Installing dependencies from $RequirementsFile..."
    pip install -r $RequirementsFile
} else {
    Write-Host "WARNING: $RequirementsFile not found. Skipping dependency installation."
}

# --------------------------
# Step 4: Create .env from example if missing
# --------------------------
if (-Not (Test-Path $EnvFile)) {
    Copy-Item $EnvExample $EnvFile
    Write-Host ".env file created from .env.example. Remember to update your API keys!"
} else {
    Write-Host ".env file already exists."
}

# --------------------------
# Step 5: Dry-run test
# --------------------------
Write-Host "Running dry-run test..."
python sync.py --dry-run

Write-Host "✅ Setup complete. You can now run sync.py or main.py."
