"""
FastAPI application main module.
"""

from fastapi import FastAPI
from config.settings import config
from interfaces.api.documents import router as documents_router

app = FastAPI(
    title=config.get_app_name(),
    version=config.get_app_version(),
    description="A clean architecture-based system for document processing and semantic retrieval"
)

# Include routers
app.include_router(documents_router)


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "message": "Welcome to Document Embedding & Retrieval System",
        "version": config.get_app_version(),
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "app_name": config.get_app_name(),
        "version": config.get_app_version()
    }


@app.get("/config")
async def get_config():
    """Get current configuration (non-sensitive data only)."""
    return {
        "app_name": config.get_app_name(),
        "version": config.get_app_version(),
        "debug": config.get_debug(),
        "embedding_model": config.get_embedding_model(),
        "vector_dimension": config.get_vector_dimension(),
        "chunk_size": config.get_chunk_size(),
        "chunk_overlap": config.get_chunk_overlap(),
        "collection_name": config.get_collection_name()
    }
