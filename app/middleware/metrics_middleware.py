"""
Prometheus metrics for FastAPI application.
"""
from prometheus_client import Counter, Histogram, Gauge
import time
from typing import Callable

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

# Define metrics
REQUEST_COUNT = Counter(
    'fastapi_requests_total',
    'Total number of requests',
    ['method', 'endpoint', 'status_code']
)

REQUEST_DURATION = Histogram(
    'fastapi_request_duration_seconds',
    'Request duration in seconds',
    ['method', 'endpoint']
)

REQUESTS_IN_PROGRESS = Gauge(
    'fastapi_requests_in_progress',
    'Number of requests currently being processed'
)

ERROR_COUNT = Counter(
    'fastapi_errors_total',
    'Total number of errors',
    ['method', 'endpoint', 'error_type']
)


class MetricsMiddleware(BaseHTTPMiddleware):
    """Middleware to collect Prometheus metrics."""
    
    async def dispatch(
        self, request: Request, call_next: Callable
    ) -> Response:
        # Ignore metrics endpoint itself
        if request.url.path == "/metrics":
            return await call_next(request)
        
        # Track requests in progress
        REQUESTS_IN_PROGRESS.inc()
        
        # Record start time
        start_time = time.time()
        
        try:
            # Process request
            response = await call_next(request)
            
            # Record metrics
            duration = time.time() - start_time
            
            REQUEST_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                status_code=response.status_code
            ).inc()
            
            REQUEST_DURATION.labels(
                method=request.method,
                endpoint=request.url.path
            ).observe(duration)
            
            return response
            
        except Exception as e:
            # Record error
            ERROR_COUNT.labels(
                method=request.method,
                endpoint=request.url.path,
                error_type=type(e).__name__
            ).inc()
            
            raise
            
        finally:
            # Decrease in-progress counter
            REQUESTS_IN_PROGRESS.dec()