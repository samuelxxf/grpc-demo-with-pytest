#include <iostream>
#include <csignal>
#include <thread>
#include <chrono>
#include "grpc_lib.h"

static volatile bool g_running = true;

void signal_handler(int signum) {
    std::cout << "\nReceived signal " << signum << ", shutting down..." << std::endl;
    g_running = false;
}

int main(int argc, char** argv) {
    // Set up signal handlers
    signal(SIGINT, signal_handler);
    signal(SIGTERM, signal_handler);

    const char* address = "0.0.0.0:50051";
    if (argc > 1) {
        address = argv[1];
    }

    std::cout << "Starting gRPC server..." << std::endl;

    // Initialize gRPC server in a separate thread
    int ret = grpc_server_init(address);
    if (ret != 0) {
        std::cerr << "Failed to initialize gRPC server" << std::endl;
        return 1;
    }

    std::cout << "gRPC server is running. Press Ctrl+C to stop." << std::endl;

    // Main thread can do other work here
    while (g_running) {
        std::this_thread::sleep_for(std::chrono::seconds(1));
    }

    // Shutdown the server
    grpc_server_shutdown();

    std::cout << "Application exited cleanly." << std::endl;
    return 0;
}
