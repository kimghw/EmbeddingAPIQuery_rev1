# Document Embedding & Retrieval System - 사용자 요구사항

## 1. 배경 및 큰 그림
- **프로젝트명**: Document Embedding & Retrieval System
- **목적**: PDF 문서 처리, 외부 API 데이터 수집, 벡터 임베딩 기반 문서 검색 시스템 구축
- **핵심 가치**: 멀티 인터페이스 지원(API, CLI)과 확장 가능한 아키텍처

## 2. 모듈 분할 기준
- **CORE 모듈**: 비즈니스 로직, 엔티티, 유스케이스 (외부 의존성 없음)
- **PORTS**: 인터페이스/추상 클래스 정의
- **ADAPTERS**: 외부 시스템 연동 구현체 (DB, API, 파일 I/O)
- **INTERFACES**: FastAPI 라우터, CLI 명령어 (얇은 어댑터)

## 3. 언어 및 라이브러리
- **언어**: Python 3.12+
- **웹 프레임워크**: FastAPI
- **CLI**: Click
- **비동기**: asyncio/await 기반
- **데이터 모델**: Pydantic
- **문서 로드 처리**: PyPDF 또는 유사 라이브러리
- **청킹**: SemanticChunker
- **임베딩**: OpenAI API
- **벡터 저장소**: Qdrant(HNSW), FAISS, Chroma
- **질의 답변**: OpenAI API

## 4. 핵심 기능 요구사항

### 4.1 Atomic 유스케이스
1. **문서 로더(Loader) 모듈**
   - [x] 사용: PyPDF, PyMuPDF, JSONLoader
   - [ ] 추가 고려: UnstructuredPDFLoader, TextLoader, WebBaseLoader
   - [ ] 요구사항: 문서 로더를 여러 개 사용할 예정이기에 필요시 인터페이스, DI, 어댑터 적용

2. **텍스트 청킹 전략**
   - [x] 사용: SemanticChunker
   - [ ] 추가 고려: RecursiveCharacterTextSplitter, MarkdownTextSplitter
   - [ ] 요구사항: 문서 ID, 메타데이터

3. **임베딩 모델**
   - [x] 사용: OpenAIEmbeddings (text-embedding-3-small)
   - [ ] 추가 고려: HuggingFaceBgeEmbeddings (BAAI/bge-small-en-v1.5)
   - [ ] 요구사항: 문서 ID, 메타데이터

4. **벡터 저장 및 인덱스**
   - [x] 사용: Qdrant
   - [ ] 추가 고려: FAISS, ChromaDB
   - [ ] 요구사항: 문서 ID, 메타데이터

5. **리트리버**
   - [x] 사용: MultiVectorRetriever
   - [ ] 추가 고려: MultiQueryRetriever, ParentDocumentRetriever, MMR 등
   - [ ] 요구사항: 문서 ID, 메타데이터

### 4.2 Composite 유스케이스/서비스
1. **벡터 DB 저장**
   - [ ] 문서 업로드, 청킹, 임베딩, 벡터 DB 저장
   - [ ] 각 모듈 다른 모듈로 변경 가능

2. **질의**
   - [ ] 질의, 임베딩, 유사도 검색, 관련 청크들 반환
   - [ ] 각 모듈 다른 모듈로 변경 가능

3. **질의 + 답변생성**
   - [ ] 청크 + 질의, LLM 답변 생성
   - [ ] 각 모듈 다른 모듈로 변경 가능

## 5. 아키텍처 요구사항
- 클린 아키텍처 적용
- 포트/어댑터 패턴
- 의존성 주입
- 비동기 처리 지원
- 멀티 인터페이스 (API, CLI)

## 6. 상태
- **현재 단계**: 프로젝트 기본 구조 완료
- **완료된 작업**:
  - [x] 프로젝트 디렉토리 구조 생성
  - [x] Git 초기화 및 가상환경 설정
  - [x] 설정 관리 시스템 (포트/어댑터 패턴)
  - [x] 도메인 엔티티 정의 (Document, DocumentChunk, Embedding, etc.)
  - [x] 포트 인터페이스 정의 (DocumentLoader, TextChunker, EmbeddingModel, VectorStore, Retriever)
  - [x] 유스케이스 정의 (DocumentProcessing, DocumentRetrieval)
  - [x] 프로젝트 문서화 (README.md)
- **다음 단계**: 어댑터 구현 및 인터페이스 개발
