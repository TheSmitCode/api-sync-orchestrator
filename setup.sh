#!/bin/bash
# -------------------------------------------------
# Setup script for API Sync Orchestrator (Mac/Linux)
# -------------------------------------------------
# 1. Create virtual environment
# 2. Install dependencies
# 3. Copy .env.example to .env if missing
# 4. Run dry-run
# -------------------------------------------------

VENV_DIR=".venv"
REQ_FILE="requirements.txt"
ENV_EXAMPLE=".env.example"
ENV_FILE=".env"

# --------------------------
# Step 1: Create virtual environment
# --------------------------
if [ ! -d "$VENV_DIR" ]; then
    echo "Creating virtual environment..."
    python3 -m venv $VENV_DIR
else
    echo "Virtual environment already exists."
fi

# --------------------------
# Step 2: Activate virtual environment
# --------------------------
echo "Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# --------------------------
# Step 3: Upgrade pip and install dependencies
# --------------------------
echo "Upgrading pip..."
python -m pip install --upgrade pip

if [ -f "$REQ_FILE" ]; then
    echo "Installing dependencies from $REQ_FILE..."
    pip install -r $REQ_FILE
else
    echo "WARNING: $REQ_FILE not found. Skipping dependency installation."
fi

# --------------------------
# Step 4: Create .env from example if missing
# --------------------------
if [ ! -f "$ENV_FILE" ]; then
    cp "$ENV_EXAMPLE" "$ENV_FILE"
    echo ".env file created from .env.example. Remember to update your API keys!"
else
    echo ".env file already exists."
fi

# --------------------------
# Step 5: Dry-run test
# --------------------------
echo "Running dry-run test..."
python sync.py --dry-run

echo "✅ Setup complete. You can now run sync.py or main.py."
