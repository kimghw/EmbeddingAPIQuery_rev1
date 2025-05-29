# Mock 클래스에서 실제 구현체로 전환 가이드

## 문제 상황 분석

### Mock 클래스 사용의 원인
1. **개발 초기 단계**: 실제 구현체가 아직 완성되지 않은 상태
2. **빠른 프로토타이핑**: API 구조를 먼저 만들고 나중에 실제 구현
3. **외부 의존성 회피**: 데이터베이스, 외부 API 등이 준비되지 않은 상태
4. **테스트 용이성**: 단위 테스트를 위한 격리된 환경

### 이번 사례의 문제점
```python
# ❌ 문제가 된 코드 (interfaces/api/email_search_routes.py)
class MockEmbeddingModel:
    def __init__(self):
        self.model_name = "mock-embedding-model"
        # ... mock 구현

class MockConfig:
    def get_openai_api_key(self) -> str:
        return "mock-api-key"
    # ... mock 구현

# 의존성 주입에서 Mock 사용
async def get_email_retriever() -> EmailRetrievalUseCase:
    embedding_model = MockEmbeddingModel()  # ❌ Mock 사용
    config = MockConfig()                   # ❌ Mock 사용
```

## 해결 방안

### 1. 어댑터 팩토리 패턴 활용
```python
# ✅ 올바른 방법
from config.adapter_factory import get_embedding_model, get_vector_store, get_retriever
from config.settings import config

async def get_email_retriever() -> EmailRetrievalUseCase:
    embedding_model = get_embedding_model()  # ✅ 팩토리 사용
    vector_store = get_vector_store()        # ✅ 팩토리 사용
    retriever = get_retriever()              # ✅ 팩토리 사용
    # config는 전역 인스턴스 사용           # ✅ 실제 설정 사용
```

### 2. 환경별 설정을 통한 자동 전환
```python
# config/adapter_factory.py
def get_embedding_model():
    config = get_settings()
    embedding_type = config.get_embedding_type()
    
    if embedding_type == "mock":
        return MockEmbeddingModel()
    elif embedding_type == "openai":
        return OpenAIEmbeddingModel(config)
    else:
        raise ValueError(f"Unknown embedding type: {embedding_type}")
```

## Mock 사용 시점과 전환 전략

### 1. 개발 단계별 전환 시점

#### Phase 1: 초기 개발 (Mock 사용)
- **시점**: API 구조 설계 및 프로토타이핑
- **사용**: 모든 외부 의존성을 Mock으로 대체
- **목적**: 빠른 개발과 테스트

#### Phase 2: 부분 통합 (혼합 사용)
- **시점**: 일부 구현체가 완성된 상태
- **사용**: 완성된 것은 실제 구현체, 미완성은 Mock
- **목적**: 점진적 통합

#### Phase 3: 완전 통합 (실제 구현체)
- **시점**: 모든 구현체가 완성된 상태
- **사용**: 실제 구현체만 사용
- **목적**: 프로덕션 준비

### 2. 전환 체크리스트

#### ✅ Mock에서 실제 구현체로 전환해야 하는 시점
1. **실제 구현체가 완성되었을 때**
2. **통합 테스트를 시작할 때**
3. **프로덕션 배포 전**
4. **성능 테스트가 필요할 때**

#### ⚠️ Mock을 계속 사용해야 하는 경우
1. **단위 테스트 환경**
2. **CI/CD 파이프라인에서 외부 의존성 없이 테스트**
3. **개발 환경에서 외부 서비스 비용 절약**

### 3. 자동화된 전환 방법

#### 환경변수를 통한 제어
```bash
# .env 파일
ENVIRONMENT=development
EMBEDDING_TYPE=mock          # 개발 시
# EMBEDDING_TYPE=openai      # 프로덕션 시
VECTOR_STORE_TYPE=mock       # 개발 시
# VECTOR_STORE_TYPE=qdrant   # 프로덕션 시
```

#### 설정 기반 팩토리 패턴
```python
# config/adapter_factory.py
def get_embedding_model():
    settings = get_settings()
    
    if settings.get_environment() == "test":
        return MockEmbeddingModel()
    elif settings.get_embedding_type() == "openai":
        return OpenAIEmbeddingModel(settings)
    else:
        return MockEmbeddingModel()  # 기본값
```

## 예방 방법

### 1. 명확한 네이밍 컨벤션
```python
# ❌ 나쁜 예
class EmbeddingModel:  # Mock인지 실제인지 불분명

# ✅ 좋은 예
class MockEmbeddingModel:     # Mock임을 명시
class OpenAIEmbeddingModel:   # 실제 구현체임을 명시
```

### 2. 디렉토리 구조로 분리
```
adapters/
├── embedding/
│   ├── openai_embedding.py      # 실제 구현체
│   └── mock_embedding.py        # Mock 구현체
├── vector_store/
│   ├── qdrant_vector_store.py   # 실제 구현체
│   └── mock_vector_store.py     # Mock 구현체
```

### 3. 문서화와 주석
```python
# interfaces/api/email_search_routes.py
async def get_email_retriever() -> EmailRetrievalUseCase:
    """
    Get email retrieval use case with dependencies.
    
    Note: 이 함수는 실제 어댑터 팩토리를 사용해야 합니다.
    Mock 클래스를 직접 사용하지 마세요.
    """
    # ✅ 어댑터 팩토리 사용 (환경에 따라 자동 선택)
    embedding_model = get_embedding_model()
    vector_store = get_vector_store()
    retriever = get_retriever()
```

### 4. 코드 리뷰 체크포인트
- [ ] Mock 클래스가 직접 인스턴스화되고 있는가?
- [ ] 어댑터 팩토리 패턴을 사용하고 있는가?
- [ ] 환경별 설정이 올바르게 적용되고 있는가?
- [ ] 프로덕션 환경에서 Mock이 사용되지 않는가?

### 5. 자동화된 검증
```python
# tests/test_production_readiness.py
def test_no_mock_in_production():
    """프로덕션 환경에서 Mock 사용 여부 검증"""
    os.environ["ENVIRONMENT"] = "production"
    
    embedding_model = get_embedding_model()
    assert not isinstance(embedding_model, MockEmbeddingModel)
    
    vector_store = get_vector_store()
    assert not isinstance(vector_store, MockVectorStore)
```

## 권장 워크플로우

### 1. 개발 시작
```python
# 1. Mock으로 시작
class MockEmailService:
    pass

# 2. 인터페이스 정의
class EmailServicePort(ABC):
    pass

# 3. Mock이 인터페이스 구현
class MockEmailService(EmailServicePort):
    pass
```

### 2. 실제 구현체 개발
```python
# 4. 실제 구현체 개발
class QdrantEmailService(EmailServicePort):
    pass
```

### 3. 팩토리 패턴 적용
```python
# 5. 팩토리에서 환경별 선택
def get_email_service():
    if get_environment() == "test":
        return MockEmailService()
    else:
        return QdrantEmailService()
```

### 4. 점진적 전환
```python
# 6. 환경변수로 제어
EMAIL_SERVICE_TYPE=mock    # 개발/테스트
EMAIL_SERVICE_TYPE=qdrant  # 프로덕션
```

이렇게 하면 Mock 클래스가 프로덕션에 남아있는 문제를 예방할 수 있습니다.
