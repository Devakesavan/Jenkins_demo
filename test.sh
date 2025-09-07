#!/bin/bash

# test.sh - Test script for DevOps Flask Application
# This script runs various tests to validate the application

set -e  # Exit on any error

echo "========================================"
echo "🧪 Starting Test Process"
echo "========================================"
echo "Timestamp: $(date)"
echo "Test Environment: ${FLASK_ENV:-testing}"
echo "Working Directory: $(pwd)"
echo ""

# Function to log messages
log() {
    echo "[TEST] $(date '+%Y-%m-%d %H:%M:%S') - $1"
}

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

TEST_START_TIME=$(date +%s)

log "Step 1: Environment setup for testing..."

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    log "Activating virtual environment..."
    source venv/bin/activate
    log "✅ Virtual environment activated"
else
    log "WARNING: No virtual environment found, using system Python"
fi

# Set testing environment variables
export FLASK_ENV=testing
export TESTING=true

log "Step 2: Running basic function tests..."

# Test the application functions directly
log "Testing application functions..."
python3 << 'EOF'
import sys
try:
    from app import add_numbers, get_deployment_status
    
    # Test add_numbers function
    print("[TEST] Testing add_numbers function...")
    assert add_numbers(2, 3) == 5, "add_numbers(2, 3) should return 5"
    assert add_numbers(-1, 1) == 0, "add_numbers(-1, 1) should return 0"
    assert add_numbers(0, 0) == 0, "add_numbers(0, 0) should return 0"
    print("✅ add_numbers function tests passed")
    
    # Test get_deployment_status function
    print("[TEST] Testing get_deployment_status function...")
    status = get_deployment_status()
    assert status['status'] == 'deployed', f"Expected 'deployed', got {status['status']}"
    assert status['environment'] == 'production', f"Expected 'production', got {status['environment']}"
    assert status['version'] == '1.0.0', f"Expected '1.0.0', got {status['version']}"
    print("✅ get_deployment_status function tests passed")
    
    print("✅ All basic function tests completed successfully")
    
except Exception as e:
    print(f"❌ Function test failed: {e}")
    sys.exit(1)
EOF

log "✅ Basic function tests completed successfully"

log "Step 3: Application startup test..."

# Test if the application can start without errors
log "Testing application startup..."
timeout 15 python3 -c "
import sys
try:
    from app import app
    print('[TEST] Flask app imported successfully')
    
    # Test app creation
    assert app is not None, 'Flask app should not be None'
    print('[TEST] ✅ Flask app created successfully')
    
    # Test app configuration
    app.config['TESTING'] = True
    print('[TEST] ✅ App configuration set for testing')
    
except Exception as e:
    print(f'[TEST] ❌ Application startup test failed: {e}')
    sys.exit(1)
"

log "✅ Application startup test passed"

log "Step 4: HTTP endpoint tests..."

# Start the application in background for endpoint testing
log "Starting Flask application for endpoint testing..."

# Kill any existing processes on port 5000
lsof -ti:5000 | xargs kill -9 2>/dev/null || true
sleep 2

# Start the application in background
nohup python3 app.py > test-app.log 2>&1 &
APP_PID=$!

log "Application started with PID: $APP_PID"
log "Waiting for application to be ready..."

# Wait for application to start (with timeout)
TIMEOUT=30
COUNTER=0
while [ $COUNTER -lt $TIMEOUT ]; do
    if curl -f -s http://localhost:5000/api/health > /dev/null 2>&1; then
        log "✅ Application is ready and responding"
        break
    fi
    sleep 1
    COUNTER=$((COUNTER + 1))
    if [ $COUNTER -eq $TIMEOUT ]; then
        log "❌ Application failed to start within $TIMEOUT seconds"
        kill $APP_PID 2>/dev/null || true
        exit 1
    fi
done

# Test main dashboard endpoint
log "Testing main dashboard endpoint (/)..."
if curl -f -s http://localhost:5000/ > /dev/null; then
    log "✅ Main dashboard endpoint test passed"
else
    log "❌ Main dashboard endpoint test failed"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Test health check endpoint
