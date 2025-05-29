# 03. 설정 가이드

## 개요

EmbeddingAPIQuery 프로젝트는 다양한 어댑터와 설정을 지원하는 유연한 시스템입니다. 이 가이드는 시스템 설정 방법과 환경 구성을 상세히 설명합니다.

## 환경 설정

### 1. 기본 환경 파일 설정

```bash
# .env 파일 생성
cp .env.example .env
```

### 2. 필수 환경 변수

#### OpenAI API 설정
```bash
# OpenAI API 키 (필수)
OPENAI_API_KEY=your_openai_api_key_here

# 임베딩 모델 설정
OPENAI_EMBEDDING_MODEL=text-embedding-3-small
OPENAI_EMBEDDING_DIMENSION=1536
OPENAI_MAX_RETRIES=3
OPENAI_TIMEOUT=30
```

#### Qdrant 벡터 데이터베이스 설정
```bash
# Qdrant 연결 정보
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key  # 선택사항
QDRANT_TIMEOUT=30
QDRANT_PREFER_GRPC=false
```

#### 어댑터 선택 설정
```bash
# 벡터 저장소 타입 (qdrant, faiss, mock)
VECTOR_STORE_TYPE=qdrant

# 임베딩 모델 타입 (openai)
EMBEDDING_MODEL_TYPE=openai

# 문서 로더 타입 (pdf, json, web)
DOCUMENT_LOADER_TYPE=pdf

# 텍스트 청킹 타입 (recursive, semantic)
TEXT_CHUNKER_TYPE=recursive
```

### 3. 선택적 환경 변수

#### 청킹 설정
```bash
# 텍스트 청킹 설정
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
CHUNKING_STRATEGY=recursive
```

#### 검색 설정
```bash
# 기본 검색 설정
DEFAULT_TOP_K=5
DEFAULT_SCORE_THRESHOLD=0.7
SEARCH_TIMEOUT=30
```

#### 로깅 설정
```bash
# 로깅 레벨 (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO
LOG_FORMAT=json
LOG_FILE=logs/app.log
```

## 어댑터 설정

### 1. 벡터 저장소 어댑터

#### Qdrant 설정
```python
# config/settings.py
class QdrantSettings(BaseSettings):
    url: str = "http://localhost:6333"
    api_key: Optional[str] = None
    timeout: int = 30
    prefer_grpc: bool = False
    collection_name: str = "documents"
    vector_size: int = 1536
    distance: str = "Cosine"
```

#### FAISS 설정
```python
class FAISSSettings(BaseSettings):
    index_type: str = "IndexFlatIP"  # IndexFlatIP, IndexIVFFlat
    storage_path: str = "./faiss_storage"
    dimension: int = 1536
    nlist: int = 100  # IVF 인덱스용
```

#### Mock 설정 (테스트용)
```python
class MockVectorStoreSettings(BaseSettings):
    storage_path: str = "./mock_storage"
    max_vectors: int = 10000
    similarity_threshold: float = 0.7
```

### 2. 임베딩 모델 어댑터

#### OpenAI 설정
```python
class OpenAIEmbeddingSettings(BaseSettings):
    api_key: str
    model: str = "text-embedding-3-small"
    dimension: int = 1536
    batch_size: int = 100
    max_retries: int = 3
    timeout: int = 30
    rate_limit_rpm: int = 3000
    rate_limit_tpm: int = 1000000
```

### 3. 문서 로더 어댑터

#### PDF 로더 설정
```python
class PDFLoaderSettings(BaseSettings):
    loader_type: str = "pypdf2"  # pypdf2, unstructured
    extract_images: bool = False
    extract_tables: bool = True
    ocr_enabled: bool = False
```

#### JSON 로더 설정
```python
class JSONLoaderSettings(BaseSettings):
    content_field: str = "content"
    title_field: str = "title"
    metadata_fields: List[str] = ["author", "date", "source"]
    validate_schema: bool = True
```

#### 웹 스크래퍼 설정
```python
class WebScraperSettings(BaseSettings):
    user_agent: str = "EmbeddingAPIQuery/1.0"
    timeout: int = 30
    max_retries: int = 3
    follow_redirects: bool = True
    extract_links: bool = False
```

## 설정 클래스 구조

### 1. 메인 설정 클래스

```python
# config/settings.py
class Settings(BaseSettings):
    # 환경 설정
    environment: str = "development"
    debug: bool = False
    
    # API 설정
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    api_reload: bool = True
    
    # 어댑터 타입 설정
    vector_store_type: str = "qdrant"
    embedding_model_type: str = "openai"
    document_loader_type: str = "pdf"
    text_chunker_type: str = "recursive"
    
    # 하위 설정 클래스들
    openai: OpenAIEmbeddingSettings
    qdrant: QdrantSettings
    faiss: FAISSSettings
    chunking: ChunkingSettings
    retrieval: RetrievalSettings
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
```

### 2. 설정 팩토리

```python
# config/adapter_factory.py
class AdapterFactory:
    def __init__(self, config: Settings):
        self.config = config
    
    def create_vector_store(self) -> VectorStorePort:
        if self.config.vector_store_type == "qdrant":
            return QdrantVectorStore(self.config.qdrant)
        elif self.config.vector_store_type == "faiss":
            return FAISSVectorStore(self.config.faiss)
        elif self.config.vector_store_type == "mock":
            return MockVectorStore()
        else:
            raise ValueError(f"Unknown vector store type: {self.config.vector_store_type}")
    
    def create_embedding_model(self) -> EmbeddingModelPort:
        if self.config.embedding_model_type == "openai":
            return OpenAIEmbedding(self.config.openai)
        else:
            raise ValueError(f"Unknown embedding model type: {self.config.embedding_model_type}")
```

## 환경별 설정

