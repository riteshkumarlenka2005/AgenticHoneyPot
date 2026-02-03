"""Main FastAPI application."""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.api.routes import conversations, intelligence, analytics, personas, mock_scammer, messages

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous AI honeypot system for scam detection and intelligence extraction"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(messages.router, prefix=f"{settings.API_V1_PREFIX}/messages", tags=["messages"])
app.include_router(conversations.router, prefix=f"{settings.API_V1_PREFIX}/conversations", tags=["conversations"])
app.include_router(intelligence.router, prefix=f"{settings.API_V1_PREFIX}/intelligence", tags=["intelligence"])
app.include_router(analytics.router, prefix=f"{settings.API_V1_PREFIX}/analytics", tags=["analytics"])
app.include_router(personas.router, prefix=f"{settings.API_V1_PREFIX}/personas", tags=["personas"])
app.include_router(mock_scammer.router, prefix=f"{settings.API_V1_PREFIX}/mock-scammer", tags=["mock-scammer"])


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
