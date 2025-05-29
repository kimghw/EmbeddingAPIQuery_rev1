# 작업 요약 및 재사용 가능한 컴포넌트 가이드

## 📋 완료된 작업 요약

### 사용자 요청사항
- **핵심 질의**: "작동 온도는 몇도인가?"
- **대상 문서**: 3DM GV7 Data Sheet PDF
- **요구사항**: PDF 문서에서 작동 온도 정보를 정확히 추출하여 답변

### 구현된 기능
1. **PDF 문서 처리 파이프라인**
   - PDF 로딩 및 텍스트 추출
   - 텍스트 청킹 (1000자, 200자 오버랩)
   - OpenAI 임베딩 생성
   - Qdrant 벡터 저장소에 저장

2. **문서 검색 시스템**
   - 의미론적 검색 (Semantic Search)
   - 다국어 질의 지원 (한국어/영어)
   - CLI 인터페이스를 통한 실시간 검색

3. **질의 결과**
   - **답변**: 3DM GV7의 작동 온도는 **-40°C to 85°C**
   - 검색 점수: 0.2489 (한국어), 0.2848 (영어)
   - 정확한 스펙 정보 추출 성공

## 🔧 핵심 기술 스택

### 아키텍처
- **클린 아키텍처** (Clean Architecture)
- **포트/어댑터 패턴** (Ports & Adapters)
- **의존성 주입** (Dependency Injection)

### 기술 구성요소
```
Core Layer:
├── Entities: Document, Chunk
├── Use Cases: DocumentProcessing, DocumentRetrieval
└── Ports: DocumentLoader, EmbeddingModel, VectorStore

Adapters Layer:
├── PDF: PyPDF, Unstructured, WebScraper
├── Embedding: OpenAI text-embedding-3-small
├── Vector Store: Qdrant, FAISS, Mock
└── Chunking: RecursiveCharacter, Semantic

Interfaces:
├── CLI: Click-based commands
└── API: FastAPI (준비됨)
```

## 🚀 다른 프로젝트에서 활용 방법

### 1. 기본 설정 및 환경 구성

#### 필수 패키지
```bash
# 가상환경 생성
python -m venv your_project_env
source your_project_env/bin/activate  # Linux/Mac
# your_project_env\Scripts\activate  # Windows

# 핵심 의존성
pip install openai qdrant-client pypdf click pydantic pydantic-settings python-dotenv
```

#### 환경 변수 설정
```bash
# .env 파일
OPENAI_API_KEY=your_openai_api_key
QDRANT_URL=http://localhost:6333
QDRANT_API_KEY=your_qdrant_api_key  # 선택사항
ENVIRONMENT=development
```

### 2. 핵심 컴포넌트 재사용

#### A. 문서 처리 파이프라인
```python
# 복사할 파일들:
core/entities/document.py
core/usecases/document_processing.py
adapters/pdf/pdf_loader.py
adapters/embedding/openai_embedding.py
adapters/embedding/text_chunker.py
adapters/vector_store/qdrant_vector_store.py
```

#### B. 검색 시스템
```python
# 복사할 파일들:
core/usecases/document_retrieval.py
adapters/vector_store/simple_retriever.py
core/ports/retriever.py
```

#### C. 설정 관리
```python
# 복사할 파일들:
config/settings.py
config/adapter_factory.py
```

### 3. 프로젝트별 커스터마이징

#### A. 새로운 문서 타입 지원
```python
# 새 로더 추가 예시
class WordDocumentLoader(DocumentLoaderPort):
    def load_document(self, file_path: str) -> Document:
        # Word 문서 처리 로직
        pass

# adapter_factory.py에 등록
def create_document_loader(loader_type: str, config):
    if loader_type == "word":
        return WordDocumentLoader()
    # 기존 로더들...
```

#### B. 다른 임베딩 모델 사용
```python
# 새 임베딩 모델 추가
class HuggingFaceEmbedding(EmbeddingModelPort):
    def generate_embedding(self, text: str) -> List[float]:
        # HuggingFace 모델 사용
        pass
```

