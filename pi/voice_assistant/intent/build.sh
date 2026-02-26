#!/bin/bash
# Build script for intent_handler C++ project

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
BUILD_DIR="$SCRIPT_DIR/build"

# Create build directory
mkdir -p "$BUILD_DIR"
cd "$BUILD_DIR"

# Configure and build
cmake ..
cmake --build .

# Run tests
echo "Running tests..."
ctest --output-on-failure

echo "Build complete! Executable: $BUILD_DIR/intent_handler"