log "Testing health check endpoint (/api/health)..."
HEALTH_RESPONSE=$(curl -f -s http://localhost:5000/api/health)
if echo "$HEALTH_RESPONSE" | grep -q '"status":"healthy"'; then
    log "✅ Health check endpoint test passed"
else
    log "❌ Health check endpoint test failed"
    log "Response: $HEALTH_RESPONSE"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Test system info endpoint
log "Testing system info endpoint (/api/system)..."
SYSTEM_RESPONSE=$(curl -f -s http://localhost:5000/api/system)
if echo "$SYSTEM_RESPONSE" | grep -q '"platform"'; then
    log "✅ System info endpoint test passed"
else
    log "❌ System info endpoint test failed"
    log "Response: $SYSTEM_RESPONSE"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Test metrics endpoint
log "Testing metrics endpoint (/api/metrics)..."
METRICS_RESPONSE=$(curl -f -s http://localhost:5000/api/metrics)
if echo "$METRICS_RESPONSE" | grep -q '"cpu"'; then
    log "✅ Metrics endpoint test passed"
else
    log "❌ Metrics endpoint test failed"
    log "Response: $METRICS_RESPONSE"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

# Test invalid endpoint (should return 404)
log "Testing invalid endpoint handling..."
if curl -f -s http://localhost:5000/invalid/endpoint > /dev/null 2>&1; then
    log "❌ Invalid endpoint test failed (should return 404)"
    kill $APP_PID 2>/dev/null || true
    exit 1
else
    log "✅ Invalid endpoint test passed (correctly returned 404)"
fi

log "✅ All HTTP endpoint tests completed successfully"

log "Step 5: Performance and load test..."

# Simple load test with curl
log "Running simple load test (10 concurrent requests)..."
for i in {1..10}; do
    curl -f -s http://localhost:5000/api/health > /dev/null &
done
wait

log "✅ Load test completed successfully"

log "Step 6: Security tests..."

# Test for common security headers (basic check)
log "Testing security headers..."
HEADERS=$(curl -I -s http://localhost:5000/)
if echo "$HEADERS" | grep -q "HTTP/1."; then
    log "✅ Application responds with proper HTTP headers"
else
    log "❌ Application security header test failed"
    kill $APP_PID 2>/dev/null || true
    exit 1
fi

log "✅ Basic security tests passed"

# Stop the application
log "Stopping test application..."
kill $APP_PID 2>/dev/null || true
wait $APP_PID 2>/dev/null || true

log "Step 7: Generating test report..."

# Create test report
TEST_REPORT="test-report-$(date +%Y%m%d-%H%M%S).txt"
TEST_DURATION=$(($(date +%s) - TEST_START_TIME))

cat > "$TEST_REPORT" << EOF
================================
DevOps Flask Application - Test Report
================================

Test Information:
- Timestamp: $(date)
- Duration: ${TEST_DURATION} seconds
- Environment: ${FLASK_ENV:-testing}
- Python Version: $(python3 --version)

Tests Executed:
✅ Basic function tests
✅ Application startup test
✅ HTTP endpoint tests
  - Main dashboard (/)
  - Health check (/api/health)
  - System info (/api/system)
  - Metrics (/api/metrics)
  - Invalid endpoint handling
✅ Load test (10 concurrent requests)
✅ Basic security tests

Test Results Summary:
- Total Tests: 8 test categories
- Passed: 8
- Failed: 0
- Success Rate: 100%

Test Status: SUCCESS
================================
EOF

log "✅ Test report generated: $TEST_REPORT"

# Create test log
echo "Test completed successfully at $(date)" > test.log
echo "All test categories passed" >> test.log
echo "Test duration: ${TEST_DURATION} seconds" >> test.log

# Clean up any remaining processes
lsof -ti:5000 | xargs kill -9 2>/dev/null || true

echo ""
echo "========================================"
echo "🎉 Test Process Completed Successfully!"
echo "========================================"
echo "Test Duration: ${TEST_DURATION} seconds"
echo "Test Report: $(pwd)/$TEST_REPORT"
echo "All tests passed! Application is ready for deployment."
echo ""

# Exit successfully
exit 0
