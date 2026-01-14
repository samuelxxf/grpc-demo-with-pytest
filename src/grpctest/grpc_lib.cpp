#include "grpc_lib.h"
#include "helloworld.grpc.pb.h"

#include <grpcpp/grpcpp.h>
#include <grpcpp/ext/proto_server_reflection_plugin.h>

#include <iostream>
#include <memory>
#include <string>
#include <thread>
#include <atomic>
#include <mutex>

using grpc::Server;
using grpc::ServerBuilder;
using grpc::ServerContext;
using grpc::Status;
using helloworld::Greeter;
using helloworld::HelloReply;
using helloworld::HelloRequest;

namespace {

class GreeterServiceImpl final : public Greeter::Service {
    Status SayHello(ServerContext* context, const HelloRequest* request,
                    HelloReply* reply) override {
        std::string prefix("Hello ");
        reply->set_message(prefix + request->name());
        std::cout << "[grpc_lib] Received request from: " << request->name() << std::endl;
        return Status::OK;
    }
};

std::unique_ptr<Server> g_server;
std::unique_ptr<std::thread> g_server_thread;
std::atomic<bool> g_initialized{false};
std::mutex g_mutex;

void RunServerInternal(const std::string& address) {
    GreeterServiceImpl service;

    grpc::EnableDefaultHealthCheckService(true);
    grpc::reflection::InitProtoReflectionServerBuilderPlugin();

    ServerBuilder builder;
    builder.AddListeningPort(address, grpc::InsecureServerCredentials());
    builder.RegisterService(&service);

    g_server = builder.BuildAndStart();
    if (g_server) {
        std::cout << "[grpc_lib] Server listening on " << address << std::endl;
        g_server->Wait();
        std::cout << "[grpc_lib] Server stopped" << std::endl;
    }
}

} // anonymous namespace

extern "C" {

GRPC_LIB_EXPORT int grpc_server_init(const char* listen_address) {
    std::lock_guard<std::mutex> lock(g_mutex);

    if (g_initialized.load()) {
        std::cerr << "[grpc_lib] Server already initialized" << std::endl;
        return -1;
    }

    std::string address = listen_address ? listen_address : "0.0.0.0:50051";

    g_server_thread = std::make_unique<std::thread>(RunServerInternal, address);
    g_initialized.store(true);

    // Give the server a moment to start
    std::this_thread::sleep_for(std::chrono::milliseconds(100));

    std::cout << "[grpc_lib] Server thread started" << std::endl;
    return 0;
}

GRPC_LIB_EXPORT void grpc_server_shutdown(void) {
    std::lock_guard<std::mutex> lock(g_mutex);

    if (!g_initialized.load()) {
        return;
    }

    if (g_server) {
        std::cout << "[grpc_lib] Shutting down server..." << std::endl;
        g_server->Shutdown();
    }

    if (g_server_thread && g_server_thread->joinable()) {
        g_server_thread->join();
    }

    g_server.reset();
    g_server_thread.reset();
    g_initialized.store(false);

    std::cout << "[grpc_lib] Server shutdown complete" << std::endl;
}

} // extern "C"
