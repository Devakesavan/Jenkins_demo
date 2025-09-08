aa#!/bin/bash
echo "========================================"
echo "🧪 Running Tests"
echo "========================================"

echo "Timestamp: $(date)"
echo "Working Directory: $(pwd)"

# Ensure virtual environment is active (if using Jenkins venv)
if [ -d ".venv" ]; then
    echo "[TEST] Activating virtual environment..."
    source .venv/bin/activate
fi

# Check for pytest
if ! command -v pytest &> /dev/null; then
    echo "[TEST] Installing pytest..."
    pip install pytest
fi

# Run tests if test_app.py exists
if [ -f "test_app.py" ]; then
    echo "[TEST] Found test_app.py, running pytest..."
    pytest -v test_app.py
    TEST_RESULT=$?
    if [ $TEST_RESULT -eq 0 ]; then
        echo "[TEST] ✅ All tests passed!"
    else
        echo "[TEST] ❌ Some tests failed!"
        exit $TEST_RESULT
    fi
else
    echo "[TEST] ⚠️ No test_app.py found, skipping tests."
fi
