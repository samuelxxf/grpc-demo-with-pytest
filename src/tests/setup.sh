#!/bin/bash
# Setup script for gRPC test environment

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

echo "=========================================="
echo "Setting up gRPC Test Environment"
echo "=========================================="

# Check Python version
echo "Checking Python version..."
python3 --version

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Generate Python gRPC code
echo "Generating Python gRPC code..."
bash generate_proto.sh

echo ""
echo "=========================================="
echo "Setup completed!"
echo ""
echo "To activate the environment:"
echo "  source ${SCRIPT_DIR}/venv/bin/activate"
echo ""
echo "To run tests:"
echo "  ./run_tests.sh"
echo ""
echo "Make sure the gRPC server is running:"
echo "  ${SCRIPT_DIR}/../../build/grpctest_app"
echo "=========================================="
