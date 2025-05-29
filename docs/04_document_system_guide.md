# 04. 문서 시스템 가이드

## 개요

문서 시스템은 다양한 형태의 문서(PDF, JSON, 웹 페이지 등)를 로드하고, 텍스트를 추출하여 임베딩으로 변환한 후 벡터 데이터베이스에 저장하는 시스템입니다.

## 지원 문서 타입

### 1. PDF 문서
- **PyPDF2 기반**: 기본 PDF 텍스트 추출
- **Unstructured 기반**: 고급 PDF 처리 (테이블, 이미지 등)
- **사용 사례**: 기술 문서, 매뉴얼, 보고서

### 2. JSON 문서
- **구조화된 데이터**: JSON 형태의 문서 데이터
- **메타데이터 지원**: 제목, 작성자, 날짜 등
- **사용 사례**: API 응답, 구조화된 콘텐츠

### 3. 웹 페이지
- **웹 스크래핑**: BeautifulSoup 기반
- **동적 콘텐츠**: Selenium 지원 (필요시)
- **사용 사례**: 온라인 문서, 블로그, 위키

## 시스템 구조

### Core Components

```python
# 문서 엔티티
@dataclass
class Document:
    id: str
    title: str
    content: str
    source: str
    metadata: Dict[str, Any]
    created_at: datetime

# 청크 엔티티
@dataclass
class Chunk:
    id: str
    document_id: str
    content: str
    chunk_index: int
    metadata: Dict[str, Any]
```

### Ports (인터페이스)

```python
class DocumentLoaderPort(ABC):
    @abstractmethod
    async def load_document(self, source: str) -> Document:
        pass

class TextChunkerPort(ABC):
    @abstractmethod
    async def chunk_text(self, text: str) -> List[Chunk]:
        pass
```

## 문서 처리 플로우

### 1. 문서 로딩

```mermaid
graph LR
    A[문서 소스] --> B[DocumentLoader]
    B --> C[Document Entity]
    C --> D[메타데이터 추출]
    D --> E[텍스트 정제]
```

### 2. 텍스트 청킹

```mermaid
graph LR
    A[Document] --> B[TextChunker]
    B --> C[Chunk 분할]
    C --> D[오버랩 처리]
    D --> E[Chunk List]
```

### 3. 임베딩 생성

```mermaid
graph LR
    A[Chunk List] --> B[EmbeddingModel]
    B --> C[배치 처리]
    C --> D[Vector List]
    D --> E[VectorStore]
```

## 사용법

### CLI 사용법

```bash
# PDF 문서 처리
python -m interfaces.cli.main documents process-pdf --file-path ./document.pdf

# JSON 문서 처리
python -m interfaces.cli.main documents process-json --file-path ./data.json

# 웹 페이지 처리
python -m interfaces.cli.main documents process-url --url https://example.com

# 문서 검색
python -m interfaces.cli.main documents search --query "IMU specifications"
```

### API 사용법

#### 1. 문서 업로드

```bash
# PDF 파일 업로드
curl -X POST "http://localhost:8000/api/documents/upload" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@document.pdf"

# JSON 데이터 업로드
curl -X POST "http://localhost:8000/api/documents/process-json" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test Doc", "content": "Document content..."}'
```

#### 2. 문서 검색

```bash
# 텍스트 검색
curl -X POST "http://localhost:8000/api/documents/search" \
  -H "Content-Type: application/json" \
  -d '{"query": "IMU specifications", "top_k": 5}'

# 고급 검색 (필터링)
curl -X POST "http://localhost:8000/api/documents/search" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "temperature sensor",
    "top_k": 10,
    "filters": {
      "source": "pdf",
      "created_after": "2024-01-01"
    }
  }'
```

#### 3. 문서 관리

```bash
# 문서 목록 조회
curl -X GET "http://localhost:8000/api/documents/"

# 특정 문서 조회
curl -X GET "http://localhost:8000/api/documents/{document_id}"

# 문서 삭제
curl -X DELETE "http://localhost:8000/api/documents/{document_id}"
```

## 설정 옵션

### 1. 텍스트 청킹 설정

```python
# config/settings.py
class ChunkingSettings(BaseSettings):
    chunk_size: int = 1000          # 청크 크기 (문자 수)
    chunk_overlap: int = 200        # 청크 간 오버랩
    chunking_strategy: str = "recursive"  # 청킹 전략
```

### 2. 임베딩 설정

```python
class EmbeddingSettings(BaseSettings):
    model_name: str = "text-embedding-3-small"
    batch_size: int = 100           # 배치 크기
    max_retries: int = 3            # 재시도 횟수
```

### 3. 벡터 저장소 설정

```python
class VectorStoreSettings(BaseSettings):
    collection_name: str = "documents"
    vector_size: int = 1536         # 벡터 차원
    distance_metric: str = "cosine" # 거리 메트릭
```

## 고급 기능

### 1. 메타데이터 추출

```python
# PDF 메타데이터
metadata = {
    "title": "Document Title",
    "author": "Author Name",
    "creation_date": "2024-01-01",
    "page_count": 10,
    "file_size": 1024000
}

# 웹 페이지 메타데이터
metadata = {
    "title": "Page Title",
    "url": "https://example.com",
    "scraped_at": "2024-01-01T10:00:00Z",
    "content_type": "text/html"
}
```

