#!/bin/bash

# build.sh - Build script for DevOps Flask Application
# This script handles the build process for the Flask application

set -e  # Exit on any error

echo "========================================"
echo "🚀 Starting Build Process"
echo "========================================"
echo "Timestamp: $(date)"
echo "Build Environment: ${FLASK_ENV:-production}"
echo "Python Version: $(python3 --version)"
echo "Working Directory: $(pwd)"
echo ""

# Function to log messages
log() {
    echo "[BUILD] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

log "Step 1: Validating environment and dependencies..."

# Check if Python 3 is available
if ! command_exists python3; then
    log "ERROR: Python 3 is not installed or not in PATH"
    exit 1
fi

log "✅ Python 3 is available"

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    log "Creating Python virtual environment..."
    python3 -m venv venv
    log "✅ Virtual environment created"
else
    log "✅ Virtual environment already exists"
fi

# Activate virtual environment
log "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
log "Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1

log "Step 2: Installing dependencies..."

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    log "ERROR: requirements.txt not found"
    exit 1
fi

# Install dependencies
log "Installing Python dependencies from requirements.txt..."
pip install -r requirements.txt

log "✅ Dependencies installed successfully"

# List installed packages
log "Installed packages:"
pip list

log "Step 3: Validating application files..."

# Check if main application file exists
if [ ! -f "app.py" ]; then
    log "ERROR: app.py not found"
    exit 1
fi

log "✅ app.py found"

# Check if test file exists
if [ ! -f "test_app.py" ]; then
    log "ERROR: test_app.py not found"
    exit 1
fi

log "✅ test_app.py found"

log "Step 4: Syntax validation..."

# Check Python syntax for main application
log "Validating app.py syntax..."
python3 -m py_compile app.py
log "✅ app.py syntax is valid"

# Check Python syntax for tests (if exists)
if [ -f "simple_tests.py" ]; then
    log "Validating simple_tests.py syntax..."
    python3 -m py_compile simple_tests.py
    log "✅ simple_tests.py syntax is valid"
else
    log "ℹ️ No test file found, skipping test syntax validation"
fi

log "Step 5: Creating build artifacts..."

# Create logs directory if it doesn't exist
mkdir -p logs

# Create build info file
BUILD_INFO_FILE="build-info.json"
log "Creating build information file: $BUILD_INFO_FILE"

cat > "$BUILD_INFO_FILE" << EOF
{
    "build_timestamp": "$(date -u +%Y-%m-%dT%H:%M:%SZ)",
    "build_number": "${BUILD_NUMBER:-local}",
    "git_commit": "$(git rev-parse HEAD 2>/dev/null || echo 'unknown')",
    "git_branch": "$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')",
    "python_version": "$(python3 --version)",
    "flask_env": "${FLASK_ENV:-production}",
    "build_status": "success"
}
EOF

log "✅ Build information file created"

# Create deployment package (simulate)
log "Creating deployment package..."
mkdir -p dist

# Copy essential files to dist directory
cp app.py dist/
cp requirements.txt dist/
cp "$BUILD_INFO_FILE" dist/

log "✅ Deployment package created in dist/ directory"

log "Step 6: Build verification..."

# Test import of main application
log "Testing application import..."
python3 -c "
try:
    from app import app, add_numbers, get_deployment_status
    print('✅ Application imports successfully')
    
    # Test basic functions
    result = add_numbers(2, 3)
    assert result == 5, f'Expected 5, got {result}'
    print('✅ add_numbers function works correctly')
    
    status = get_deployment_status()
    assert status['status'] == 'deployed', f'Expected deployed status, got {status}'
    print('✅ get_deployment_status function works correctly')
    
    print('✅ All basic function tests passed')
except Exception as e:
    print(f'❌ Application import/test failed: {e}')
    exit(1)
"

log "✅ Application import and basic tests successful"

# Generate build report
BUILD_REPORT="build-report-$(date +%Y%m%d-%H%M%S).txt"
log "Generating build report: $BUILD_REPORT"

cat > "$BUILD_REPORT" << EOF
================================
DevOps Flask Application - Build Report
================================

Build Information:
- Timestamp: $(date)
- Build Number: ${BUILD_NUMBER:-local}
- Environment: ${FLASK_ENV:-production}
- Python Version: $(python3 --version)
- Git Commit: $(git rev-parse HEAD 2>/dev/null || echo 'unknown')
- Git Branch: $(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo 'unknown')

Build Steps Completed:
✅ Environment validation
✅ Virtual environment setup
✅ Dependencies installation
✅ File validation
✅ Syntax checking
✅ Build artifacts creation
✅ Application import test
✅ Basic function tests

Dependencies Installed:
$(pip list)

Build Status: SUCCESS
================================
EOF

log "✅ Build report generated: $BUILD_REPORT"

# Create build log
cp /dev/null build.log 2>/dev/null || true
echo "Build completed successfully at $(date)" >> build.log
echo "Build artifacts created in dist/ directory" >> build.log

log "Step 7: Post-build cleanup..."

# Set proper permissions
chmod +x dist/app.py 2>/dev/null || true

log "✅ Post-build cleanup completed"

echo ""
echo "========================================"
echo "🎉 Build Process Completed Successfully!"
echo "========================================"
echo "Build Duration: $(($(date +%s) - ${BUILD_START_TIME:-$(date +%s)})) seconds"
echo "Artifacts Location: $(pwd)/dist/"
echo "Build Report: $(pwd)/$BUILD_REPORT"
echo "Next Step: Run ./test.sh to execute tests"
echo ""

# Exit successfully
exit 0
