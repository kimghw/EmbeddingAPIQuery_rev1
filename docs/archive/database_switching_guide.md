# 데이터베이스 변경 가이드

## 🔄 현재 상황: 2개의 벡터 데이터베이스

### 현재 사용 가능한 데이터베이스:
1. **Qdrant** - 실제 벡터 데이터베이스 (운영용)
2. **Mock** - 가짜 데이터베이스 (테스트용)
3. **FAISS** - 설치됨 (구현 대기)

## 🛠️ 데이터베이스 변경 방법

### 방법 1: 코드에서 직접 변경 (현재 방식)

#### CLI에서 변경:
```python
# interfaces/cli/main.py

# 현재 (Qdrant 사용)
vector_store = QdrantVectorStoreAdapter()

# 변경 (Mock으로 교체)
vector_store = MockVectorStoreAdapter()
```

#### API에서 변경:
```python
# interfaces/api/documents.py

# 현재 (Qdrant 사용)
vector_store = QdrantVectorStoreAdapter()

# 변경 (Mock으로 교체)
vector_store = MockVectorStoreAdapter()
```

### 방법 2: 어댑터 팩토리 사용 (권장)

#### 팩토리로 변경:
```python
# interfaces/cli/main.py
from config.adapter_factory import AdapterFactory

# 현재
vector_store = AdapterFactory.create_vector_store_adapter("qdrant")

# 변경
vector_store = AdapterFactory.create_vector_store_adapter("mock")
```

### 방법 3: 환경변수로 변경 (가장 편리)

#### .env 파일 설정:
```bash
# .env
VECTOR_STORE_TYPE=qdrant  # 현재
# VECTOR_STORE_TYPE=mock  # 변경 시
```

#### 설정 클래스 확장:
```python
# config/settings.py
class Settings(BaseSettings):
    # 기존 설정들...
    vector_store_type: str = "qdrant"  # 기본값
    
    def get_vector_store_type(self) -> str:
        return self.vector_store_type
```

#### 코드에서 사용:
```python
# interfaces/cli/main.py
from config.adapter_factory import get_vector_store_adapter

# 환경변수에 따라 자동 선택
vector_store = get_vector_store_adapter(config)
```

## 🎯 실제 변경 예시

### 현재 CLI 코드 확인:
```python
# interfaces/cli/main.py 현재 상태
vector_store = QdrantVectorStoreAdapter()
```

### 변경 옵션들:

#### Option A: 직접 변경 (간단)
```python
# Qdrant → Mock으로 변경
# vector_store = QdrantVectorStoreAdapter()  # 주석 처리
vector_store = MockVectorStoreAdapter()      # 활성화
```

#### Option B: 팩토리 사용 (유연)
```python
# 팩토리로 변경
vector_store = AdapterFactory.create_vector_store_adapter("mock")
```

#### Option C: 설정 기반 (운영 권장)
```python
# 설정에 따라 자동 선택
vector_store = get_vector_store_adapter(config)
```

## 🔧 단계별 변경 가이드

### 1단계: 현재 상태 확인
```bash
# CLI로 현재 데이터베이스 확인
python -m interfaces.cli.main query "test"
```

### 2단계: 데이터베이스 변경
```python
# interfaces/cli/main.py에서 한 줄만 변경
vector_store = MockVectorStoreAdapter()  # Qdrant → Mock
```

### 3단계: 변경 확인
```bash
# 변경된 데이터베이스로 테스트
python -m interfaces.cli.main query "test"
```

## 🚀 고급 변경 방법

### 런타임 변경 (명령어 옵션)
```python
# CLI에 옵션 추가
@click.option('--db-type', default='qdrant', help='Vector database type')
def query(query_text: str, db_type: str):
    vector_store = AdapterFactory.create_vector_store_adapter(db_type)
    # ... 나머지 로직
```

### 사용법:
```bash
python -m interfaces.cli.main query "test" --db-type=mock
python -m interfaces.cli.main query "test" --db-type=qdrant
```

## 💡 권장 변경 방법

### 개발/테스트 환경:
```bash
# .env.development
VECTOR_STORE_TYPE=mock
```

### 운영 환경:
```bash
# .env.production  
VECTOR_STORE_TYPE=qdrant
```

### 코드는 동일:
```python
# 환경에 따라 자동 선택
vector_store = get_vector_store_adapter(config)
```

## 🎯 결론

**가장 쉬운 변경 방법:**
1. `interfaces/cli/main.py` 파일 열기
2. `vector_store = QdrantVectorStoreAdapter()` 찾기
3. `vector_store = MockVectorStoreAdapter()`로 변경
4. 저장 후 테스트

**한 줄만 바꾸면 전체 시스템의 데이터베이스가 바뀝니다!**
