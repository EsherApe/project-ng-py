import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.app.core.config import settings
from backend.app.db.init_db import init_db
from backend.app.api.auth import router as auth_router
from backend.app.api.users import router as users_router
from backend.app.middlewares.token_middleware import TokenRefreshMiddleware

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("app")

# Startup and shutdown events
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run startup code
    logger.info("Initializing application...")
    init_db()
    logger.info("Database initialized")
    yield
    # Run shutdown code
    logger.info("Shutting down application...")

# Create FastAPI application
app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Authentication Service API",
    version="0.1.0",
    lifespan=lifespan,
)

# Add custom middleware
app.add_middleware(TokenRefreshMiddleware)

# Setup CORS
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(users_router, prefix=settings.API_V1_STR)

@app.get("/")
async def root():
    """
    Root endpoint to check if the API is running
    """
    return {
        "status": "online",
        "message": f"Welcome to {settings.PROJECT_NAME}!",
        "version": "0.1.0",
        "docs": "/docs",
    }

@app.get("/health")
async def health_check():
    """
    Health check endpoint
    """
    return {"status": "healthy"}

# Run the application with uvicorn
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)