# Project Description

## 프로젝트 개요

### 프로젝트명
**Document Embedding & Retrieval System**

### 프로젝트 목적
PDF 문서 처리, 외부 API 데이터 수집, 벡터 임베딩 기반 문서 검색 시스템을 구축하여 효율적인 문서 관리 및 검색 솔루션을 제공합니다.

### 핵심 가치
- **멀티 인터페이스 지원**: API와 CLI 모두 지원하여 다양한 사용 시나리오에 대응
- **확장 가능한 아키텍처**: 클린 아키텍처와 포트/어댑터 패턴으로 유지보수성 확보
- **모듈화된 설계**: 각 구성 요소를 독립적으로 교체 가능한 구조

## 기술 스택

### 언어 및 프레임워크
- **언어**: Python 3.12+
- **웹 프레임워크**: FastAPI (비동기 처리 지원)
- **CLI 프레임워크**: Click
- **데이터 모델**: Pydantic (타입 안전성 보장)

### 핵심 라이브러리
- **문서 처리**: PyPDF, PyMuPDF, JSONLoader
- **텍스트 청킹**: SemanticChunker, RecursiveCharacterTextSplitter
- **임베딩**: OpenAI API (text-embedding-3-small), HuggingFace BGE
- **벡터 저장소**: Qdrant (HNSW), FAISS, ChromaDB
- **비동기 처리**: asyncio/await

### 외부 서비스
- **OpenAI API**: 임베딩 및 답변 생성
- **Microsoft Graph API**: 이메일 데이터 수집 (예정)

## 아키텍처 설계

