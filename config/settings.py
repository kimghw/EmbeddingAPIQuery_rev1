"""
Configuration settings for Document Embedding & Retrieval System.
Implements port/adapter pattern for configuration management.
"""

from abc import ABC, abstractmethod
from typing import Optional, List
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
    
    # Dependency Injection Configuration
    @abstractmethod
    def get_vector_store_type(self) -> str:
        pass
    
    @abstractmethod
    def get_embedding_type(self) -> str:
        pass
    
    @abstractmethod
    def get_document_loader_type(self) -> str:
        pass
    
    @abstractmethod
    def get_text_chunker_type(self) -> str:
        pass
    
    @abstractmethod
    def get_retriever_type(self) -> str:
        pass
    
    @abstractmethod
    def get_llm_model_type(self) -> str:
        pass
    
    @abstractmethod
    def get_llm_model_name(self) -> str:
        pass
    
    @abstractmethod
    def get_llm_temperature(self) -> float:
        pass
    
    @abstractmethod
    def get_llm_max_tokens(self) -> int:
        pass
    
    # Upload Configuration
    @abstractmethod
    def get_upload_max_file_size(self) -> int:
        pass
    
    @abstractmethod
    def get_upload_allowed_extensions(self) -> List[str]:
        pass
    
    @abstractmethod
    def get_upload_directory(self) -> str:
        pass
    
    @abstractmethod
    def get_upload_temp_directory(self) -> str:
        pass
    
    # Advanced Chunking Configuration
    @abstractmethod
    def get_semantic_chunk_min_size(self) -> int:
        pass
    
    @abstractmethod
    def get_semantic_chunk_max_size(self) -> int:
        pass
    
    @abstractmethod
    def get_semantic_similarity_threshold(self) -> float:
        pass
    
    # Retrieval Configuration
    @abstractmethod
    def get_retrieval_top_k(self) -> int:
        pass
    
    @abstractmethod
    def get_retrieval_score_threshold(self) -> float:
        pass
    
    # Ensemble Retriever Configuration
    @abstractmethod
    def get_ensemble_weights(self) -> List[float]:
        pass
    
    @abstractmethod
    def get_ensemble_search_types(self) -> List[str]:
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
    
    # Dependency Injection Configuration
    vector_store_type: str = Field(default="qdrant", env="VECTOR_STORE_TYPE")
    embedding_type: str = Field(default="openai", env="EMBEDDING_TYPE")
    document_loader_type: str = Field(default="pdf", env="DOCUMENT_LOADER_TYPE")
    text_chunker_type: str = Field(default="recursive", env="TEXT_CHUNKER_TYPE")
    retriever_type: str = Field(default="simple", env="RETRIEVER_TYPE")
    
    # LLM Configuration
    llm_model_type: str = Field(default="openai", env="LLM_MODEL_TYPE")
    llm_model_name: str = Field(default="gpt-3.5-turbo", env="LLM_MODEL_NAME")
    llm_temperature: float = Field(default=0.7, env="LLM_TEMPERATURE")
    llm_max_tokens: int = Field(default=1000, env="LLM_MAX_TOKENS")
    
    # Upload Configuration
    upload_max_file_size: int = Field(default=50*1024*1024, env="UPLOAD_MAX_FILE_SIZE")  # 50MB
    upload_allowed_extensions: str = Field(default="pdf,txt,json,docx,html", env="UPLOAD_ALLOWED_EXTENSIONS")
    upload_directory: str = Field(default="uploads", env="UPLOAD_DIRECTORY")
    upload_temp_directory: str = Field(default="temp", env="UPLOAD_TEMP_DIRECTORY")
    
    # Advanced Chunking Configuration
    semantic_chunk_min_size: int = Field(default=100, env="SEMANTIC_CHUNK_MIN_SIZE")
    semantic_chunk_max_size: int = Field(default=2000, env="SEMANTIC_CHUNK_MAX_SIZE")
    semantic_similarity_threshold: float = Field(default=0.8, env="SEMANTIC_SIMILARITY_THRESHOLD")
    
    # Retrieval Configuration
    retrieval_top_k: int = Field(default=5, env="RETRIEVAL_TOP_K")
    retrieval_score_threshold: float = Field(default=0.7, env="RETRIEVAL_SCORE_THRESHOLD")
    
    # Ensemble Retriever Configuration
    ensemble_weights: str = Field(default="0.5,0.5", env="ENSEMBLE_WEIGHTS")
    ensemble_search_types: str = Field(default="similarity,mmr", env="ENSEMBLE_SEARCH_TYPES")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


class DevelopmentConfig(BaseConfig):
    """Development environment configuration."""
    debug: bool = True
    log_level: str = "DEBUG"
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Override log_level for development
        self.log_level = "DEBUG"


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
    upload_max_file_size: int = 10*1024*1024  # 10MB for testing
    
    def __init__(self, **kwargs):
        # TestConfig에서는 환경변수를 무시하고 고정값 사용
        super().__init__(**kwargs)
        self.openai_api_key = "test-key"
        self.log_level = "DEBUG"
        self.upload_max_file_size = 10*1024*1024
    
    class Config:
        # Test 환경에서는 .env 파일을 읽지 않음
        env_file = None


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
    
    # Dependency Injection Configuration
    def get_vector_store_type(self) -> str:
        return self._config.vector_store_type
    
    def get_embedding_type(self) -> str:
        return self._config.embedding_type
    
    def get_document_loader_type(self) -> str:
        return self._config.document_loader_type
    
    def get_text_chunker_type(self) -> str:
        return self._config.text_chunker_type
    
    def get_retriever_type(self) -> str:
        return self._config.retriever_type
    
    def get_llm_model_type(self) -> str:
        return self._config.llm_model_type
    
    def get_llm_model_name(self) -> str:
        return self._config.llm_model_name
    
    def get_llm_temperature(self) -> float:
        return self._config.llm_temperature
    
    def get_llm_max_tokens(self) -> int:
        return self._config.llm_max_tokens
    
    # Upload Configuration
    def get_upload_max_file_size(self) -> int:
        return self._config.upload_max_file_size
    
    def get_upload_allowed_extensions(self) -> List[str]:
        return [ext.strip() for ext in self._config.upload_allowed_extensions.split(",")]
    
    def get_upload_directory(self) -> str:
        return self._config.upload_directory
    
    def get_upload_temp_directory(self) -> str:
        return self._config.upload_temp_directory
    
    # Advanced Chunking Configuration
    def get_semantic_chunk_min_size(self) -> int:
        return self._config.semantic_chunk_min_size
    
    def get_semantic_chunk_max_size(self) -> int:
        return self._config.semantic_chunk_max_size
    
    def get_semantic_similarity_threshold(self) -> float:
        return self._config.semantic_similarity_threshold
    
    # Retrieval Configuration
    def get_retrieval_top_k(self) -> int:
        return self._config.retrieval_top_k
    
    def get_retrieval_score_threshold(self) -> float:
        return self._config.retrieval_score_threshold
    
    # Ensemble Retriever Configuration
    def get_ensemble_weights(self) -> List[float]:
        return [float(w.strip()) for w in self._config.ensemble_weights.split(",")]
    
    def get_ensemble_search_types(self) -> List[str]:
        return [t.strip() for t in self._config.ensemble_search_types.split(",")]


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
