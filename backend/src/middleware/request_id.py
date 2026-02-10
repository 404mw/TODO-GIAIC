"""Request ID middleware for request correlation and tracing.

Generates a unique request ID for each request and adds it to:
- Request state (for use in handlers and logging)
- Response headers (X-Request-ID)
"""

from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.requests import Request
from starlette.responses import Response


class RequestIDMiddleware(BaseHTTPMiddleware):
    """Middleware to add unique request IDs for correlation.

    The request ID is:
    - Generated as a UUID v4 if not provided
    - Stored in request.state.request_id
    - Returned in the X-Request-ID response header
    """

    HEADER_NAME = "X-Request-ID"

    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        """Process the request and add request ID."""
        # Check if request ID was provided in headers
        request_id = request.headers.get(self.HEADER_NAME)

        # Generate a new one if not provided
        if not request_id:
            request_id = str(uuid4())

        # Store in request state for access in handlers
        request.state.request_id = request_id

        # Process the request
        response = await call_next(request)

        # Add request ID to response headers
        response.headers[self.HEADER_NAME] = request_id

        return response
