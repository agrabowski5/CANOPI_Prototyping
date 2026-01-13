"""
CANOPI Energy Planning Platform - FastAPI Backend
Main application entry point
"""

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# Initialize FastAPI app
app = FastAPI(
    title="CANOPI Energy Planning Platform API",
    description="API for grid strategy planning using CANOPI optimization",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# CORS middleware - allow ALL origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=False,  # Must be False when using wildcard
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    """Initialize services on application startup"""
    logger.info("Starting CANOPI Energy Planning Platform API")
    # TODO: Initialize database connection
    # TODO: Initialize Redis connection
    # TODO: Load network topology data


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on application shutdown"""
    logger.info("Shutting down CANOPI Energy Planning Platform API")
    # TODO: Close database connections
    # TODO: Close Redis connections


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "CANOPI Energy Planning Platform API",
        "version": "0.1.0",
        "status": "running",
        "docs": "/api/docs"
    }


@app.get("/health")
async def health_check_simple():
    """Simple health check endpoint for Docker"""
    return {"status": "healthy"}


@app.get("/api/v1/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "canopi-api",
        "version": "0.1.0"
    }


@app.post("/api/v1/log-error")
async def log_frontend_error(request: Request):
    """Receive and log errors from the frontend for debugging"""
    try:
        data = await request.json()
        logger.error(f"[FRONTEND ERROR] {data.get('message', 'Unknown error')}")
        if data.get('stack'):
            logger.error(f"[FRONTEND STACK] {data.get('stack')}")
        if data.get('componentStack'):
            logger.error(f"[FRONTEND COMPONENT] {data.get('componentStack')}")
        return {"status": "logged"}
    except Exception as e:
        logger.error(f"Failed to log frontend error: {e}")
        return {"status": "error", "message": str(e)}


# API version 1 routes
from app.api.v1 import projects, optimization, grid_data, transmission

app.include_router(
    projects.router,
    prefix="/api/v1/projects",
    tags=["projects"]
)

app.include_router(
    optimization.router,
    prefix="/api/v1/optimization",
    tags=["optimization"]
)

app.include_router(
    grid_data.router,
    prefix="/api/v1/grid",
    tags=["grid"]
)

app.include_router(
    transmission.router,
    prefix="/api/v1",
    tags=["transmission"]
)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": str(exc)
        }
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
