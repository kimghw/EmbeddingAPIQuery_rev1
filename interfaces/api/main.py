"""
FastAPI interface for Document Embedding & Retrieval System.
"""

from fastapi import FastAPI
from config.settings import config


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    
    app = FastAPI(
        title=config.get_app_name(),
        description="A clean architecture-based system for document processing and semantic retrieval",
        version=config.get_app_version(),
        debug=config.get_debug()
    )
    
    @app.get("/")
    async def root():
        return {
            "message": "Document Embedding & Retrieval System",
            "version": config.get_app_version(),
            "status": "running"
        }
    
    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "app_name": config.get_app_name(),
            "version": config.get_app_version()
        }
    
    @app.get("/config")
    async def get_config():
        """Get current configuration (safe values only)."""
        return {
            "app_name": config.get_app_name(),
            "app_version": config.get_app_version(),
            "debug": config.get_debug(),
            "embedding_model": config.get_embedding_model(),
            "vector_dimension": config.get_vector_dimension(),
            "chunk_size": config.get_chunk_size(),
            "chunk_overlap": config.get_chunk_overlap(),
            "collection_name": config.get_collection_name()
        }
    
    return app
