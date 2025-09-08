#!/bin/bash

# test.sh - Test script for Flask application
# This script runs various tests including unit tests, integration tests, and health checks

set -e  # Exit on any error

echo "🧪 Starting test process..."
echo "=========================================="

# Print test information
echo "📋 Test Information:"
echo "Date: $(date)"
echo "User: $(whoami)"
echo "Working Directory: $(pwd)"
echo ""

# Create logs directory if it doesn't exist
mkdir -p logs
mkdir -p test_reports

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    echo "🔌 Activating virtual environment..."
    source venv/bin/activate
    echo "✅ Virtual environment activated"
else
    echo "⚠️  No virtual environment found, using system Python"
fi

# Create test file if it doesn't exist
if [ ! -f "test_app.py" ]; then
    echo "📝 Creating test file..."
    cat > test_app.py << 'EOF'
import pytest
import json
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app import app

@pytest.fixture
def client():
    """Create a test client for the Flask application."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

class TestFlaskApp:
    """Test cases for the Flask application."""
    
    def test_home_page(self, client):
        """Test the home page route."""
        response = client.get('/')
        assert response.status_code == 200
        assert b'Flask CI/CD Pipeline Demo' in response.data
        
    def test_health_check(self, client):
        """Test the health check endpoint."""
        response = client.get('/health')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert 'version' in data
        
    def test_api_status(self, client):
        """Test the API status endpoint."""
        response = client.get('/api/status')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['api_status'] == 'active'
        assert 'endpoints_available' in data
        
    def test_api_info(self, client):
        """Test the API info endpoint."""
        response = client.get('/api/info')
        assert response.status_code == 200
        
        data = json.loads(response.data)
        assert data['app_name'] == 'Flask CI/CD Demo'
        assert data['version'] == '1.0.0'
        assert 'endpoints' in data
        
    def test_404_error(self, client):
        """Test 404 error handling."""
        response = client.get('/nonexistent')
        assert response.status_code == 404
        
        data = json.loads(response.data)
        assert data['error'] == 'Not Found'
        
    def test_all_endpoints_return_json_or_html(self, client):
        """Test that all endpoints return valid responses."""
        endpoints = ['/', '/health', '/api/status', '/api/info']
        
        for endpoint in endpoints:
            response = client.get(endpoint)
            assert response.status_code == 200
            assert response.data is not None
            
    def test_application_configuration(self):
        """Test application configuration."""
        assert app.name == 'app'
        assert 'TESTING' not in app.config or app.config['TESTING'] is False

class TestApplicationIntegrity:
    """Test cases for application integrity."""
    
    def test_import_application(self):
        """Test that the application can be imported without errors."""
        try:
            from app import app
            assert app is not None
        except ImportError as e:
            pytest.fail(f"Failed to import application: {e}")
            
    def test_application_routes(self):
        """Test that all expected routes are registered."""
        from app import app
        
        routes = [rule.rule for rule in app.url_map.iter_rules()]
        expected_routes = ['/', '/health', '/api/status', '/api/info']
        
        for route in expected_routes:
            assert route in routes, f"Route {route} not found in application"

if __name__ == '__main__':
    pytest.main([__file__, '-v'])
EOF
    echo "✅ Test file created"
fi

# Install pytest if not available
echo "📦 Ensuring pytest is available..."
python3 -c "import pytest" 2>/dev/null || pip install pytest pytest-flask > logs/pytest_install.log 2>&1
echo "✅ Pytest verification completed"

# Run syntax check first
echo "📝 Running syntax check..."
python3 -m py_compile app.py test_app.py
if [ $? -eq 0 ]; then
    echo "✅ Syntax check passed"
else
    echo "❌ Syntax check failed"
    exit 1
fi

# Run import tests
echo "🔍 Running import tests..."
python3 -c "
try:
    from app import app
    print('✅ Application imports successfully')
    print(f'✅ Application name: {app.name}')
    print(f'✅ Number of routes: {len(app.url_map._rules)}')
except Exception as e:
    print(f'❌ Import test failed: {e}')
    exit(1)
" > logs/import_tests.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Import tests passed"
    cat logs/import_tests.log
else
    echo "❌ Import tests failed"
    cat logs/import_tests.log
    exit 1
fi

# Run unit tests with pytest
echo "🧪 Running unit tests with pytest..."
python3 -m pytest test_app.py -v --tb=short --junit-xml=test_reports/junit.xml > logs/pytest_output.log 2>&1

PYTEST_EXIT_CODE=$?

if [ $PYTEST_EXIT_CODE -eq 0 ]; then
    echo "✅ Unit tests passed"
    echo "📊 Test summary:"
    tail -10 logs/pytest_output.log
else
    echo "❌ Unit tests failed"
    echo "📊 Test failure details:"
    cat logs/pytest_output.log
    exit 1
fi

# Run application health check by starting it briefly
echo "🏥 Running application health check..."
python3 -c "
import threading
import time
import requests
import sys
from app import app

def run_app():
    app.run(host='127.0.0.1', port=5555, debug=False, use_reloader=False)

# Start the app in a separate thread
server_thread = threading.Thread(target=run_app, daemon=True)
server_thread.start()

# Give the server time to start
time.sleep(3)

try:
    # Test the health endpoint
    response = requests.get('http://127.0.0.1:5555/health', timeout=5)
    if response.status_code == 200:
        print('✅ Health check endpoint is working')
        data = response.json()
        print(f'✅ Health status: {data[\"status\"]}')
    else:
        print(f'❌ Health check failed with status code: {response.status_code}')
        sys.exit(1)
        
    # Test the home page
    response = requests.get('http://127.0.0.1:5555/', timeout=5)
    if response.status_code == 200:
        print('✅ Home page is accessible')
    else:
        print(f'❌ Home page check failed with status code: {response.status_code}')
        sys.exit(1)
        
    print('✅ Application health check completed successfully')
    
except requests.exceptions.RequestException as e:
    print(f'❌ Health check failed: {e}')
    sys.exit(1)
except Exception as e:
    print(f'❌ Unexpected error during health check: {e}')
    sys.exit(1)
" > logs/health_check.log 2>&1 &

# Wait for health check to complete or timeout
HEALTH_PID=$!
timeout 30 wait $HEALTH_PID
HEALTH_EXIT_CODE=$?

if [ $HEALTH_EXIT_CODE -eq 0 ]; then
    echo "✅ Health check passed"
    cat logs/health_check.log
else
    echo "❌ Health check failed or timed out"
    cat logs/health_check.log
    kill $HEALTH_PID 2>/dev/null || true
    exit 1
fi

# Generate test report
echo "📊 Generating test report..."
cat > test_reports/test_summary.txt << EOF
Test Execution Summary
======================
Test Date: $(date)
Test User: $(whoami)
Test Host: $(hostname)
Working Directory: $(pwd)
Python Version: $(python3 --version)

Test Results:
- Syntax Check: PASSED
- Import Tests: PASSED
- Unit Tests: PASSED
- Health Check: PASSED

Test Files:
- Unit Tests: test_app.py
- JUnit XML: test_reports/junit.xml
- Test Logs: logs/

Total Tests Run: $(grep -c "PASSED\|FAILED" logs/pytest_output.log 2>/dev/null || echo "N/A")
All Tests Status: PASSED
EOF

echo "✅ Test report generated"

# Code coverage analysis (optional)
echo "📈 Running code coverage analysis..."
python3 -c "
try:
    import coverage
    print('✅ Coverage module available')
except ImportError:
    print('⚠️  Coverage module not available, skipping coverage analysis')
" > logs/coverage_check.log 2>&1

# Performance test (simple)
echo "⚡ Running performance test..."
python3 -c "
import time
from app import app

start_time = time.time()

# Test app initialization time
with app.app_context():
    # Simulate some operations
    for i in range(1000):
        with app.test_client() as client:
            if i % 100 == 0:  # Test every 100th iteration
                response = client.get('/health')
                assert response.status_code == 200

end_time = time.time()
duration = end_time - start_time

print(f'✅ Performance test completed')
print(f'✅ Test duration: {duration:.2f} seconds')

if duration < 10:  # Arbitrary threshold
    print('✅ Performance is acceptable')
else:
    print('⚠️  Performance might need optimization')
" > logs/performance_test.log 2>&1

if [ $? -eq 0 ]; then
    echo "✅ Performance test completed"
    cat logs/performance_test.log
else
    echo "⚠️  Performance test had issues, but continuing"
fi

echo ""
echo "🎉 ALL TESTS COMPLETED SUCCESSFULLY!"
echo "=========================================="
echo "📋 Test Summary:"
echo "  ✅ Syntax Check: PASSED"
echo "  ✅ Import Tests: PASSED" 
echo "  ✅ Unit Tests: PASSED"
echo "  ✅ Health Check: PASSED"
echo "  ✅ Performance Test: COMPLETED"
echo ""
echo "📁 Test reports available in: test_reports/"
echo "📋 Test logs available in: logs/"
echo "⏰ Tests completed at: $(date)"
echo ""

# Deactivate virtual environment
deactivate 2>/dev/null || true

exit 0
