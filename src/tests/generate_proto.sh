#!/bin/bash
# Generate Python gRPC code from proto files

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROTO_DIR="${SCRIPT_DIR}/proto"
OUTPUT_DIR="${SCRIPT_DIR}/generated"

# Create output directory if not exists
mkdir -p "${OUTPUT_DIR}"

# Generate Python code
python3 -m grpc_tools.protoc \
    -I "${PROTO_DIR}" \
    --python_out="${OUTPUT_DIR}" \
    --grpc_python_out="${OUTPUT_DIR}" \
    "${PROTO_DIR}/helloworld.proto"

# Create __init__.py for the generated package
touch "${OUTPUT_DIR}/__init__.py"

echo "Proto files generated successfully in ${OUTPUT_DIR}"
