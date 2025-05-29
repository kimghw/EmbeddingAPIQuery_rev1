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

### 3.1 핵심 기술 스택
- **언어**: Python 3.12+
- **웹 프레임워크**: FastAPI 0.104.1
- **CLI**: Click 8.1.7
- **비동기**: asyncio/await 기반
- **데이터 모델**: Pydantic 2.5.0, Pydantic-Settings 2.1.0

### 3.2 문서 처리 라이브러리
- **PDF 처리**: 
  - PyPDF 3.17.1 (기본 PDF 파싱)
  - PyMuPDF 1.23.8 (고급 PDF 처리)
- **웹 스크래핑**: 
  - aiohttp 3.9.1 (비동기 HTTP 클라이언트)
  - BeautifulSoup4 4.12.2 (HTML 파싱)
  - lxml 4.9.3 (XML/HTML 파서)
- **구조화되지 않은 문서**: 
  - unstructured[all-docs] 0.11.2 (선택적, 다양한 문서 형식 지원)

### 3.3 AI/ML 및 임베딩 라이브러리
- **LLM 및 임베딩**: 
  - OpenAI >=1.6.1 (GPT 모델 및 text-embedding-3-small)
  - LangChain 0.0.350 (LLM 체인 및 프롬프트 관리)
  - LangChain-OpenAI 0.0.2 (OpenAI 통합)
  - LangChain-Community 0.0.10 (커뮤니티 통합)

### 3.4 벡터 저장소 및 검색
- **벡터 데이터베이스**:
  - Qdrant-client 1.7.0 (클라우드 네이티브 벡터 DB, HNSW 알고리즘)
  - FAISS-cpu 1.7.4 (Facebook AI 유사도 검색, 로컬 벡터 인덱스)
- **텍스트 청킹**: 
  - LangChain SemanticChunker (의미 기반 청킹)
  - RecursiveCharacterTextSplitter (재귀적 문자 분할)

### 3.5 질의 답변 시스템
- **LLM 모델**: 
  - OpenAI GPT-4 / GPT-3.5-turbo (질의 응답 생성)
  - LangChain ChatOpenAI (채팅 기반 LLM 인터페이스)
- **프롬프트 엔지니어링**:
  - LangChain PromptTemplate (프롬프트 템플릿 관리)
  - LangChain ChatPromptTemplate (채팅 프롬프트)
- **체인 구성**:
  - LangChain RetrievalQA (검색 기반 질의응답)
  - LangChain ConversationalRetrievalChain (대화형 검색)
  - LangChain LCEL (LangChain Expression Language)

### 3.6 개발 및 테스트 도구
- **테스트**: pytest 7.4.3, pytest-asyncio 0.21.1
- **코드 품질**: black 23.11.0, isort 5.12.0, flake8 6.1.0, mypy 1.7.1
- **유틸리티**: python-multipart 0.0.6, python-dotenv 1.0.0

## 4. 핵심 기능 요구사항

### 4.1 Atomic 유스케이스
1. **문서 로더(Loader) 모듈**
   - [x] 사용: PyPDF, PyMuPDF, JSONLoader
   - [x] 추가 구현: UnstructuredPDFLoader, WebScraperLoader
   - [x] 요구사항: 문서 로더를 여러 개 사용할 예정이기에 필요시 인터페이스, DI, 어댑터 적용

2. **텍스트 청킹 전략**
   - [x] 사용: SemanticChunker
   - [x] 추가 구현: RecursiveCharacterTextSplitter
   - [x] 요구사항: 문서 ID, 메타데이터

3. **임베딩 모델**
   - [x] 사용: OpenAIEmbeddings (text-embedding-3-small)
   - [ ] 추가 고려: HuggingFaceBgeEmbeddings (BAAI/bge-small-en-v1.5)
   - [x] 요구사항: 문서 ID, 메타데이터

4. **벡터 저장 및 인덱스**
   - [x] 사용: Qdrant
   - [x] 추가 구현: FAISS, MockVectorStore
   - [x] 요구사항: 문서 ID, 메타데이터

