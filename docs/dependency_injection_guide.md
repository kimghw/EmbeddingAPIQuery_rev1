# 의존성 주입 설정 가이드

## 개요

이 문서는 Document Embedding & Retrieval System의 의존성 주입(Dependency Injection) 설정 방법과 사용법을 설명합니다.

## 1. 설정 기반 의존성 주입

### 1.1 환경 변수 설정

`.env` 파일에서 다음 환경 변수들을 설정하여 어댑터 타입을 선택할 수 있습니다:

```bash
# 의존성 주입 설정
VECTOR_STORE_TYPE=qdrant        # qdrant, faiss, mock
EMBEDDING_TYPE=openai           # openai, huggingface (future)
DOCUMENT_LOADER_TYPE=pdf        # pdf, json, web_scraper, unstructured
TEXT_CHUNKER_TYPE=recursive     # recursive, semantic
RETRIEVER_TYPE=simple           # simple, ensemble

# LLM 설정
LLM_MODEL_TYPE=openai           # openai, anthropic (future), cohere (future)
LLM_MODEL_NAME=gpt-3.5-turbo    # gpt-3.5-turbo, gpt-4, gpt-4-turbo
LLM_TEMPERATURE=0.7             # 0.0 to 1.0
LLM_MAX_TOKENS=1000             # 최대 토큰 수
```

### 1.2 설정 포트/어댑터 패턴

```python
from config.settings import ConfigPort, ConfigAdapter, TestConfig

# 설정 어댑터 생성
config = ConfigAdapter(TestConfig())

# 설정 값 조회
vector_store_type = config.get_vector_store_type()
embedding_type = config.get_embedding_type()
llm_model_name = config.get_llm_model_name()
```

## 2. AdapterFactory 사용법

### 2.1 개별 어댑터 생성

```python
from config.adapter_factory import AdapterFactory

# 벡터 저장소 어댑터
vector_store = AdapterFactory.create_vector_store_adapter("qdrant")
faiss_store = AdapterFactory.create_vector_store_adapter("faiss")
mock_store = AdapterFactory.create_vector_store_adapter("mock")

# 임베딩 어댑터
embedding = AdapterFactory.create_embedding_adapter("openai", config)

# 문서 로더 어댑터
pdf_loader = AdapterFactory.create_document_loader_adapter("pdf")
json_loader = AdapterFactory.create_document_loader_adapter("json")
web_loader = AdapterFactory.create_document_loader_adapter("web_scraper")

# 텍스트 청킹 어댑터
recursive_chunker = AdapterFactory.create_text_chunker_adapter("recursive")
semantic_chunker = AdapterFactory.create_text_chunker_adapter("semantic")

# 리트리버 어댑터
simple_retriever = AdapterFactory.create_retriever_adapter(
    "simple", vector_store, embedding
)
```

### 2.2 설정 기반 어댑터 생성

```python
from config.adapter_factory import (
    get_vector_store_adapter,
    get_embedding_adapter,
    get_document_loader_adapter,
    get_text_chunker_adapter,
    get_retriever_adapter
)

# 설정에서 자동으로 타입을 읽어서 생성
vector_store = get_vector_store_adapter(config)
embedding = get_embedding_adapter(config)
document_loader = get_document_loader_adapter(config)
text_chunker = get_text_chunker_adapter(config)
retriever = get_retriever_adapter(config)
```

## 3. DependencyContainer 사용법

### 3.1 싱글톤 패턴

```python
from config.adapter_factory import DependencyContainer
from config.settings import ConfigAdapter, TestConfig

# 컨테이너 생성
config = ConfigAdapter(TestConfig())
container = DependencyContainer(config)

# 싱글톤 인스턴스 조회
vector_store = container.vector_store      # 첫 번째 호출 시 생성
vector_store2 = container.vector_store     # 동일한 인스턴스 반환

embedding = container.embedding_model
document_loader = container.document_loader
text_chunker = container.text_chunker
retriever = container.retriever
```

### 3.2 컨테이너 리셋

```python
# 모든 인스턴스 초기화 (테스트용)
container.reset()

# 리셋 후 새로운 인스턴스 생성
new_vector_store = container.vector_store  # 새 인스턴스
```

### 3.3 전역 컨테이너

```python
from config.adapter_factory import container

# 전역 컨테이너 사용 (설정 기반 자동 초기화)
vector_store = container.vector_store
embedding = container.embedding_model
```

## 4. 환경별 설정

### 4.1 개발 환경

