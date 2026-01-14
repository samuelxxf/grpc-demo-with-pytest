#!/bin/bash
# Run gRPC tests with Allure reporting

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "${SCRIPT_DIR}"

# Default values
GRPC_HOST="${GRPC_HOST:-localhost}"
GRPC_PORT="${GRPC_PORT:-50051}"
MARKERS=""
OPEN_REPORT=false

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --host)
            GRPC_HOST="$2"
            shift 2
            ;;
        --port)
            GRPC_PORT="$2"
            shift 2
            ;;
        --smoke)
            MARKERS="-m smoke"
            shift
            ;;
        --regression)
            MARKERS="-m regression"
            shift
            ;;
        --performance)
            MARKERS="-m performance"
            shift
            ;;
        --open)
            OPEN_REPORT=true
            shift
            ;;
        --help)
            echo "Usage: $0 [OPTIONS]"
            echo ""
            echo "Options:"
            echo "  --host HOST       gRPC server host (default: localhost)"
            echo "  --port PORT       gRPC server port (default: 50051)"
            echo "  --smoke           Run only smoke tests"
            echo "  --regression      Run only regression tests"
            echo "  --performance     Run only performance tests"
            echo "  --open            Open Allure report after tests"
            echo "  --help            Show this help message"
            exit 0
            ;;
        *)
            echo "Unknown option: $1"
            exit 1
            ;;
    esac
done

echo "=========================================="
echo "gRPC Test Runner"
echo "=========================================="
echo "Server: ${GRPC_HOST}:${GRPC_PORT}"
echo ""

# Check if generated files exist, if not generate them
if [ ! -f "${SCRIPT_DIR}/generated/helloworld_pb2.py" ]; then
    echo "Generating Python gRPC code..."
    bash "${SCRIPT_DIR}/generate_proto.sh"
fi

# Clean previous results
echo "Cleaning previous test results..."
rm -rf "${SCRIPT_DIR}/reports/allure-results"
mkdir -p "${SCRIPT_DIR}/reports/allure-results"

# Run tests
echo "Running tests..."
echo ""

pytest \
    --grpc-host="${GRPC_HOST}" \
    --grpc-port="${GRPC_PORT}" \
    --alluredir="${SCRIPT_DIR}/reports/allure-results" \
    ${MARKERS} \
    "${SCRIPT_DIR}"

# Generate Allure report
echo ""
echo "Generating Allure report..."

if command -v allure &> /dev/null; then
    allure generate "${SCRIPT_DIR}/reports/allure-results" \
        -o "${SCRIPT_DIR}/reports/allure-report" \
        --clean

    echo ""
    echo "=========================================="
    echo "Test completed!"
    echo "Allure results: ${SCRIPT_DIR}/reports/allure-results"
    echo "Allure report:  ${SCRIPT_DIR}/reports/allure-report"
    echo ""
    echo "To view the report, run:"
    echo "  allure open ${SCRIPT_DIR}/reports/allure-report"
    echo "Or:"
    echo "  allure serve ${SCRIPT_DIR}/reports/allure-results"
    echo "=========================================="

    if [ "$OPEN_REPORT" = true ]; then
        allure open "${SCRIPT_DIR}/reports/allure-report"
    fi
else
    echo ""
    echo "=========================================="
    echo "Test completed!"
    echo "Allure results: ${SCRIPT_DIR}/reports/allure-results"
    echo ""
    echo "Note: 'allure' command not found."
    echo "Install Allure CLI to generate HTML report:"
    echo "  sudo apt install allure  # Debian/Ubuntu"
    echo "  brew install allure      # macOS"
    echo ""
    echo "Or view results with:"
    echo "  allure serve ${SCRIPT_DIR}/reports/allure-results"
    echo "=========================================="
fi
