import logging
import signal
import sys
from concurrent import futures

import grpc

import os
import sys

# --- FIX: WeasyPrint GTK Dependency ---
# This must run BEFORE any WeasyPrint code is imported, even indirectly.
MSYS2_DLL_PATH = r'D:\BME\msys2\mingw64\bin'

if os.path.exists(MSYS2_DLL_PATH):
    # This tells Python where to find the DLLs and their sub-dependencies.
    os.add_dll_directory(MSYS2_DLL_PATH)
else:
    # This warning helps confirm that the path itself is the issue
    print(f"ERROR: MSYS2 DLL path not found at {MSYS2_DLL_PATH}. Check installation.")

from config.settings import settings
from server.generated import report_pb2, report_pb2_grpc
from server.service_impl import ReportServiceServicer

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


class AuthInterceptor(grpc.ServerInterceptor):
    """
    Simple gRPC server interceptor that checks metadata for an authorization token.
    Expects metadata key: "authorization": "Bearer <token>"
    """
    def __init__(self):
        self.expected_token = settings.api_key

    def _unauthenticated_handler(self, context, details="unauthenticated"):
        context.abort(grpc.StatusCode.UNAUTHENTICATED, details)

    def intercept_service(self, continuation, handler_call_details):
        meta = {}
        if handler_call_details.invocation_metadata:
            meta = {k: v for k, v in handler_call_details.invocation_metadata}

        token = meta.get("authorization", "")
        if token.startswith("Bearer "):
            token = token.split(" ", 1)[1]

        if self.expected_token is None:
            logger.warning("No expected auth token configured; rejecting all requests by default.")
            # Deny access if no token configured
            def handler(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Auth token not configured on server")
            return grpc.unary_unary_rpc_method_handler(handler)

        if token != self.expected_token:
            # Deny access
            def handler(request, context):
                context.abort(grpc.StatusCode.UNAUTHENTICATED, "Invalid service token")
            return grpc.unary_unary_rpc_method_handler(handler)

        # allow
        return continuation(handler_call_details)


def serve():
    host = settings.grpc_host
    port = settings.grpc_port

    server_address = f"{host}:{port}"

    # Create gRPC server with auth interceptor
    interceptor = AuthInterceptor()

    server = grpc.server(
        futures.ThreadPoolExecutor(max_workers=10),
        interceptors=(interceptor,)
    )

    report_pb2_grpc.add_ReportServiceServicer_to_server(ReportServiceServicer(), server)
    server.add_insecure_port(server_address)
    server.start()

    logger.info("gRPC server started and listening on %s", server_address)

    def _graceful_shutdown(signum, frame):
        logger.info("Signal %s received: stopping gRPC server...", signum)
        server.stop(0)
        sys.exit(0)

    signal.signal(signal.SIGINT, _graceful_shutdown)
    signal.signal(signal.SIGTERM, _graceful_shutdown)

    server.wait_for_termination()


if __name__ == "__main__":
    serve()
