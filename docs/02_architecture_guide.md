# 02. 아키텍처 가이드

## 개요

EmbeddingAPIQuery 프로젝트는 클린 아키텍처(Clean Architecture)와 포트/어댑터 패턴을 기반으로 설계되었습니다. 이 문서는 프로젝트의 전체 아키텍처와 설계 원칙을 설명합니다.

## 아키텍처 원칙

### 1. 클린 아키텍처 (Clean Architecture)

```
┌─────────────────────────────────────────────────────────────┐
│                        Interfaces                           │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   FastAPI       │  │      CLI        │  │   Webhooks   │ │
│  │   Routes        │  │   Commands      │  │              │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                        Adapters                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Vector Store  │  │   Embedding     │  │   Document   │ │
│  │   (Qdrant)      │  │   (OpenAI)      │  │   Loaders    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
┌─────────────────────────────────────────────────────────────┐
│                         Core                               │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Use Cases     │  │    Entities     │  │    Ports     │ │
│  │                 │  │                 │  │ (Interfaces) │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2. 의존성 방향

- **외부 → 내부**: 모든 의존성은 외부에서 내부로 향합니다
- **Core 독립성**: Core 레이어는 외부 구현에 의존하지 않습니다
- **인터페이스 기반**: 추상화(Ports)를 통해 의존성을 관리합니다

## 폴더 구조

```
project/
├── core/                    # 비즈니스 로직 (의존성 없음)
│   ├── entities/           # 도메인 엔티티
│   ├── ports/              # 인터페이스 정의
│   ├── usecases/           # 비즈니스 유스케이스
│   └── services/           # 도메인 서비스
├── adapters/               # 외부 시스템 연동
│   ├── vector_store/       # 벡터 DB 어댑터
│   ├── embedding/          # 임베딩 모델 어댑터
│   ├── pdf/               # 문서 로더 어댑터
│   └── email/             # 이메일 처리 어댑터
├── interfaces/             # 진입점 (얇은 레이어)
│   ├── api/               # FastAPI 라우터
│   └── cli/               # CLI 명령어
├── config/                 # 설정 관리
├── schemas/               # API 스키마
└── tests/                 # 테스트
```

## 핵심 컴포넌트

### 1. Core Layer

#### Entities (엔티티)
- **Document**: 문서 도메인 엔티티
- **Email**: 이메일 도메인 엔티티
- **Embedding**: 임베딩 벡터 엔티티
- **SearchResult**: 검색 결과 엔티티

#### Ports (포트/인터페이스)
- **DocumentLoaderPort**: 문서 로딩 인터페이스
- **EmbeddingModelPort**: 임베딩 생성 인터페이스
- **VectorStorePort**: 벡터 저장소 인터페이스
- **EmailLoaderPort**: 이메일 로딩 인터페이스

#### Use Cases (유스케이스)
- **DocumentProcessingUseCase**: 문서 처리 비즈니스 로직
- **DocumentRetrievalUseCase**: 문서 검색 비즈니스 로직
- **EmailProcessingUseCase**: 이메일 처리 비즈니스 로직

### 2. Adapters Layer

#### Vector Store Adapters
- **QdrantVectorStore**: Qdrant 벡터 DB 구현
- **FAISSVectorStore**: FAISS 벡터 DB 구현
- **MockVectorStore**: 테스트용 Mock 구현

#### Embedding Adapters
- **OpenAIEmbedding**: OpenAI 임베딩 모델 구현
- **TextChunker**: 텍스트 청킹 구현

#### Document Loader Adapters
- **PDFLoader**: PDF 문서 로더
- **JSONLoader**: JSON 문서 로더
- **WebScraperLoader**: 웹 스크래핑 로더

### 3. Interfaces Layer

#### API Routes
- **DocumentRoutes**: 문서 관련 API 엔드포인트
- **EmailRoutes**: 이메일 관련 API 엔드포인트
- **ChatRoutes**: 채팅/검색 API 엔드포인트

#### CLI Commands
- **DocumentCommands**: 문서 처리 CLI 명령어
- **EmailCommands**: 이메일 처리 CLI 명령어

## 설계 패턴

### 1. 포트/어댑터 패턴 (Ports/Adapters)

```python
# Port (Interface)
class VectorStorePort(ABC):
    @abstractmethod
    async def add_embeddings(self, embeddings: List[Embedding]) -> bool:
        pass

