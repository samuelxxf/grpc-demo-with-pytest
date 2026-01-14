#ifndef GRPC_LIB_H
#define GRPC_LIB_H

#ifdef __cplusplus
extern "C" {
#endif

#if defined(_WIN32)
    #define GRPC_LIB_EXPORT __declspec(dllexport)
#else
    #define GRPC_LIB_EXPORT __attribute__((visibility("default")))
#endif

// Initialize and start gRPC server in a separate thread
// Returns 0 on success, non-zero on failure
GRPC_LIB_EXPORT int grpc_server_init(const char* listen_address);

// Stop the gRPC server
GRPC_LIB_EXPORT void grpc_server_shutdown(void);

#ifdef __cplusplus
}
#endif

#endif // GRPC_LIB_H
