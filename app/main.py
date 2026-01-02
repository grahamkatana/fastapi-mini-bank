from fastapi import FastAPI
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response
from app.core.logging_config import setup_logging, logger
from app.middleware.logging_middleware import LoggingMiddleware
from app.middleware.metrics_middleware import MetricsMiddleware
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import engine, Base
from app.api import api_router

# Create database tables
Base.metadata.create_all(bind=engine)
setup_logging(log_level="INFO")

# Initialize FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    description="FastAPI project with JWT Auth, MySQL, and Celery with Redis, Dockerized and kubernetes-ready.",
    version="1.0.0",
    docs_url="/docs",
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(LoggingMiddleware)
app.add_middleware(MetricsMiddleware)

logger.info("Application starting up")


# Include API router
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    logger.info("Health check endpoint called")
    return {"status": "healthy", "service": "fastapi-mini-bank"}

@app.get("/metrics")
async def metrics():
    """Prometheus metrics endpoint."""
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST
    )


@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}
