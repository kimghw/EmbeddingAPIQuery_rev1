# 어댑터 교체 가이드

## 🎯 포트/어댑터 패턴의 핵심 장점

**"기존 DB나 모듈을 교체하려면 어댑터를 새로 만들어야 하는 구나?"** - 맞습니다!

이것이 바로 **포트/어댑터 패턴**의 핵심 가치입니다.

## 📋 어댑터 교체 과정

### 1. 새로운 어댑터 생성
```python
# adapters/vector_store/new_vector_store.py
class NewVectorStoreAdapter(VectorStorePort):
    """새로운 벡터 저장소 어댑터"""
    
    async def create_collection(self, collection_name: str, vector_dimension: int) -> bool:
        # 새로운 벡터 DB 구현
        pass
    
    async def store_chunks(self, chunks: List[DocumentChunk], collection_name: str) -> bool:
        # 새로운 저장 로직
        pass
    
    async def search_similar(self, query_embedding: List[float], collection_name: str, limit: int = 10, score_threshold: float = 0.0) -> List[RetrievalResult]:
        # 새로운 검색 로직
        pass
```

### 2. 의존성 주입 변경 (한 줄만!)

#### CLI에서 교체:
```python
# interfaces/cli/main.py
# 기존
vector_store = QdrantVectorStoreAdapter()

# 변경
vector_store = NewVectorStoreAdapter()
```

#### API에서 교체:
```python
# interfaces/api/documents.py
# 기존
vector_store = QdrantVectorStoreAdapter()

# 변경  
vector_store = NewVectorStoreAdapter()
```

### 3. 교체 완료!
- ✅ CORE 로직 변경 없음
- ✅ 비즈니스 로직 재사용
- ✅ 테스트 코드 재사용
- ✅ CLI/API 인터페이스 동일

## 🔄 지원 가능한 교체 시나리오

### 벡터 저장소 교체
- **Qdrant** → **FAISS** → **Pinecone** → **Chroma**
- 동일한 `VectorStorePort` 인터페이스 구현

### 임베딩 모델 교체  
- **OpenAI** → **HuggingFace** → **Cohere**
- 동일한 `EmbeddingModelPort` 인터페이스 구현

### 문서 로더 교체
- **PyPDF** → **PyMuPDF** → **Unstructured**
- 동일한 `DocumentLoaderPort` 인터페이스 구현

### 텍스트 청킹 교체
- **RecursiveCharacter** → **Semantic** → **Token-based**
- 동일한 `TextChunkerPort` 인터페이스 구현

## 📊 실제 테스트 결과

```bash
=== 어댑터 교체 테스트 ===

1. Qdrant 어댑터로 검색:
   - 결과 수: 2
   - 첫 번째 결과 점수: 0.2750
   - 내용 미리보기: the harshest environments, the 3DM-GV7 features a...

2. Mock 어댑터로 교체:
   - 결과 수: 0
   - Mock은 가짜 데이터 반환 (정상)

=== 어댑터 교체의 핵심 ===
✅ CORE 로직 변경 없음
✅ 포트 인터페이스 동일  
✅ 의존성 주입만 변경
✅ 비즈니스 로직 재사용
```

## 🏗️ 아키텍처 장점

### 1. 확장성 (Extensibility)
- 새로운 기술 스택 쉽게 추가
- 기존 코드 영향 없음

### 2. 테스트 용이성 (Testability)  
- Mock 어댑터로 단위 테스트
- 실제 외부 의존성 없이 테스트

### 3. 유지보수성 (Maintainability)
- 각 어댑터 독립적 수정
- 버그 격리 효과

### 4. 비즈니스 로직 보호
- CORE는 외부 변화에 영향받지 않음
- 도메인 지식 보존

## 💡 핵심 포인트

> **"어댑터만 바꾸면 전체 시스템의 기술 스택이 바뀐다!"**

이것이 바로 **클린 아키텍처**와 **포트/어댑터 패턴**의 진정한 가치입니다.

- 🔄 **기술 변화에 유연하게 대응**
- 🛡️ **비즈니스 로직 안정성 보장**  
- 🚀 **빠른 프로토타이핑과 실험**
- 🧪 **A/B 테스트 용이성**