```python
from config.settings import ConfigAdapter, DevelopmentConfig

config = ConfigAdapter(DevelopmentConfig())
print(f"Debug: {config.get_debug()}")        # True
print(f"Log Level: {config.get_log_level()}") # DEBUG
```

### 4.2 테스트 환경

```python
from config.settings import ConfigAdapter, TestConfig

config = ConfigAdapter(TestConfig())
print(f"Debug: {config.get_debug()}")        # True
print(f"OpenAI Key: {config.get_openai_api_key()}")  # test-key
```

### 4.3 운영 환경

```python
from config.settings import ConfigAdapter, ProductionConfig

config = ConfigAdapter(ProductionConfig())
print(f"Debug: {config.get_debug()}")        # False
print(f"Log Level: {config.get_log_level()}") # INFO
```

## 5. 어댑터 전환 예제

### 5.1 벡터 저장소 전환

```python
# Qdrant에서 FAISS로 전환
os.environ["VECTOR_STORE_TYPE"] = "faiss"
container.reset()
faiss_store = container.vector_store  # FaissVectorStoreAdapter

# Mock으로 전환 (테스트용)
os.environ["VECTOR_STORE_TYPE"] = "mock"
container.reset()
mock_store = container.vector_store   # MockVectorStoreAdapter
```

### 5.2 리트리버 전환

```python
# Simple에서 Ensemble로 전환
os.environ["RETRIEVER_TYPE"] = "ensemble"
container.reset()
ensemble_retriever = container.retriever  # EnsembleRetrieverAdapter
```

### 5.3 텍스트 청킹 전환

```python
# Recursive에서 Semantic으로 전환
os.environ["TEXT_CHUNKER_TYPE"] = "semantic"
container.reset()
semantic_chunker = container.text_chunker  # SemanticTextChunkerAdapter
```

## 6. 유스케이스에서 사용법

### 6.1 DocumentProcessing 유스케이스

```python
from core.usecases.document_processing import DocumentProcessingUseCase
from config.adapter_factory import container

# 의존성 주입
usecase = DocumentProcessingUseCase(
    document_loader=container.document_loader,
    text_chunker=container.text_chunker,
    embedding_model=container.embedding_model,
    vector_store=container.vector_store
)

# 문서 처리
result = await usecase.process_document("document.pdf")
```

### 6.2 DocumentRetrieval 유스케이스

```python
from core.usecases.document_retrieval import DocumentRetrievalUseCase
from config.adapter_factory import container

# 의존성 주입
usecase = DocumentRetrievalUseCase(
    retriever=container.retriever
)

# 문서 검색
results = await usecase.search_documents("query", top_k=5)
```

## 7. 테스트에서 사용법

### 7.1 Mock 어댑터 사용

```python
def test_with_mock_adapters():
    # 테스트용 설정
    config = ConfigAdapter(TestConfig())
    
    # Mock 어댑터 생성
    mock_vector_store = AdapterFactory.create_vector_store_adapter("mock")
    
    # 테스트 실행
    # ...
```

### 7.2 컨테이너 리셋

```python
def test_with_container_reset():
    # 테스트 전 컨테이너 리셋
    container.reset()
    
    # 새로운 설정으로 테스트
    os.environ["VECTOR_STORE_TYPE"] = "mock"
    mock_store = container.vector_store
    
    # 테스트 실행
    # ...
```

## 8. 장점

### 8.1 유연성
- 환경 변수만 변경하여 어댑터 전환 가능
- 런타임에 동적 어댑터 변경 지원

### 8.2 테스트 용이성
- Mock 어댑터로 쉬운 단위 테스트
- 컨테이너 리셋으로 격리된 테스트

### 8.3 확장성
- 새로운 어댑터 타입 쉽게 추가
- 기존 코드 수정 없이 확장 가능

### 8.4 성능
- 싱글톤 패턴으로 인스턴스 재사용
- 지연 로딩으로 필요시에만 생성

## 9. 주의사항

### 9.1 환경 변수 검증
- 잘못된 어댑터 타입 설정 시 ValueError 발생
- 운영 환경에서는 필수 설정 검증 필요

### 9.2 순환 의존성
- 어댑터 간 순환 의존성 주의
- 포트/어댑터 패턴으로 의존성 방향 관리

### 9.3 스레드 안전성
- 현재 구현은 단일 스레드 환경 가정
- 멀티 스레드 환경에서는 추가 동기화 필요

이 가이드를 통해 의존성 주입 설정을 효과적으로 활용하여 유연하고 테스트 가능한 시스템을 구축할 수 있습니다.