### 1. 개발 환경 (development)

```bash
# .env.development
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG

# 로컬 Qdrant 사용
QDRANT_URL=http://localhost:6333
VECTOR_STORE_TYPE=qdrant

# 작은 청크 크기로 빠른 테스트
CHUNK_SIZE=500
CHUNK_OVERLAP=100
```

### 2. 테스트 환경 (testing)

```bash
# .env.testing
ENVIRONMENT=testing
DEBUG=true
LOG_LEVEL=WARNING

# Mock 어댑터 사용
VECTOR_STORE_TYPE=mock
EMBEDDING_MODEL_TYPE=openai

# 작은 배치 크기
OPENAI_BATCH_SIZE=10
DEFAULT_TOP_K=3
```

### 3. 운영 환경 (production)

```bash
# .env.production
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO

# 운영 Qdrant 클러스터
QDRANT_URL=https://your-qdrant-cluster.com
QDRANT_API_KEY=your_production_api_key

# 최적화된 설정
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
OPENAI_BATCH_SIZE=100
```

## 설정 검증

### 1. 설정 유효성 검사

```python
# config/validation.py
class ConfigValidator:
    @staticmethod
    def validate_openai_config(config: OpenAIEmbeddingSettings) -> bool:
        if not config.api_key:
            raise ValueError("OpenAI API key is required")
        
        if config.dimension not in [1536, 3072]:
            raise ValueError("Invalid embedding dimension")
        
        return True
    
    @staticmethod
    def validate_qdrant_config(config: QdrantSettings) -> bool:
        if not config.url:
            raise ValueError("Qdrant URL is required")
        
        if config.vector_size != 1536:
            raise ValueError("Vector size must match embedding dimension")
        
        return True
```

### 2. 연결 테스트

```python
# config/health_check.py
class HealthChecker:
    @staticmethod
    async def check_qdrant_connection(config: QdrantSettings) -> bool:
        try:
            client = QdrantClient(url=config.url, api_key=config.api_key)
            collections = await client.get_collections()
            return True
        except Exception as e:
            logger.error(f"Qdrant connection failed: {e}")
            return False
    
    @staticmethod
    async def check_openai_connection(config: OpenAIEmbeddingSettings) -> bool:
        try:
            client = OpenAI(api_key=config.api_key)
            response = await client.embeddings.create(
                model=config.model,
                input="test"
            )
            return True
        except Exception as e:
            logger.error(f"OpenAI connection failed: {e}")
            return False
```

## 설정 사용법

### 1. CLI에서 설정 사용

```python
# interfaces/cli/main.py
from config.settings import get_settings
from config.adapter_factory import AdapterFactory

def main():
    config = get_settings()
    factory = AdapterFactory(config)
    
    # 어댑터 생성
    vector_store = factory.create_vector_store()
    embedding_model = factory.create_embedding_model()
```

### 2. FastAPI에서 설정 사용

```python
# interfaces/api/main.py
from fastapi import FastAPI, Depends
from config.settings import get_settings, Settings

app = FastAPI()

@app.get("/health")
async def health_check(config: Settings = Depends(get_settings)):
    return {
        "status": "healthy",
        "environment": config.environment,
        "vector_store": config.vector_store_type,
        "embedding_model": config.embedding_model_type
    }
```

### 3. 테스트에서 설정 사용

```python
# tests/conftest.py
import pytest
from config.settings import Settings

@pytest.fixture
def test_config():
    return Settings(
        environment="testing",
        vector_store_type="mock",
        embedding_model_type="openai",
        openai=OpenAIEmbeddingSettings(
            api_key="test-key",
            model="text-embedding-3-small"
        )
    )
```

## 설정 최적화

### 1. 성능 최적화 설정

```bash
# 고성능 설정
OPENAI_BATCH_SIZE=100
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
DEFAULT_TOP_K=10
QDRANT_PREFER_GRPC=true
```

### 2. 메모리 최적화 설정

```bash
# 메모리 절약 설정
OPENAI_BATCH_SIZE=50
CHUNK_SIZE=500
CHUNK_OVERLAP=100
DEFAULT_TOP_K=5
```

### 3. 비용 최적화 설정

```bash
# API 비용 절약 설정
OPENAI_BATCH_SIZE=200
OPENAI_MAX_RETRIES=1
CHUNK_SIZE=1500
DEFAULT_TOP_K=3
```

## 문제 해결

### 1. 일반적인 설정 문제

#### API 키 오류
```bash
# 환경 변수 확인
echo $OPENAI_API_KEY

# .env 파일 확인
cat .env | grep OPENAI_API_KEY
```

#### 연결 오류
```bash
# Qdrant 연결 테스트
curl http://localhost:6333/collections

# 포트 확인
netstat -an | grep 6333
```

### 2. 설정 디버깅

```python
# 현재 설정 출력
from config.settings import get_settings

config = get_settings()
print(f"Vector Store: {config.vector_store_type}")
print(f"Embedding Model: {config.embedding_model_type}")
print(f"Qdrant URL: {config.qdrant.url}")
```

### 3. 설정 검증 스크립트

```python
# scripts/validate_config.py
async def validate_all_configs():
    config = get_settings()
    
    # OpenAI 연결 테스트
    openai_ok = await HealthChecker.check_openai_connection(config.openai)
    print(f"OpenAI: {'✅' if openai_ok else '❌'}")
    
    # Qdrant 연결 테스트
    qdrant_ok = await HealthChecker.check_qdrant_connection(config.qdrant)
    print(f"Qdrant: {'✅' if qdrant_ok else '❌'}")
    
    return openai_ok and qdrant_ok
```

이 설정 가이드를 통해 시스템을 다양한 환경에서 효과적으로 구성하고 운영할 수 있습니다.
