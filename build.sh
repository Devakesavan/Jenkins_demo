#!/bin/bash

# build.sh - Build script for Flask application
# This script handles the build process including dependency installation and preparation

set -e  # Exit on any error

echo "🔨 Starting build process..."
echo "=========================================="

# Print system information
echo "📋 System Information:"
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Working Directory: $(pwd)"
echo "Python Version: $(python3 --version)"
echo "Pip Version: $(pip3 --version)"
echo ""

# Create logs directory if it doesn't exist
echo "📁 Creating logs directory..."
mkdir -p logs
echo "✅ Logs directory created/verified"

# Check if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Found requirements.txt"
else
    echo "⚠️  requirements.txt not found, creating basic requirements..."
    cat > requirements.txt << EOF
Flask==2.3.3
pytest==7.4.2
pytest-flask==1.3.0
requests==2.31.0
EOF
    echo "✅ Basic requirements.txt created"
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating virtual environment..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
else
    echo "✅ Virtual environment already exists"
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate
echo "✅ Virtual environment activated"

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip > logs/pip_upgrade.log 2>&1
echo "✅ Pip upgraded successfully"

# Install dependencies
echo "📥 Installing dependencies from requirements.txt..."
pip install -r requirements.txt > logs/pip_install.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Dependencies installed successfully"
else
    echo "❌ Failed to install dependencies"
    echo "Check logs/pip_install.log for details"
    exit 1
fi

# Verify Flask installation
echo "🔍 Verifying Flask installation..."
python3 -c "import flask; print(f'Flask version: {flask.__version__}')" > logs/flask_verification.log 2>&1
if [ $? -eq 0 ]; then
    echo "✅ Flask verification successful"
    cat logs/flask_verification.log
else
    echo "❌ Flask verification failed"
    exit 1
fi

# Check application syntax
echo "📝 Checking application syntax..."
python3 -m py_compile app.py
if [ $? -eq 0 ]; then
    echo "✅ Application syntax check passed"
else
    echo "❌ Application syntax check failed"
    exit 1
fi

# Create a simple test to verify the application can be imported
echo "🧪 Testing application import..."
python3 -c "
try:
    from app import app
    print('✅ Application imported successfully')
    print(f'Application name: {app.name}')
except Exception as e:
    print(f'❌ Failed to import application: {e}')
    exit(1)
" > logs/import_test.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Application import test passed"
    cat logs/import_test.log
else
    echo "❌ Application import test failed"
    cat logs/import_test.log
    exit 1
fi

# Generate build information
echo "📊 Generating build information..."
cat > build_info.txt << EOF
Build Information
==================
Build Date: $(date)
Build User: $(whoami)
Build Host: $(hostname)
Python Version: $(python3 --version)
Flask Version: $(python3 -c "import flask; print(flask.__version__)")
Working Directory: $(pwd)
Git Commit: $(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
Git Branch: $(git branch --show-current 2>/dev/null || echo "N/A")
EOF

echo "✅ Build information generated"

# List installed packages
echo "📋 Generating installed packages list..."
pip freeze > logs/installed_packages.txt
echo "✅ Installed packages list saved to logs/installed_packages.txt"

# Create deployment artifacts
echo "📦 Creating deployment artifacts..."
mkdir -p artifacts
cp app.py artifacts/
cp requirements.txt artifacts/
cp build_info.txt artifacts/
echo "✅ Deployment artifacts created"

# Final build verification
echo "🏁 Final build verification..."
if [ -f "app.py" ] && [ -f "requirements.txt" ] && [ -d "venv" ]; then
    echo "✅ All required files are present"
    
    # Test that the application can start (without actually running it)
    timeout 10s python3 -c "
from app import app
import sys
print('✅ Application can be initialized')
print(f'✅ Routes registered: {len(app.url_map._rules)}')
sys.exit(0)
" > logs/final_verification.log 2>&1
    
    if [ $? -eq 0 ]; then
        echo "✅ Final verification passed"
    else
        echo "⚠️  Final verification had issues, but build continues"
    fi
else
    echo "❌ Missing required files for deployment"
    exit 1
fi

echo ""
echo "🎉 BUILD COMPLETED SUCCESSFULLY!"
echo "=========================================="
echo "📁 Build artifacts available in: artifacts/"
echo "📋 Build logs available in: logs/"
echo "📊 Build info available in: build_info.txt"
echo "⏰ Build completed at: $(date)"
echo ""

# Deactivate virtual environment
deactivate 2>/dev/null || true

exit 0
