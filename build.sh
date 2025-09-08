#!/bin/bash

# Build script for DevOps CI/CD Demo
echo "Starting DevOps application build process..."

# Create build directory if it doesn't exist
mkdir -p build

# Copy application files to build directory
cp index.html build/
echo "Application files copied to build directory"

# Simulate build process
echo "Installing dependencies..."
sleep 2
echo "Compiling application..."
sleep 3

# Create build information file
echo "Creating build information..."
echo "Build Number: $BUILD_NUMBER" > build/build_info.txt
echo "Build Date: $(date)" >> build/build_info.txt
echo "Built by: $JOB_NAME" >> build/build_info.txt
echo "Build Node: $NODE_NAME" >> build/build_info.txt

# Generate build artifact manifest
echo "Generating artifact manifest..."
echo "Files in this build:" > build/artifacts.txt
ls -la build/ >> build/artifacts.txt

# Simulate a compilation step
echo "Optimizing assets..."
sleep 2

# Verify build contents
echo "Verifying build contents..."
if [ -f "build/index.html" ]; then
    echo "HTML file verified successfully"
else
    echo "ERROR: HTML file missing from build"
    exit 1
fi

if [ -f "build/build_info.txt" ]; then
    echo "Build info file verified successfully"
else
    echo "ERROR: Build info file missing from build"
    exit 1
fi

echo "Build completed successfully!"
echo "Build artifacts are available in the build directory"
