#!/bin/bash

# Test script for DevOps CI/CD Demo
echo "Starting DevOps application test process..."

# Check if build directory exists
if [ ! -d "build" ]; then
    echo "ERROR: Build directory does not exist"
    exit 1
fi

# Test 1: Verify index.html exists
echo "Test 1: Checking for index.html..."
if [ -f "build/index.html" ]; then
    echo "PASS: index.html found in build directory"
else
    echo "FAIL: index.html not found in build directory"
    exit 1
fi

# Test 2: Verify build_info.txt exists
echo "Test 2: Checking for build_info.txt..."
if [ -f "build/build_info.txt" ]; then
    echo "PASS: build_info.txt found in build directory"
else
    echo "FAIL: build_info.txt not found in build directory"
    exit 1
fi

# Test 3: Check HTML content for required elements
echo "Test 3: Validating HTML structure..."
if grep -q "DevOps Pipeline Dashboard" build/index.html; then
    echo "PASS: Required content found in HTML"
else
    echo "FAIL: Required content not found in HTML"
    exit 1
fi

# Test 4: Check for CSS styles
echo "Test 4: Checking CSS styles..."
if grep -q "background: linear-gradient" build/index.html; then
    echo "PASS: CSS styles found in HTML"
else
    echo "FAIL: CSS styles not found in HTML"
    exit 1
fi

# Test 5: Verify build information
echo "Test 5: Checking build information..."
if grep -q "Build Number" build/build_info.txt; then
    echo "PASS: Build information is complete"
else
    echo "FAIL: Build information is incomplete"
    exit 1
fi

# Test 6: Check for JavaScript content
echo "Test 6: Checking for JavaScript functionality..."
if grep -q "animatePipeline" build/index.html; then
    echo "PASS: JavaScript found in HTML"
else
    echo "FAIL: JavaScript not found in HTML"
    exit 1
fi

# Test 7: Validate HTML structure
echo "Test 7: Validating HTML structure..."
if grep -q "<!DOCTYPE html>" build/index.html; then
    echo "PASS: HTML structure is valid"
else
    echo "FAIL: HTML structure is invalid"
    exit 1
fi

# Test 8: Simulate a test that might fail (can be toggled)
# Set FAIL_TEST environment variable to "true" to make this test fail
if [ "$FAIL_TEST" = "true" ]; then
    echo "Test 8: Simulating a failed test (as requested)..."
    echo "FAIL: This test was configured to fail"
    exit 1
else
    echo "Test 8: Simulating a passing test..."
    echo "PASS: This test passed as expected"
fi

# All tests passed
echo "All tests completed successfully!"
echo "Test Summary:"
echo " - 8 tests run"
echo " - 0 failures"
echo " - 100% pass rate"

exit 0