### 클린 아키텍처 적용
```
┌─────────────────────────────────────────────────────────────┐
│                    Interfaces Layer                         │
│  ┌─────────────────┐    ┌─────────────────────────────────┐ │
│  │   FastAPI       │    │        CLI                      │ │
│  │   Routes        │    │     Commands                    │ │
│  └─────────────────┘    └─────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                   Adapters Layer                            │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │   PDF       │ │ Embedding   │ │    Vector Store         │ │
│  │  Adapters   │ │  Adapters   │ │     Adapters            │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────────────────────────────────────┐
│                     Core Layer                              │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐ │
│  │  Entities   │ │    Ports    │ │      Use Cases          │ │
│  │             │ │(Interfaces) │ │                         │ │
│  └─────────────┘ └─────────────┘ └─────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 포트/어댑터 패턴
- **포트(Ports)**: 비즈니스 로직이 필요로 하는 인터페이스 정의
- **어댑터(Adapters)**: 외부 시스템과의 실제 연동 구현
- **의존성 역전**: Core는 구체적인 구현에 의존하지 않음

## 디렉터리 구조

```
EmbeddingAPIQuery_rev1/
├── core/                           # 비즈니스 로직 (외부 의존성 없음)
│   ├── entities/                   # 도메인 엔티티
│   │   ├── __init__.py
│   │   └── document.py            # Document, DocumentChunk 엔티티
│   ├── ports/                     # 인터페이스 정의
│   │   ├── __init__.py
│   │   ├── document_loader.py     # 문서 로더 인터페이스
│   │   ├── text_chunker.py        # 텍스트 청킹 인터페이스
│   │   ├── embedding_model.py     # 임베딩 모델 인터페이스
│   │   ├── vector_store.py        # 벡터 저장소 인터페이스
│   │   └── retriever.py           # 검색 인터페이스
│   ├── usecases/                  # 유스케이스
│   │   ├── __init__.py
│   │   ├── document_processing.py # 문서 처리 유스케이스
│   │   └── document_retrieval.py  # 문서 검색 유스케이스
│   └── services/                  # 서비스 로직
│       └── __init__.py
├── adapters/                      # 외부 시스템 연동
│   ├── db/                        # 데이터베이스 어댑터
│   ├── external_api/              # 외부 API 어댑터
│   ├── pdf/                       # PDF 처리 어댑터
│   │   └── pdf_loader.py         # PyPDF 기반 로더
│   ├── embedding/                 # 임베딩 어댑터
│   │   ├── text_chunker.py       # 텍스트 청킹 구현
│   │   └── openai_embedding.py   # OpenAI 임베딩 구현
│   └── vector_store/              # 벡터 저장소 어댑터
│       └── mock_vector_store.py  # 테스트용 Mock 구현
├── interfaces/                    # 진입점 (얇은 어댑터)
│   ├── api/                       # FastAPI 라우터
│   │   ├── __init__.py
│   │   ├── main.py               # FastAPI 앱 설정
│   │   └── documents.py          # 문서 관련 라우터
│   └── cli/                       # CLI 명령어
│       ├── __init__.py
│       └── main.py               # Click 기반 CLI
├── schemas/                       # Pydantic 모델
│   ├── __init__.py
│   └── document.py               # API 스키마 정의
├── config/                        # 설정 관리
│   ├── __init__.py
│   └── settings.py               # 환경별 설정
├── tests/                         # 테스트 코드
├── docs/                          # 문서
│   ├── user_requirements.md      # 사용자 요구사항
│   ├── ProcessAndTodoList.md     # 프로세스 및 할일 목록
│   ├── ProjectDescription.md     # 프로젝트 설명 (현재 파일)
│   └── testreport.md            # 테스트 보고서
├── main.py                        # 메인 진입점
├── requirements.txt               # 의존성 패키지
├── .env                          # 환경변수
├── .env.example                  # 환경변수 예시
└── .gitignore                    # Git 무시 파일
```

## 핵심 기능

### 1. 문서 처리 파이프라인
```
PDF/JSON 문서 → 텍스트 추출 → 청킹 → 임베딩 → 벡터 저장소
```

#### 지원 문서 형식
- **PDF**: PyPDF, PyMuPDF 기반
- **JSON**: 구조화된 데이터 처리
- **웹 페이지**: WebBaseLoader (예정)
- **마크다운**: MarkdownTextSplitter (예정)

#### 텍스트 청킹 전략
- **RecursiveCharacterTextSplitter**: 일반 텍스트 분할
- **SemanticChunker**: 의미 기반 분할 (예정)
- **MarkdownTextSplitter**: 마크다운 구조 기반 분할 (예정)

### 2. 임베딩 생성
- **OpenAI Embeddings**: text-embedding-3-small (1536차원)
- **HuggingFace BGE**: BAAI/bge-small-en-v1.5 (대안)
- **메타데이터 포함**: 문서 ID, 청크 정보, 생성 시간

### 3. 벡터 저장 및 검색
#### 지원 벡터 저장소
- **Qdrant**: HNSW 알고리즘 기반 (주요)
- **FAISS**: Facebook AI 유사도 검색 (선택사항)
- **ChromaDB**: 오픈소스 벡터 데이터베이스 (선택사항)

#### 검색 전략
- **MultiVectorRetriever**: 다중 벡터 검색
- **MultiQueryRetriever**: 다중 쿼리 검색 (예정)
- **ParentDocumentRetriever**: 부모 문서 검색 (예정)
- **MMR (Maximal Marginal Relevance)**: 다양성 고려 검색 (예정)

### 4. 질의 응답 시스템 (예정)
```
사용자 질의 → 임베딩 → 유사도 검색 → 관련 청크 → LLM → 답변 생성
```

## API 엔드포인트

### 문서 관리
- **POST /documents/upload**: 문서 업로드 및 처리
- **GET /documents/**: 문서 목록 조회
- **GET /documents/{document_id}/status**: 문서 처리 상태 조회
- **DELETE /documents/{document_id}**: 문서 삭제

### 검색 및 질의
- **POST /documents/search**: 문서 검색
- **POST /documents/query**: 질의 응답 (예정)

### 시스템 관리
- **GET /**: 시스템 상태 확인
- **GET /health**: 헬스 체크
- **GET /config**: 설정 정보 조회

## CLI 명령어

### 설정 관리
```bash
python -m interfaces.cli.main config-info    # 설정 정보 조회
```

### 테스트 명령어
```bash
python -m interfaces.cli.main test-chunker   # 텍스트 청킹 테스트
python -m interfaces.cli.main test-embedding # 임베딩 생성 테스트
```

### 문서 처리 (예정)
```bash
python -m interfaces.cli.main upload-pdf <file_path>     # PDF 업로드
python -m interfaces.cli.main search-docs <query>       # 문서 검색
python -m interfaces.cli.main process-batch <directory> # 배치 처리
```

## 설정 관리

### 환경별 설정
- **Development**: 개발 환경 설정
- **Production**: 운영 환경 설정
- **Test**: 테스트 환경 설정

### 주요 설정 항목
```python
# 애플리케이션 설정
APP_NAME = "Document Embedding & Retrieval System"
APP_VERSION = "1.0.0"
DEBUG = True

