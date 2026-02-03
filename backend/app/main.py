"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import settings
from .api.routes import conversations, intelligence, analytics, personas, mock_scammer
from .db.database import engine, Base
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

# Create database tables
try:
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
except Exception as e:
    logger.error(f"Error creating database tables: {e}")

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous AI Honeypot for Scam Detection & Intelligence Extraction"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    conversations.router,
    prefix=f"{settings.API_V1_PREFIX}/conversations",
    tags=["conversations"]
)
app.include_router(
    intelligence.router,
    prefix=f"{settings.API_V1_PREFIX}/intelligence",
    tags=["intelligence"]
)
app.include_router(
    analytics.router,
    prefix=f"{settings.API_V1_PREFIX}/analytics",
    tags=["analytics"]
)
app.include_router(
    personas.router,
    prefix=f"{settings.API_V1_PREFIX}/personas",
    tags=["personas"]
)
app.include_router(
    mock_scammer.router,
    prefix=f"{settings.API_V1_PREFIX}/mock-scammer",
    tags=["mock-scammer"]
)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
