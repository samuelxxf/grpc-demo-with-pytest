import pytest
import grpc
import sys
import os

# Add generated directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

from helloworld_pb2 import HelloRequest, HelloReply
from helloworld_pb2_grpc import GreeterStub


def pytest_addoption(parser):
    """Add command line options for pytest."""
    parser.addoption(
        "--grpc-host",
        action="store",
        default="localhost",
        help="gRPC server host"
    )
    parser.addoption(
        "--grpc-port",
        action="store",
        default="50051",
        help="gRPC server port"
    )


@pytest.fixture(scope="session")
def grpc_server_address(request):
    """Get gRPC server address from command line options."""
    host = request.config.getoption("--grpc-host")
    port = request.config.getoption("--grpc-port")
    return f"{host}:{port}"


@pytest.fixture(scope="session")
def grpc_channel(grpc_server_address):
    """Create a gRPC channel for the test session."""
    channel = grpc.insecure_channel(grpc_server_address)
    yield channel
    channel.close()


@pytest.fixture(scope="function")
def greeter_stub(grpc_channel):
    """Create a Greeter stub for each test function."""
    return GreeterStub(grpc_channel)


@pytest.fixture(scope="session")
def grpc_channel_with_timeout(grpc_server_address):
    """Create a gRPC channel with connection timeout."""
    channel = grpc.insecure_channel(
        grpc_server_address,
        options=[
            ('grpc.connect_timeout_ms', 5000),
            ('grpc.keepalive_time_ms', 10000),
        ]
    )
    # Wait for channel to be ready
    try:
        grpc.channel_ready_future(channel).result(timeout=5)
    except grpc.FutureTimeoutError:
        pytest.skip(f"Could not connect to gRPC server at {grpc_server_address}")
    yield channel
    channel.close()