# Adapter (Implementation)
class QdrantVectorStore(VectorStorePort):
    async def add_embeddings(self, embeddings: List[Embedding]) -> bool:
        # Qdrant 구체적 구현
        pass
```

### 2. 의존성 주입 (Dependency Injection)

```python
# Use Case는 Port에만 의존
class DocumentProcessingUseCase:
    def __init__(
        self,
        document_loader: DocumentLoaderPort,
        embedding_model: EmbeddingModelPort,
        vector_store: VectorStorePort
    ):
        self._document_loader = document_loader
        self._embedding_model = embedding_model
        self._vector_store = vector_store
```

### 3. 팩토리 패턴 (Factory Pattern)

```python
# 어댑터 생성을 위한 팩토리
class AdapterFactory:
    @staticmethod
    def create_vector_store(config: ConfigPort) -> VectorStorePort:
        if config.get_vector_store_type() == "qdrant":
            return QdrantVectorStore(config)
        elif config.get_vector_store_type() == "faiss":
            return FAISSVectorStore(config)
```

## 데이터 흐름

### 1. 문서 처리 플로우

```
JSON/PDF → DocumentLoader → Document Entity → 
TextChunker → Chunks → EmbeddingModel → Vectors → 
VectorStore → Storage
```

### 2. 이메일 처리 플로우

```
Email JSON → EmailLoader → Email Entity → 
Subject/Body → EmbeddingModel → Vectors → 
VectorStore → Storage
```

### 3. 검색 플로우

```
Query → EmbeddingModel → Query Vector → 
VectorStore → Similar Vectors → SearchResult → 
Response
```

## 확장성 고려사항

### 1. 새로운 벡터 DB 추가

1. `VectorStorePort` 인터페이스 구현
2. `AdapterFactory`에 새 어댑터 등록
3. 설정에 새 타입 추가

### 2. 새로운 임베딩 모델 추가

1. `EmbeddingModelPort` 인터페이스 구현
2. `AdapterFactory`에 새 어댑터 등록
3. 설정에 새 모델 추가

### 3. 새로운 문서 타입 추가

1. `DocumentLoaderPort` 인터페이스 구현
2. 새 엔티티 타입 정의 (필요시)
3. 유스케이스에 새 로더 통합

## 테스트 전략

### 1. 단위 테스트
- Core 레이어의 각 컴포넌트 독립 테스트
- Mock 객체를 사용한 의존성 격리

### 2. 통합 테스트
- 어댑터와 외부 시스템 간 연동 테스트
- 실제 데이터베이스/API 사용

### 3. E2E 테스트
- 전체 플로우 테스트
- API 엔드포인트 테스트

## 성능 고려사항

### 1. 비동기 처리
- 모든 I/O 작업은 비동기로 처리
- 배치 처리를 통한 효율성 향상

### 2. 메모리 관리
- 대용량 문서 처리 시 스트리밍 방식 사용
- 청킹을 통한 메모리 사용량 제어

### 3. 캐싱
- 임베딩 결과 캐싱
- 검색 결과 캐싱 (필요시)

## 보안 고려사항

### 1. API 보안
- 인증/권한 부여 구현
- Rate Limiting 적용

### 2. 데이터 보안
- 민감정보 마스킹
- 데이터 암호화 (필요시)

### 3. 입력 검증
- 모든 입력 데이터 검증
- SQL Injection 등 공격 방어

## 모니터링 및 로깅

### 1. 구조화된 로깅
- 각 레이어별 로깅 전략
- 에러 추적 및 디버깅 지원

### 2. 메트릭 수집
- 처리 성능 모니터링
- 리소스 사용량 추적

### 3. 헬스 체크
- 외부 시스템 연결 상태 확인
- 서비스 가용성 모니터링

이 아키텍처는 유지보수성, 확장성, 테스트 가능성을 극대화하도록 설계되었으며, 새로운 요구사항에 유연하게 대응할 수 있는 구조를 제공합니다.