#### C. 다른 벡터 데이터베이스 사용
```python
# 새 벡터 저장소 추가
class ChromaVectorStore(VectorStorePort):
    def store_embeddings(self, embeddings: List[Embedding]) -> bool:
        # ChromaDB 사용
        pass
```

### 4. CLI 명령어 확장

#### 새 명령어 추가
```python
# interfaces/cli/main.py에 추가
@cli.command()
@click.option('--query', required=True, help='Search query')
@click.option('--language', default='auto', help='Query language')
def advanced_search(query: str, language: str):
    """Advanced search with language detection"""
    # 고급 검색 로직
    pass
```

### 5. API 인터페이스 활용

#### FastAPI 서버 시작
```python
# 이미 준비된 API 사용
python -m interfaces.api.main

# 또는 uvicorn 직접 실행
uvicorn interfaces.api.main:app --reload --port 8000
```

#### API 엔드포인트 예시
```bash
# 문서 업로드
curl -X POST "http://localhost:8000/documents/upload" \
     -F "file=@your_document.pdf"

# 문서 검색
curl -X GET "http://localhost:8000/documents/search?query=your_question"
```

## 📊 성능 최적화 팁

### 1. 청킹 전략
- **일반 문서**: chunk_size=1000, overlap=200
- **기술 문서**: chunk_size=1500, overlap=300
- **짧은 문서**: chunk_size=500, overlap=100

### 2. 임베딩 모델 선택
- **속도 우선**: text-embedding-3-small
- **정확도 우선**: text-embedding-3-large
- **비용 절약**: text-embedding-ada-002

### 3. 벡터 저장소 선택
- **개발/테스트**: Mock 또는 FAISS
- **프로덕션**: Qdrant 또는 Pinecone
- **대용량**: Elasticsearch with dense_vector

## 🔍 테스트 전략

### 1. 단위 테스트
```python
# 각 어댑터별 테스트
python test_pdf_loader.py
python test_embedding.py
python test_vector_store.py
```

### 2. 통합 테스트
```python
# 전체 파이프라인 테스트
python test_full_pipeline.py
```

### 3. 성능 테스트
```python
# 대용량 문서 처리 테스트
python test_performance.py
```

## 📝 프로젝트 적용 체크리스트

### 필수 단계
- [ ] 가상환경 설정 및 패키지 설치
- [ ] 환경 변수 설정 (.env 파일)
- [ ] 핵심 컴포넌트 복사 (core, adapters, config)
- [ ] 프로젝트별 설정 조정 (settings.py)
- [ ] 기본 테스트 실행

### 선택 단계
- [ ] 새로운 문서 타입 지원 추가
- [ ] 다른 임베딩 모델 통합
- [ ] 다른 벡터 데이터베이스 연동
- [ ] API 인터페이스 커스터마이징
- [ ] 고급 검색 기능 추가

### 검증 단계
- [ ] 샘플 문서로 전체 파이프라인 테스트
- [ ] 질의 응답 정확도 확인
- [ ] 성능 벤치마크 실행
- [ ] 에러 처리 및 로깅 확인

## 🎯 성공 사례: 3DM GV7 온도 질의

### 입력
- **문서**: 3DM GV7 Data Sheet (PDF, 1.3MB)
- **질의**: "작동 온도는 몇도인가?" / "operating temperature"

### 출력
- **정확한 답변**: -40°C to 85°C
- **처리 시간**: ~2초 (문서 로딩 + 임베딩 + 검색)
- **신뢰도**: 높음 (관련 스펙 섹션에서 정확히 추출)

### 핵심 성공 요인
1. **적절한 청킹**: 스펙 정보가 하나의 청크에 완전히 포함
2. **의미론적 검색**: 한국어 질의도 영어 문서에서 정확히 매칭
3. **클린 아키텍처**: 각 컴포넌트의 독립성으로 디버깅 용이
4. **포트/어댑터 패턴**: 다양한 구현체 교체 가능

이 가이드를 참고하여 다른 프로젝트에서도 동일한 수준의 문서 검색 시스템을 구축할 수 있습니다.