# OpenAI 설정
OPENAI_API_KEY = "your-api-key"
EMBEDDING_MODEL = "text-embedding-3-small"
VECTOR_DIMENSION = 1536

# 청킹 설정
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200

# 벡터 저장소 설정
COLLECTION_NAME = "documents"
```

## 보안 고려사항

### API 키 관리
- 환경변수를 통한 안전한 키 관리
- .env 파일을 .gitignore에 포함
- 운영 환경에서는 시크릿 관리 시스템 사용

### 데이터 보호
- 업로드된 문서의 안전한 처리
- 벡터 데이터의 암호화 저장 (예정)
- 사용자 인증 및 권한 관리 (예정)

## 성능 최적화

### 비동기 처리
- FastAPI의 비동기 기능 활용
- 대용량 문서 처리 시 스트리밍
- 배치 처리를 통한 효율성 향상

### 메모리 관리
- 청킹을 통한 메모리 사용량 제어
- 스트리밍 처리로 대용량 파일 지원
- 캐싱 시스템 도입 (예정)

### 확장성
- 마이크로서비스 아키텍처 준비
- 로드 밸런싱 지원 구조
- 수평 확장 가능한 설계

## 모니터링 및 로깅

### 로깅 시스템 (예정)
- 구조화된 로깅 (JSON 형식)
- 레벨별 로그 관리 (DEBUG, INFO, WARNING, ERROR)
- 로그 집계 및 분석 시스템 연동

### 성능 모니터링 (예정)
- API 응답 시간 측정
- 메모리 사용량 모니터링
- 에러율 추적

### 알림 시스템 (예정)
- 시스템 장애 시 알림
- 성능 임계치 초과 시 경고
- 정기적인 상태 보고

## 테스트 전략

### 단위 테스트
- Core 로직의 독립적 테스트
- Mock을 활용한 외부 의존성 분리
- 높은 코드 커버리지 목표

### 통합 테스트
- API 엔드포인트 테스트
- 전체 파이프라인 테스트
- 실제 외부 서비스와의 연동 테스트

### 성능 테스트
- 대용량 문서 처리 테스트
- 동시 요청 처리 능력 테스트
- 메모리 사용량 테스트

## 배포 및 운영

### 컨테이너화 (예정)
- Docker 이미지 생성
- 멀티 스테이지 빌드 최적화
- 환경별 컨테이너 설정

### CI/CD 파이프라인 (예정)
- 자동화된 테스트 실행
- 코드 품질 검사
- 자동 배포 시스템

### 환경 관리
- 개발/스테이징/운영 환경 분리
- 환경별 설정 관리
- 블루-그린 배포 전략

## 향후 발전 방향

### 단기 목표 (1-2개월)
- 실제 벡터 저장소 연동 완료
- 다양한 문서 형식 지원 확대
- 고급 검색 기능 구현

### 중기 목표 (3-6개월)
- 질의 응답 시스템 완성
- Microsoft Graph API 연동
- 성능 최적화 및 모니터링 시스템

### 장기 목표 (6개월 이상)
- 다국어 지원
- 고급 AI 기능 통합
- 엔터프라이즈 기능 (사용자 관리, 권한 제어)

## 기여 가이드라인

### 개발 원칙
1. **클린 아키텍처 유지**: Core 로직의 독립성 보장
2. **포트/어댑터 패턴**: 외부 의존성 분리
3. **테스트 주도 개발**: 기능 구현 전 테스트 작성
4. **문서화 우선**: 코드와 함께 문서 업데이트

### 코딩 스타일
- Python PEP 8 준수
- 타입 힌트 필수 사용
- Docstring 작성 (Google 스타일)
- 비동기 처리 적극 활용

### 브랜치 전략
- **main**: 운영 배포용 (안정 버전)
- **develop**: 개발 통합 브랜치
- **feature/***: 기능 개발 브랜치
- **hotfix/***: 긴급 수정 브랜치

---

**문서 버전**: 1.0.0  
**최종 업데이트**: 2025-05-24  
**작성자**: Development Team  
**검토자**: Architecture Team
