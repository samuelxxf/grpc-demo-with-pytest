import pytest
import grpc
import allure
import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'generated'))

from helloworld_pb2 import HelloRequest, HelloReply
from helloworld_pb2_grpc import GreeterStub


@allure.epic("gRPC Service")
@allure.feature("Greeter Service")
class TestGreeterService:
    """Test cases for the Greeter gRPC service."""

    @allure.story("SayHello RPC")
    @allure.title("Test basic SayHello with valid name")
    @allure.severity(allure.severity_level.CRITICAL)
    @pytest.mark.smoke
    def test_say_hello_basic(self, greeter_stub):
        """Test basic SayHello functionality with a simple name."""
        with allure.step("Create HelloRequest with name 'World'"):
            request = HelloRequest(name="World")

        with allure.step("Call SayHello RPC"):
            response = greeter_stub.SayHello(request)

        with allure.step("Verify response message"):
            assert response.message == "Hello World"
            allure.attach(response.message, "Response Message", allure.attachment_type.TEXT)

    @allure.story("SayHello RPC")
    @allure.title("Test SayHello with empty name")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_say_hello_empty_name(self, greeter_stub):
        """Test SayHello with an empty name string."""
        with allure.step("Create HelloRequest with empty name"):
            request = HelloRequest(name="")

        with allure.step("Call SayHello RPC"):
            response = greeter_stub.SayHello(request)

        with allure.step("Verify response handles empty name"):
            assert response.message == "Hello "
            allure.attach(response.message, "Response Message", allure.attachment_type.TEXT)

    @allure.story("SayHello RPC")
    @allure.title("Test SayHello with Chinese characters")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_say_hello_unicode(self, greeter_stub):
        """Test SayHello with Unicode characters (Chinese)."""
        with allure.step("Create HelloRequest with Chinese name"):
            request = HelloRequest(name="世界")

        with allure.step("Call SayHello RPC"):
            response = greeter_stub.SayHello(request)

        with allure.step("Verify response with Unicode"):
            assert response.message == "Hello 世界"
            allure.attach(response.message, "Response Message", allure.attachment_type.TEXT)

    @allure.story("SayHello RPC")
    @allure.title("Test SayHello with special characters")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_say_hello_special_chars(self, greeter_stub):
        """Test SayHello with special characters."""
        with allure.step("Create HelloRequest with special characters"):
            special_name = "Test!@#$%^&*()_+-=[]{}|;':\",./<>?"
            request = HelloRequest(name=special_name)

        with allure.step("Call SayHello RPC"):
            response = greeter_stub.SayHello(request)

        with allure.step("Verify response with special characters"):
            expected = f"Hello {special_name}"
            assert response.message == expected
            allure.attach(response.message, "Response Message", allure.attachment_type.TEXT)

    @allure.story("SayHello RPC")
    @allure.title("Test SayHello with long name")
    @allure.severity(allure.severity_level.MINOR)
    @pytest.mark.regression
    def test_say_hello_long_name(self, greeter_stub):
        """Test SayHello with a very long name string."""
        with allure.step("Create HelloRequest with long name (1000 chars)"):
            long_name = "A" * 1000
            request = HelloRequest(name=long_name)

        with allure.step("Call SayHello RPC"):
            response = greeter_stub.SayHello(request)

        with allure.step("Verify response with long name"):
            expected = f"Hello {long_name}"
            assert response.message == expected
            allure.attach(f"Name length: {len(long_name)}", "Name Info", allure.attachment_type.TEXT)

    @allure.story("SayHello RPC")
    @allure.title("Test multiple sequential calls")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_say_hello_multiple_calls(self, greeter_stub):
        """Test multiple sequential SayHello calls."""
        names = ["Alice", "Bob", "Charlie", "David", "Eve"]

        for name in names:
            with allure.step(f"Call SayHello with name '{name}'"):
                request = HelloRequest(name=name)
                response = greeter_stub.SayHello(request)
                assert response.message == f"Hello {name}"

        allure.attach(str(names), "Tested Names", allure.attachment_type.TEXT)


@allure.epic("gRPC Service")
@allure.feature("Connection Tests")
class TestGrpcConnection:
    """Test cases for gRPC connection handling."""

    @allure.story("Connection")
    @allure.title("Test connection to server")
    @allure.severity(allure.severity_level.BLOCKER)
    @pytest.mark.smoke
    def test_server_connectivity(self, grpc_channel, grpc_server_address):
        """Test that we can connect to the gRPC server."""
        with allure.step(f"Check connectivity to {grpc_server_address}"):
            try:
                grpc.channel_ready_future(grpc_channel).result(timeout=5)
                connected = True
            except grpc.FutureTimeoutError:
                connected = False

        with allure.step("Verify connection status"):
            assert connected, f"Failed to connect to gRPC server at {grpc_server_address}"
            allure.attach(grpc_server_address, "Server Address", allure.attachment_type.TEXT)

    @allure.story("Connection")
    @allure.title("Test invalid server address")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.regression
    def test_invalid_server_connection(self):
        """Test behavior when connecting to invalid server address."""
        with allure.step("Create channel to invalid address"):
            invalid_channel = grpc.insecure_channel("localhost:99999")
            stub = GreeterStub(invalid_channel)

        with allure.step("Attempt to call RPC (expect failure)"):
            request = HelloRequest(name="Test")
            with pytest.raises(grpc.RpcError) as exc_info:
                stub.SayHello(request, timeout=2)

        with allure.step("Verify error details"):
            error = exc_info.value
            allure.attach(str(error.code()), "Error Code", allure.attachment_type.TEXT)

        invalid_channel.close()


@allure.epic("gRPC Service")
@allure.feature("Performance Tests")
class TestPerformance:
    """Performance test cases for the gRPC service."""

    @allure.story("Latency")
    @allure.title("Test single call latency")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.performance
    def test_single_call_latency(self, greeter_stub):
        """Measure latency of a single SayHello call."""
        request = HelloRequest(name="LatencyTest")

        with allure.step("Measure call latency"):
            start_time = time.time()
            response = greeter_stub.SayHello(request)
            end_time = time.time()

        latency_ms = (end_time - start_time) * 1000

        with allure.step("Verify latency is acceptable"):
            allure.attach(f"{latency_ms:.2f} ms", "Latency", allure.attachment_type.TEXT)
            assert latency_ms < 1000, f"Latency too high: {latency_ms:.2f} ms"

    @allure.story("Throughput")
    @allure.title("Test throughput with 100 calls")
    @allure.severity(allure.severity_level.NORMAL)
    @pytest.mark.performance
    def test_throughput(self, greeter_stub):
        """Measure throughput with multiple calls."""
        num_calls = 100

        with allure.step(f"Execute {num_calls} sequential calls"):
            start_time = time.time()
            for i in range(num_calls):
                request = HelloRequest(name=f"User{i}")
                response = greeter_stub.SayHello(request)
            end_time = time.time()

        total_time = end_time - start_time
        throughput = num_calls / total_time

        with allure.step("Calculate and verify throughput"):
            allure.attach(f"{throughput:.2f} calls/second", "Throughput", allure.attachment_type.TEXT)
            allure.attach(f"{total_time:.2f} seconds", "Total Time", allure.attachment_type.TEXT)
            assert throughput > 10, f"Throughput too low: {throughput:.2f} calls/second"
