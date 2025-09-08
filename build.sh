#!/bin/bash
echo "========================================"
echo "🚀 Starting Build Process"
echo "========================================"

echo "Timestamp: $(date)"
echo "Build Environment: production"
echo "Python Version: $(python3 --version)"
echo "Working Directory: $(pwd)"

echo "[BUILD] Step 1: Validating environment and dependencies..."
if command -v python3 >/dev/null 2>&1; then
    echo "[BUILD] ✅ Python 3 is available"
else
    echo "[BUILD] ❌ Python 3 is not installed"
    exit 1
fi

echo "[BUILD] Step 2: Installing dependencies..."
if [ -f requirements.txt ]; then
    echo "[BUILD] Installing Python dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    echo "[BUILD] ⚠️ No requirements.txt found, skipping dependencies"
fi

echo "[BUILD] Step 3: Validating application files..."
if [ -f app.py ]; then
    echo "[BUILD] ✅ app.py found"
else
    echo "[BUILD] ❌ app.py not found"
    exit 1
fi

echo "[BUILD] ✅ Build completed successfully"
