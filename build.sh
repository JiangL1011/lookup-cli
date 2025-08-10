#!/bin/bash

# Build script for lookup-cli using nuitka (Local Development)
# This script compiles the Python project into a single executable file named 'lu'
# All build artifacts are placed in the 'build' directory
# 
# Note: GitHub Actions uses the same nuitka commands but integrated directly in the workflow

set -e  # Exit on any error

echo "🚀 Starting build process..."

# Check if uv is available
if ! command -v uv &> /dev/null; then
    echo "❌ Error: uv is not installed or not in PATH"
    exit 1
fi

# Install development dependencies (including nuitka)
echo "📦 Installing development dependencies..."
uv sync --group dev

# Clean up any previous build artifacts
echo "🧹 Cleaning up previous build artifacts..."
rm -rf build main.build main.dist main.onefile-build

# Create build directory
mkdir -p build

# Build the executable using nuitka
echo "🔨 Building executable with nuitka..."
echo -e "no\n" | uv run nuitka \
    --mode=onefile \
    --output-dir=build \
    --output-filename=lu \
    --include-package=app \
    --include-package-data=langdetect \
    main.py

# Verify the build was successful
if [ -f "build/lu" ]; then
    echo "✅ Build successful!"
    echo "📊 Executable size: $(ls -lh build/lu | awk '{print $5}')"
    echo "🧪 Testing executable..."
    build/lu --help > /dev/null && echo "✅ Basic functionality test passed!"
else
    echo "❌ Build failed!"
    exit 1
fi


echo "🎉 Build complete! The executable 'lu' is ready to use."
echo "� Output location: build/lu"
echo "�💡 Try: build/lu --help"
