#!/bin/bash
echo "🚀 Starting API Sync Orchestrator setup..."

# Step 1: Rust (must come first for Pydantic v2 build)
if ! command -v rustc & > /dev/null; then
    echo "🦀 Rust not found — installing..."
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
    source $HOME/.cargo/env
    echo "✅ Rust installed. Restarting terminal for PATH..."
    echo "Please re-run this script after restart."
    exit 0
else
    echo "✅ Rust already installed."
fi

# Step 2: Ensure Python and Pip (after Rust)
if ! command -v python3 & > /dev/null; then
    echo "❌ Python not found. Install Python 3.12+ from python.org"
    exit 1
fi

# Step 3: Venv
if [ ! -d ".venv" ]; then
    echo "🧱 Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate
source .venv/bin/activate

# Step 4: Upgrade pip (after Rust/Python ready)
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Step 5: Install requirements (pips only after Rust)
echo "📦 Installing requirements..."
pip install -r requirements.txt

# Step 6: Test run
echo "🧪 Running dry-run test..."
python sync.py --dry-run

echo "✅ Setup complete! Run: python sync.py --dry-run"