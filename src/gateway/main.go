package main

import (
	"context"
	"flag"
	"fmt"
	"log"
	"net/http"

	"github.com/grpc-ecosystem/grpc-gateway/v2/runtime"
	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	robotsv1 "github.com/xxf/grpc-test/gen/gateway/robots/v1"
)

var (
	grpcServerAddr = flag.String("grpc-server", "localhost:50051", "gRPC server address")
	httpAddr       = flag.String("http-addr", ":8080", "HTTP server address")
)

func main() {
	flag.Parse()

	ctx := context.Background()
	ctx, cancel := context.WithCancel(ctx)
	defer cancel()

	// Create gRPC client connection
	conn, err := grpc.DialContext(
		ctx,
		*grpcServerAddr,
		grpc.WithTransportCredentials(insecure.NewCredentials()),
		grpc.WithBlock(),
	)
	if err != nil {
		log.Fatalf("Failed to connect to gRPC server: %v", err)
	}
	defer conn.Close()

	// Create gateway mux
	mux := runtime.NewServeMux()

	// Register AuthService handler
	err = robotsv1.RegisterAuthServiceHandler(ctx, mux, conn)
	if err != nil {
		log.Fatalf("Failed to register AuthService handler: %v", err)
	}

	// Start HTTP server
	fmt.Printf("Starting HTTP gateway server on %s\n", *httpAddr)
	fmt.Printf("Proxying requests to gRPC server at %s\n", *grpcServerAddr)
	fmt.Println("\nAvailable endpoints:")
	fmt.Println("  POST /api/v1/auth/login")
	fmt.Println("  POST /api/v1/auth/logout")

	if err := http.ListenAndServe(*httpAddr, mux); err != nil {
		log.Fatalf("Failed to start HTTP server: %v", err)
	}
}
