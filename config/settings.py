"""
Configuration settings for Document Embedding & Retrieval System.
Implements port/adapter pattern for configuration management.
"""

from abc import ABC, abstractmethod
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field
from pydantic_settings import BaseSettings as PydanticBaseSettings
import os


class ConfigPort(ABC):
    """Port interface for configuration management."""
    
    @abstractmethod
    def get_openai_api_key(self) -> str:
        pass
    
    @abstractmethod
    def get_qdrant_url(self) -> str:
        pass
    
    @abstractmethod
    def get_qdrant_api_key(self) -> Optional[str]:
        pass
    
    @abstractmethod
    def get_app_name(self) -> str:
        pass
    
    @abstractmethod
    def get_app_version(self) -> str:
        pass
    
    @abstractmethod
    def get_debug(self) -> bool:
        pass
    
    @abstractmethod
    def get_host(self) -> str:
        pass
    
    @abstractmethod
    def get_port(self) -> int:
        pass
    
    @abstractmethod
    def get_log_level(self) -> str:
        pass
    
    @abstractmethod
    def get_vector_dimension(self) -> int:
        pass
    
    @abstractmethod
    def get_collection_name(self) -> str:
        pass
    
    @abstractmethod
    def get_embedding_model(self) -> str:
        pass
    
    @abstractmethod
    def get_chunk_size(self) -> int:
        pass
    
    @abstractmethod
    def get_chunk_overlap(self) -> int:
        pass


class BaseConfig(PydanticBaseSettings):
    """Base configuration class."""
    
    # Environment
    environment: str = Field(default="development", env="ENVIRONMENT")
    
    # OpenAI Configuration
    openai_api_key: str = Field(..., env="OPENAI_API_KEY")
    
    # Qdrant Configuration
    qdrant_url: str = Field(default="http://localhost:6333", env="QDRANT_URL")
    qdrant_api_key: Optional[str] = Field(default=None, env="QDRANT_API_KEY")
    
    # Application Configuration
    app_name: str = Field(default="Document Embedding & Retrieval System", env="APP_NAME")
    app_version: str = Field(default="1.0.0", env="APP_VERSION")
    debug: bool = Field(default=True, env="DEBUG")
    
    # Server Configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    
    # Logging Configuration
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_format: str = Field(default="json", env="LOG_FORMAT")
    
    # Vector Store Configuration
    vector_dimension: int = Field(default=1536, env="VECTOR_DIMENSION")
    collection_name: str = Field(default="documents", env="COLLECTION_NAME")
    
    # Embedding Configuration
    embedding_model: str = Field(default="text-embedding-3-small", env="EMBEDDING_MODEL")
    chunk_size: int = Field(default=1000, env="CHUNK_SIZE")
    chunk_overlap: int = Field(default=200, env="CHUNK_OVERLAP")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    debug: bool = True
    log_level: str = "DEBUG"


class ProductionConfig(BaseConfig):
    """Production environment configuration."""
    debug: bool = False
    log_level: str = "INFO"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        
        @classmethod
        def validate_production_settings(cls, values):
            """Validate required settings for production."""
            required_fields = ["openai_api_key"]
            for field in required_fields:
                if not values.get(field):
                    raise ValueError(f"{field} is required in production environment")
            return values


class TestConfig(BaseConfig):
    """Test environment configuration."""
    debug: bool = True
    log_level: str = "DEBUG"
    openai_api_key: str = "test-key"
    qdrant_url: str = "http://localhost:6333"


class ConfigAdapter(ConfigPort):
    """Adapter implementation for configuration management."""
    
    def __init__(self, config: BaseConfig):
        self._config = config
    
    def get_openai_api_key(self) -> str:
        return self._config.openai_api_key
    
    def get_qdrant_url(self) -> str:
        return self._config.qdrant_url
    
    def get_qdrant_api_key(self) -> Optional[str]:
        return self._config.qdrant_api_key
    
    def get_app_name(self) -> str:
        return self._config.app_name
    
    def get_app_version(self) -> str:
        return self._config.app_version
    
    def get_debug(self) -> bool:
        return self._config.debug
    
    def get_host(self) -> str:
        return self._config.host
    
    def get_port(self) -> int:
        return self._config.port
    
    def get_log_level(self) -> str:
        return self._config.log_level
    
    def get_vector_dimension(self) -> int:
        return self._config.vector_dimension
    
    def get_collection_name(self) -> str:
        return self._config.collection_name
    
    def get_embedding_model(self) -> str:
        return self._config.embedding_model
    
    def get_chunk_size(self) -> int:
        return self._config.chunk_size
    
    def get_chunk_overlap(self) -> int:
        return self._config.chunk_overlap


def create_config() -> ConfigPort:
    """Factory function to create appropriate configuration based on environment."""
    environment = os.getenv("ENVIRONMENT", "development").lower()
    
    if environment == "production":
        config = ProductionConfig()
    elif environment == "test":
        config = TestConfig()
    else:
        config = DevelopmentConfig()
    
    return ConfigAdapter(config)


# Global configuration instance
config = create_config()
