# 프로젝트 전체 흐름도

## 1. 시스템 아키텍처 개요

```mermaid
graph TB
    subgraph "Entry Points (진입점)"
        CLI[CLI Interface]
        API[FastAPI Interface]
        WEB[Web Interface]
    end
    
    subgraph "Core Business Logic (핵심 비즈니스 로직)"
        UC1[Document Processing UseCase]
        UC2[Document Retrieval UseCase]
        ENT[Entities: Document, Chunk, Query]
        PORTS[Ports: Interfaces]
    end
    
    subgraph "Adapters (어댑터)"
        LOAD[Document Loaders]
        CHUNK[Text Chunkers]
        EMBED[Embedding Models]
        VECTOR[Vector Stores]
        RETR[Retrievers]
    end
    
    subgraph "External Services (외부 서비스)"
        OPENAI[OpenAI API]
        QDRANT[Qdrant DB]
        FAISS[FAISS Storage]
        FILES[File System]
    end
    
    CLI --> UC1
    CLI --> UC2
    API --> UC1
    API --> UC2
    WEB --> UC1
    WEB --> UC2
    
    UC1 --> ENT
    UC2 --> ENT
    UC1 --> PORTS
    UC2 --> PORTS
    
    PORTS --> LOAD
    PORTS --> CHUNK
    PORTS --> EMBED
    PORTS --> VECTOR
    PORTS --> RETR
    
    LOAD --> FILES
    EMBED --> OPENAI
    VECTOR --> QDRANT
    VECTOR --> FAISS
```

## 2. 문서 처리 흐름 (Document Processing Flow)

```mermaid
flowchart TD
    START([시작: 문서 업로드]) --> LOAD{문서 로더 선택}
    
    LOAD -->|PDF| PDF_LOAD[PDF Loader]
    LOAD -->|JSON| JSON_LOAD[JSON Loader]
    LOAD -->|WEB| WEB_LOAD[Web Scraper]
    LOAD -->|기타| UNSTR_LOAD[Unstructured Loader]
    
    PDF_LOAD --> DOC[Document Entity 생성]
    JSON_LOAD --> DOC
    WEB_LOAD --> DOC
    UNSTR_LOAD --> DOC
    
    DOC --> CHUNK_SELECT{청킹 방법 선택}
    
    CHUNK_SELECT -->|Recursive| REC_CHUNK[Recursive Chunker]
    CHUNK_SELECT -->|Semantic| SEM_CHUNK[Semantic Chunker]
    
    REC_CHUNK --> CHUNKS[Document Chunks 생성]
    SEM_CHUNK --> CHUNKS
    
    CHUNKS --> EMBED_SELECT{임베딩 모델 선택}
    
    EMBED_SELECT -->|OpenAI| OPENAI_EMBED[OpenAI Embedding]
    EMBED_SELECT -->|HuggingFace| HF_EMBED[HuggingFace Embedding]
    
    OPENAI_EMBED --> VECTORS[Vector Embeddings 생성]
    HF_EMBED --> VECTORS
    
    VECTORS --> STORE_SELECT{벡터 저장소 선택}
    
    STORE_SELECT -->|Qdrant| QDRANT_STORE[Qdrant Vector Store]
    STORE_SELECT -->|FAISS| FAISS_STORE[FAISS Vector Store]
    STORE_SELECT -->|Mock| MOCK_STORE[Mock Vector Store]
    
    QDRANT_STORE --> STORED[벡터 저장 완료]
    FAISS_STORE --> STORED
    MOCK_STORE --> STORED
    
    STORED --> END([처리 완료])
```

## 3. 문서 검색 흐름 (Document Retrieval Flow)

```mermaid
flowchart TD
    QUERY_START([검색 쿼리 입력]) --> QUERY_EMBED[쿼리 임베딩 생성]
    
    QUERY_EMBED --> RETR_SELECT{리트리버 선택}
    
    RETR_SELECT -->|Simple| SIMPLE_RETR[Simple Retriever]
    RETR_SELECT -->|Ensemble| ENSEMBLE_RETR[Ensemble Retriever]
    
    SIMPLE_RETR --> VECTOR_SEARCH[벡터 유사도 검색]
    
    ENSEMBLE_RETR --> MULTI_SEARCH[다중 검색 전략]
    MULTI_SEARCH --> SIMILARITY[Similarity Search]
    MULTI_SEARCH --> MMR[MMR Search]
    MULTI_SEARCH --> THRESHOLD[Threshold Search]
    
    VECTOR_SEARCH --> RESULTS[검색 결과]
    SIMILARITY --> COMBINE[결과 조합]
    MMR --> COMBINE
    THRESHOLD --> COMBINE
    COMBINE --> RESULTS
    
    RESULTS --> RANK[결과 랭킹 및 스코어링]
    RANK --> FILTER[필터링 및 후처리]
    FILTER --> RESPONSE[최종 응답 생성]
    RESPONSE --> QUERY_END([검색 완료])
```

## 4. 클린 아키텍처 레이어 구조

