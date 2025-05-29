# Mock 클래스 정리 전략

## 문제 상황

맞습니다! **Mock 클래스를 의존성 주입 코드에 직접 넣으면 코드가 삭제되지 않고 남아있게 됩니다.**

### 문제가 되는 패턴
```python
# ❌ 문제: Mock 클래스가 프로덕션 코드에 남아있음
async def get_email_retriever() -> EmailRetrievalUseCase:
    embedding_model = MockEmbeddingModel()  # 🚨 이 코드가 삭제되지 않음
    config = MockConfig()                   # 🚨 이 코드가 삭제되지 않음
    vector_store = MockVectorStore()        # 🚨 이 코드가 삭제되지 않음
    
    return EmailRetrievalUseCase(...)
```

## Mock 클래스 정리 전략

### 1. 즉시 삭제 전략 (권장)

#### ✅ 테스트 완료 후 Mock 클래스 즉시 삭제
```python
# Step 1: Mock 클래스 제거
# 파일에서 MockEmbeddingModel, MockConfig 등 클래스 정의 삭제

# Step 2: 어댑터 팩토리로 교체
async def get_email_retriever() -> EmailRetrievalUseCase:
    # ✅ 팩토리 함수 사용 (환경에 따라 자동 선택)
    embedding_model = get_embedding_model()
    vector_store = get_vector_store()
    retriever = get_retriever()
    
    return EmailRetrievalUseCase(...)
```

### 2. 단계적 정리 전략

#### Phase 1: Mock 클래스를 별도 파일로 분리
```python
# adapters/mock/mock_embedding.py (새 파일)
class MockEmbeddingModel:
    pass

# adapters/mock/mock_config.py (새 파일)  
class MockConfig:
    pass
```

#### Phase 2: 조건부 import로 변경
```python
# interfaces/api/email_search_routes.py
async def get_email_retriever() -> EmailRetrievalUseCase:
    # 환경변수로 제어
    if os.getenv("USE_MOCK", "false").lower() == "true":
        from adapters.mock.mock_embedding import MockEmbeddingModel
        from adapters.mock.mock_config import MockConfig
        embedding_model = MockEmbeddingModel()
        config = MockConfig()
    else:
        # 실제 구현체 사용
        embedding_model = get_embedding_model()
        config = get_config()
    
    return EmailRetrievalUseCase(...)
```

#### Phase 3: Mock 파일들 삭제
```bash
# Mock 파일들 완전 삭제
rm -rf adapters/mock/
```

### 3. 자동화된 정리 스크립트

#### Mock 클래스 탐지 스크립트
```python
# scripts/detect_mock_usage.py
import os
import re

def find_mock_classes():
    """프로덕션 코드에서 Mock 클래스 사용 탐지"""
    mock_patterns = [
        r'class\s+Mock\w+',
        r'MockEmbeddingModel\(\)',
        r'MockConfig\(\)',
        r'MockVectorStore\(\)'
    ]
    
    for root, dirs, files in os.walk('.'):
        # tests 디렉토리는 제외
        if 'tests' in root or 'test_' in root:
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                    
                for pattern in mock_patterns:
                    if re.search(pattern, content):
                        print(f"🚨 Mock 발견: {filepath}")
                        print(f"   패턴: {pattern}")

if __name__ == "__main__":
    find_mock_classes()
```

#### Mock 클래스 자동 제거 스크립트
```python
# scripts/cleanup_mocks.py
import os
import re

def remove_mock_classes():
    """Mock 클래스 정의 자동 제거"""
    mock_class_pattern = r'class\s+Mock\w+:.*?(?=\n\nclass|\n\ndef|\Z)'
    
    for root, dirs, files in os.walk('.'):
        if 'tests' in root:  # 테스트 파일은 제외
            continue
            
        for file in files:
            if file.endswith('.py'):
                filepath = os.path.join(root, file)
                with open(filepath, 'r') as f:
                    content = f.read()
                
                # Mock 클래스 정의 제거
                new_content = re.sub(mock_class_pattern, '', content, flags=re.DOTALL)
                
                if new_content != content:
                    print(f"🧹 Mock 클래스 제거: {filepath}")
                    with open(filepath, 'w') as f:
                        f.write(new_content)

if __name__ == "__main__":
    remove_mock_classes()
```

### 4. CI/CD 파이프라인에 Mock 검증 추가

#### GitHub Actions 예시
```yaml
# .github/workflows/mock-check.yml
name: Mock Class Check
on: [push, pull_request]

jobs:
  check-mocks:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v2
    - name: Check for Mock classes in production code
      run: |
        python scripts/detect_mock_usage.py
        if [ $? -eq 0 ]; then
          echo "❌ Mock 클래스가 프로덕션 코드에서 발견되었습니다!"
          exit 1
        fi
```

### 5. 코드 리뷰 체크리스트

#### PR 리뷰 시 확인사항
- [ ] Mock 클래스가 새로 추가되었는가?
- [ ] Mock 클래스가 프로덕션 코드에 직접 인스턴스화되고 있는가?
- [ ] 어댑터 팩토리 패턴을 사용하고 있는가?
- [ ] 테스트 완료 후 Mock 클래스 삭제 계획이 있는가?

#### 삭제 체크리스트
- [ ] Mock 클래스 정의 삭제
- [ ] Mock 클래스 import 문 삭제
- [ ] Mock 클래스 인스턴스화 코드 삭제
- [ ] 어댑터 팩토리로 교체 완료
- [ ] 테스트 실행하여 정상 동작 확인

### 6. 권장 워크플로우

#### 개발 시작 시
```python
# 1. 처음부터 어댑터 팩토리 사용
async def get_email_retriever() -> EmailRetrievalUseCase:
    embedding_model = get_embedding_model()  # 환경에 따라 자동 선택
    return EmailRetrievalUseCase(...)

# 2. 환경변수로 Mock 제어
# .env
EMBEDDING_TYPE=mock  # 개발 시
EMBEDDING_TYPE=openai  # 프로덕션 시
```

#### 기존 Mock 코드 정리 시
```bash
# 1. Mock 탐지
python scripts/detect_mock_usage.py

# 2. 어댑터 팩토리로 교체
# (수동으로 코드 수정)

# 3. Mock 클래스 삭제
python scripts/cleanup_mocks.py

# 4. 테스트 실행
python -m pytest

# 5. 서버 실행 테스트
uvicorn main:app --reload
```

## 결론

**Mock 클래스는 테스트 완료 후 즉시 삭제하는 것이 가장 안전합니다.**

1. **즉시 삭제**: 테스트 완료 → Mock 클래스 삭제 → 어댑터 팩토리로 교체
2. **자동화**: 스크립트로 Mock 탐지 및 제거 자동화
3. **CI/CD 검증**: 파이프라인에서 Mock 사용 여부 자동 검증
4. **코드 리뷰**: PR에서 Mock 사용 패턴 체크

이렇게 하면 Mock 클래스가 프로덕션에 남아있는 문제를 완전히 예방할 수 있습니다.