### 2. 텍스트 전처리

```python
class TextPreprocessor:
    def clean_text(self, text: str) -> str:
        # HTML 태그 제거
        text = re.sub(r'<[^>]+>', '', text)
        
        # 특수 문자 정리
        text = re.sub(r'[^\w\s]', ' ', text)
        
        # 공백 정리
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
```

### 3. 청킹 전략

#### Recursive Text Splitter
```python
class RecursiveTextSplitter:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.separators = ["\n\n", "\n", " ", ""]
```

#### Semantic Text Splitter
```python
class SemanticTextSplitter:
    def __init__(self, embedding_model, similarity_threshold=0.8):
        self.embedding_model = embedding_model
        self.similarity_threshold = similarity_threshold
```

## 성능 최적화

### 1. 배치 처리

```python
async def process_documents_batch(
    documents: List[Document],
    batch_size: int = 10
) -> List[ProcessingResult]:
    results = []
    
    for i in range(0, len(documents), batch_size):
        batch = documents[i:i + batch_size]
        batch_results = await asyncio.gather(
            *[process_single_document(doc) for doc in batch]
        )
        results.extend(batch_results)
    
    return results
```

### 2. 캐싱

```python
from functools import lru_cache

@lru_cache(maxsize=1000)
def get_document_embedding(content_hash: str) -> List[float]:
    # 이미 계산된 임베딩 반환
    pass
```

### 3. 스트리밍 처리

```python
async def process_large_document(file_path: str):
    async with aiofiles.open(file_path, 'r') as file:
        async for chunk in read_in_chunks(file, chunk_size=1024):
            await process_chunk(chunk)
```

## 에러 처리

### 1. 문서 로딩 에러

```python
class DocumentLoadingError(Exception):
    def __init__(self, source: str, reason: str):
        self.source = source
        self.reason = reason
        super().__init__(f"Failed to load document from {source}: {reason}")

try:
    document = await document_loader.load_document(source)
except DocumentLoadingError as e:
    logger.error(f"Document loading failed: {e}")
    # 에러 처리 로직
```

### 2. 임베딩 생성 에러

```python
class EmbeddingGenerationError(Exception):
    pass

async def generate_embeddings_with_retry(
    texts: List[str],
    max_retries: int = 3
) -> List[List[float]]:
    for attempt in range(max_retries):
        try:
            return await embedding_model.embed_texts(texts)
        except Exception as e:
            if attempt == max_retries - 1:
                raise EmbeddingGenerationError(f"Failed after {max_retries} attempts: {e}")
            await asyncio.sleep(2 ** attempt)  # 지수 백오프
```

## 모니터링 및 로깅

### 1. 처리 통계

```python
@dataclass
class ProcessingStats:
    total_documents: int
    successful_documents: int
    failed_documents: int
    total_chunks: int
    total_embeddings: int
    processing_time: float
```

### 2. 로깅 설정

```python
import logging

logger = logging.getLogger(__name__)

async def process_document_with_logging(document: Document):
    logger.info(f"Processing document: {document.id}")
    
    try:
        result = await process_document(document)
        logger.info(f"Successfully processed document: {document.id}")
        return result
    except Exception as e:
        logger.error(f"Failed to process document {document.id}: {e}")
        raise
```

## 테스트

### 1. 단위 테스트

```python
import pytest
from unittest.mock import Mock

@pytest.mark.asyncio
async def test_document_processing():
    # Mock 의존성
    mock_loader = Mock(spec=DocumentLoaderPort)
    mock_chunker = Mock(spec=TextChunkerPort)
    mock_embedding = Mock(spec=EmbeddingModelPort)
    
    # 테스트 실행
    use_case = DocumentProcessingUseCase(
        document_loader=mock_loader,
        text_chunker=mock_chunker,
        embedding_model=mock_embedding
    )
    
    result = await use_case.process_document("test.pdf")
    assert result.success is True
```

### 2. 통합 테스트

```python
@pytest.mark.integration
async def test_full_document_pipeline():
    # 실제 구현체 사용
    config = get_test_config()
    factory = AdapterFactory(config)
    
    document_loader = factory.create_document_loader()
    embedding_model = factory.create_embedding_model()
    vector_store = factory.create_vector_store()
    
    # 전체 파이프라인 테스트
    result = await process_test_document()
    assert result.total_embeddings > 0
```

## 문제 해결

### 1. 일반적인 문제

#### 메모리 부족
- 큰 문서를 작은 청크로 분할
- 배치 크기 줄이기
- 스트리밍 처리 사용

#### 임베딩 API 제한
- Rate limiting 구현
- 재시도 로직 추가
- 배치 크기 조정

#### 벡터 저장소 연결 실패
- 연결 상태 확인
- 재연결 로직 구현
- 헬스 체크 추가

### 2. 디버깅 도구

```python
# 문서 처리 상태 확인
async def debug_document_processing(document_id: str):
    document = await get_document(document_id)
    chunks = await get_document_chunks(document_id)
    embeddings = await get_document_embeddings(document_id)
    
    print(f"Document: {document.title}")
    print(f"Chunks: {len(chunks)}")
    print(f"Embeddings: {len(embeddings)}")
```

이 가이드를 통해 문서 시스템의 모든 기능을 효과적으로 활용할 수 있습니다.
