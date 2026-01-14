cmake_minimum_required(VERSION 3.18)
project(grpctest)

set(CMAKE_CXX_STANDARD 17)
set(CMAKE_CXX_STANDARD_REQUIRED ON)

# Use precompiled gRPC from /opt/grpc-dev
list(PREPEND CMAKE_PREFIX_PATH "/opt/grpc-dev")

# Find required packages
find_package(Protobuf CONFIG REQUIRED)
find_package(gRPC CONFIG REQUIRED)

# Get protoc and grpc_cpp_plugin executables
set(_PROTOBUF_PROTOC $<TARGET_FILE:protobuf::protoc>)
set(_GRPC_CPP_PLUGIN_EXECUTABLE $<TARGET_FILE:gRPC::grpc_cpp_plugin>)

# Proto file
get_filename_component(hw_proto "helloworld.proto" ABSOLUTE)
get_filename_component(hw_proto_path "${hw_proto}" PATH)

# Generated sources
set(hw_proto_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.cc")
set(hw_proto_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.pb.h")
set(hw_grpc_srcs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.cc")
set(hw_grpc_hdrs "${CMAKE_CURRENT_BINARY_DIR}/helloworld.grpc.pb.h")

# Custom command to generate protobuf and grpc files
add_custom_command(
    OUTPUT "${hw_proto_srcs}" "${hw_proto_hdrs}" "${hw_grpc_srcs}" "${hw_grpc_hdrs}"
    COMMAND ${_PROTOBUF_PROTOC}
    ARGS --grpc_out "${CMAKE_CURRENT_BINARY_DIR}"
         --cpp_out "${CMAKE_CURRENT_BINARY_DIR}"
         -I "${hw_proto_path}"
         --plugin=protoc-gen-grpc="${_GRPC_CPP_PLUGIN_EXECUTABLE}"
         "${hw_proto}"
    DEPENDS "${hw_proto}"
)

# Include generated headers
include_directories("${CMAKE_CURRENT_BINARY_DIR}")

# ============================================
# Build shared library with hidden symbols
# ============================================
add_library(grpc_lib SHARED
    grpc_lib.cpp
    ${hw_proto_srcs}
    ${hw_grpc_srcs}
)

# Hide all symbols by default, only export marked ones
set_target_properties(grpc_lib PROPERTIES
    CXX_VISIBILITY_PRESET hidden
    VISIBILITY_INLINES_HIDDEN ON
    POSITION_INDEPENDENT_CODE ON
)

# Link gRPC statically into the shared library
target_link_libraries(grpc_lib PRIVATE
    -Wl,--whole-archive
    gRPC::grpc++
    gRPC::grpc++_reflection
    protobuf::libprotobuf
    -Wl,--no-whole-archive
)

# Exclude symbols from linked static libraries
target_link_options(grpc_lib PRIVATE
    -Wl,--exclude-libs,ALL
)

# ============================================
# Build executable that uses the shared library
# ============================================
add_executable(grpctest_app
    main.cpp
)

target_include_directories(grpctest_app PRIVATE
    ${CMAKE_CURRENT_SOURCE_DIR}
)

target_link_libraries(grpctest_app PRIVATE
    grpc_lib
)

# Set rpath for the executable to find the library
set_target_properties(grpctest_app PROPERTIES
    BUILD_RPATH "${CMAKE_CURRENT_BINARY_DIR}"
    INSTALL_RPATH "$ORIGIN"
)