```mermaid
graph TB
    subgraph "Interfaces Layer (인터페이스 계층)"
        CLI_INT[CLI Interface]
        API_INT[FastAPI Interface]
        WEB_INT[Web Interface]
    end
    
    subgraph "Use Cases Layer (유즈케이스 계층)"
        DOC_PROC[Document Processing UseCase]
        DOC_RETR[Document Retrieval UseCase]
    end
    
    subgraph "Domain Layer (도메인 계층)"
        ENTITIES[Entities]
        PORTS_INT[Ports/Interfaces]
    end
    
    subgraph "Infrastructure Layer (인프라 계층)"
        ADAPTERS[Adapters]
        EXTERNAL[External Services]
    end
    
    CLI_INT --> DOC_PROC
    CLI_INT --> DOC_RETR
    API_INT --> DOC_PROC
    API_INT --> DOC_RETR
    WEB_INT --> DOC_PROC
    WEB_INT --> DOC_RETR
    
    DOC_PROC --> ENTITIES
    DOC_PROC --> PORTS_INT
    DOC_RETR --> ENTITIES
    DOC_RETR --> PORTS_INT
    
    PORTS_INT --> ADAPTERS
    ADAPTERS --> EXTERNAL
```

## 5. 어댑터 팩토리 패턴

```mermaid
flowchart LR
    CONFIG[Configuration] --> FACTORY[Adapter Factory]
    
    FACTORY --> LOADER_FACTORY[Document Loader Factory]
    FACTORY --> CHUNKER_FACTORY[Text Chunker Factory]
    FACTORY --> EMBED_FACTORY[Embedding Factory]
    FACTORY --> VECTOR_FACTORY[Vector Store Factory]
    FACTORY --> RETR_FACTORY[Retriever Factory]
    
    LOADER_FACTORY -->|pdf| PDF_ADAPTER[PDF Adapter]
    LOADER_FACTORY -->|json| JSON_ADAPTER[JSON Adapter]
    LOADER_FACTORY -->|web| WEB_ADAPTER[Web Adapter]
    
    CHUNKER_FACTORY -->|recursive| REC_ADAPTER[Recursive Adapter]
    CHUNKER_FACTORY -->|semantic| SEM_ADAPTER[Semantic Adapter]
    
    EMBED_FACTORY -->|openai| OPENAI_ADAPTER[OpenAI Adapter]
    EMBED_FACTORY -->|huggingface| HF_ADAPTER[HuggingFace Adapter]
    
    VECTOR_FACTORY -->|qdrant| QDRANT_ADAPTER[Qdrant Adapter]
    VECTOR_FACTORY -->|faiss| FAISS_ADAPTER[FAISS Adapter]
    VECTOR_FACTORY -->|mock| MOCK_ADAPTER[Mock Adapter]
    
    RETR_FACTORY -->|simple| SIMPLE_ADAPTER[Simple Adapter]
    RETR_FACTORY -->|ensemble| ENSEMBLE_ADAPTER[Ensemble Adapter]
```

## 6. 데이터 흐름 (Data Flow)

```mermaid
sequenceDiagram
    participant User
    participant CLI
    participant UseCase
    participant Adapter
    participant External
    
    User->>CLI: 문서 처리 요청
    CLI->>UseCase: process_document()
    UseCase->>Adapter: load_document()
    Adapter->>External: 파일 읽기
    External-->>Adapter: 문서 데이터
    Adapter-->>UseCase: Document Entity
    
    UseCase->>Adapter: chunk_document()
    Adapter-->>UseCase: Document Chunks
    
    UseCase->>Adapter: embed_chunks()
    Adapter->>External: OpenAI API 호출
    External-->>Adapter: 임베딩 벡터
    Adapter-->>UseCase: Embeddings
    
    UseCase->>Adapter: store_embeddings()
    Adapter->>External: Qdrant 저장
    External-->>Adapter: 저장 완료
    Adapter-->>UseCase: 성공 응답
    
    UseCase-->>CLI: 처리 결과
    CLI-->>User: 완료 메시지
```

## 7. 설정 기반 컴포넌트 선택

```mermaid
flowchart TD
    ENV_FILE[.env 파일] --> CONFIG[Configuration]
    ENV_VAR[환경변수] --> CONFIG
    CLI_OPT[CLI 옵션] --> CONFIG
    
    CONFIG --> FACTORY[Adapter Factory]
    
    FACTORY --> DECISION{설정 값에 따른 선택}
    
    DECISION -->|DOCUMENT_LOADER_TYPE=pdf| PDF_CHOICE[PDF Loader]
    DECISION -->|TEXT_CHUNKER_TYPE=semantic| SEM_CHOICE[Semantic Chunker]
    DECISION -->|EMBEDDING_TYPE=openai| OPENAI_CHOICE[OpenAI Embedding]
    DECISION -->|VECTOR_STORE_TYPE=qdrant| QDRANT_CHOICE[Qdrant Store]
    DECISION -->|RETRIEVER_TYPE=ensemble| ENSEMBLE_CHOICE[Ensemble Retriever]
    
    PDF_CHOICE --> PIPELINE[처리 파이프라인]
    SEM_CHOICE --> PIPELINE
    OPENAI_CHOICE --> PIPELINE
    QDRANT_CHOICE --> PIPELINE
    ENSEMBLE_CHOICE --> PIPELINE
```

## 8. 에러 처리 및 로깅

```mermaid
flowchart TD
    OPERATION[작업 실행] --> SUCCESS{성공?}
    
    SUCCESS -->|Yes| LOG_SUCCESS[성공 로그]
    SUCCESS -->|No| CATCH_ERROR[예외 포착]
    
    CATCH_ERROR --> LOG_ERROR[에러 로그]
    LOG_ERROR --> ERROR_RESPONSE[에러 응답 생성]
    
    LOG_SUCCESS --> RESPONSE[성공 응답]
    ERROR_RESPONSE --> RESPONSE
    
    RESPONSE --> USER[사용자에게 반환]
```

이 흐름도들은 프로젝트의 전체적인 구조와 데이터 흐름을 보여주며, 클린 아키텍처 원칙에 따라 각 계층이 어떻게 상호작용하는지 명확하게 표현합니다.
