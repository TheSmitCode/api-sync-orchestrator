#!/bin/bash
# -------------------------------------------------
# Setup script for API Sync Orchestrator (Mac/Linux)
# -------------------------------------------------
# 1. Check Rust (required for Pydantic v2 build)
# 2. Check Python 3.12+ and pip
# 3. Create/activate virtual environment
# 4. Upgrade pip and install dependencies
# 5. Copy .env.example to .env if missing
# 6. Run dry-run test
# -------------------------------------------------

VENV_DIR=".venv312"
REQ_FILE="requirements.txt"
ENV_EXAMPLE=".env.example"
ENV_FILE=".env"

# --------------------------
# Step 1: Check Rust (must come first for Pydantic v2 build)
# --------------------------
if ! command -v rustc & > /dev/null; then
    echo "🦀 Rust not found — installing..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
    echo "✅ Rust installed. Restart terminal for PATH..."
    echo "Please re-run this script after restart."
    exit 0
else
    echo "✅ Rust already installed."
fi

# --------------------------
# Step 2: Ensure Python 3.12+ and Pip
# --------------------------
python_version=$(python3 --version 2>&1 | grep -oE 'Python [0-9]+\.[0-9]+\.[0-9]+')
if [[ ! "$python_version" =~ "Python 3.12" ]]; then
    echo "❌ Python 3.12+ not found. Install from python.org"
    exit 1
fi
echo "✅ Python 3.12+ found."

if ! command -v pip & > /dev/null; then
    echo "❌ pip not found. Run 'python3 -m ensurepip' or reinstall Python."
    exit 1
fi
echo "✅ pip found."

# --------------------------
# Step 3: Create and activate virtual environment
# --------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "🧱 Creating virtual environment (3.12)..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

# --------------------------
# Step 4: Activate virtual environment
# --------------------------
echo "🔌 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# --------------------------
# Step 5: Upgrade pip and install dependencies
# --------------------------
echo "⬆️ Upgrading pip..."
python -m pip install --upgrade pip

if [ -f "$REQ_FILE" ]; then
    echo "📦 Installing dependencies from $REQ_FILE..."
    pip install -r $REQ_FILE
else
    echo "WARNING: $REQ_FILE not found. Skipping dependency installation."
fi

# --------------------------
# Step 6: Create .env from example if missing
# --------------------------
if [ ! -f "$ENV_FILE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo ".env file created from .env.example. Remember to update your API keys!"
else
    echo ".env file already exists."
fi

# --------------------------
# Step 7: Dry-run test
# --------------------------
echo "🧪 Running dry-run test..."
python sync.py --dry-run

echo "✅ Setup complete! Run: python sync.py --dry-run"