5. **리트리버**
   - [x] 사용: SimpleRetriever
   - [x] 추가 구현: EnsembleRetriever (다중 융합 전략 지원)
   - [x] 요구사항: 문서 ID, 메타데이터

6. **질의 답변 생성**
   - [ ] LLM 모델: OpenAI GPT-4/GPT-3.5-turbo
   - [ ] 체인 구성: LangChain RetrievalQA, ConversationalRetrievalChain
   - [ ] 프롬프트 관리: LangChain PromptTemplate, ChatPromptTemplate
   - [ ] 요구사항: 검색된 청크 + 사용자 질의 → 자연어 답변 생성

### 4.2 Composite 유스케이스/서비스
1. **벡터 DB 저장**
   - [x] 문서 업로드, 청킹, 임베딩, 벡터 DB 저장
   - [x] 각 모듈 다른 모듈로 변경 가능

2. **질의**
   - [x] 질의, 임베딩, 유사도 검색, 관련 청크들 반환
   - [x] 각 모듈 다른 모듈로 변경 가능

3. **질의 + 답변생성**
   - [ ] 청크 + 질의, LLM 답변 생성 (LangChain 기반)
   - [ ] 각 모듈 다른 모듈로 변경 가능
   - [ ] 대화 히스토리 관리 및 컨텍스트 유지

## 5. 아키텍처 요구사항
- 클린 아키텍처 적용
- 포트/어댑터 패턴
- 의존성 주입
- 비동기 처리 지원
- 멀티 인터페이스 (API, CLI)

## 6. 최신 추가 기능 (2024-05-24)

### 6.1 EnsembleRetriever 구현 완료
- **다중 융합 전략 지원**:
  - Rank Fusion (RRF): 순위 기반 융합
  - Score Fusion: 점수 기반 융합  
  - Weighted Score: 가중치 적용 점수 융합
  - Voting: 투표 기반 융합
- **동적 리트리버 관리**: 런타임에 리트리버 추가/제거 가능
- **가중치 조정**: 각 리트리버별 가중치 설정 가능
- **헬스 체크**: 앙상블 내 모든 리트리버 상태 확인

### 6.2 JSON 로더 구현 완료
- **JSON/JSONL 파일 지원**: 구조화된 데이터 로드
- **메타데이터 자동 추출**: 파일 정보 및 구조 분석
- **다중 파일 처리**: 배치 로드 기능
- **바이트 스트림 지원**: 메모리 기반 처리

### 6.3 AdapterFactory 확장
- **리트리버 생성 메서드 추가**: create_retriever_adapter, create_ensemble_retriever
- **통합 팩토리 패턴**: 모든 어댑터 타입을 단일 팩토리에서 관리
- **설정 기반 생성**: 환경 설정에 따른 자동 어댑터 선택

## 7. 상태
- **현재 단계**: 고급 검색 기능 구현 완료
- **완료된 작업**:
  - [x] 프로젝트 디렉토리 구조 생성
  - [x] Git 초기화 및 가상환경 설정
  - [x] 설정 관리 시스템 (포트/어댑터 패턴)
  - [x] 도메인 엔티티 정의 (Document, DocumentChunk, Embedding, etc.)
  - [x] 포트 인터페이스 정의 (DocumentLoader, TextChunker, EmbeddingModel, VectorStore, Retriever)
  - [x] 유스케이스 정의 (DocumentProcessing, DocumentRetrieval)
  - [x] 프로젝트 문서화 (README.md)
  - [x] 다양한 어댑터 구현 (PDF, JSON, Web Scraper, Unstructured)
  - [x] 벡터 저장소 어댑터 (Qdrant, FAISS, Mock)
  - [x] 텍스트 청킹 어댑터 (Recursive, Semantic)
  - [x] 고급 리트리버 (Simple, Ensemble)
  - [x] AdapterFactory 패턴 구현
  - [x] 통합 테스트 및 검증
- **다음 단계**: LLM 답변 생성 기능 및 API/CLI 인터페이스 완성
