# 🚨 이메일 시스템 문제 해결 가이드

## 📋 개요

이메일 시스템 운영 중 발생할 수 있는 다양한 문제들과 해결 방법을 정리한 문서입니다.

## 🔍 주요 문제 및 해결책

### 1. Qdrant 무한 루프 문제 ⚠️

#### 문제 증상
```
- /api/emails/list API 호출 시 무한 대기 (hang)
- 서버 CPU 사용률 급증
- 응답 없음 (timeout)
```

#### 근본 원인
```python
# ❌ 잘못된 Qdrant scroll API 사용
async def count_embeddings(self, collection_name: str) -> int:
    while True:  # 무한 루프 위험!
        result = self.client.scroll(
            collection_name=collection_name,
            offset=offset,  # ❌ 단순 숫자 증가 방식
        )
        offset += batch_size  # ❌ Qdrant에서 작동하지 않음
```

#### 해결 방법
```python
# ✅ 올바른 Qdrant scroll API 사용
async def count_embeddings(self, collection_name: str) -> int:
    count = 0
    next_page_offset = None
    max_iterations = 1000  # 안전장치
    
    while iterations < max_iterations:
        result = self.client.scroll(
            collection_name=collection_name,
            offset=next_page_offset,  # ✅ next_page_offset 사용
        )
        
        points, next_page_offset = result[0], result[1]
        count += len(points)
        
        if len(points) == 0 or next_page_offset is None:
            break  # ✅ 명확한 종료 조건
    
    return count
```

#### 예방 조치
- Qdrant 공식 문서 준수
- 무한 루프 방지를 위한 max_iterations 설정
- 페이지네이션 로직 테스트 강화

### 2. 이메일 JSON 파싱 오류

#### 문제 증상
```
ValueError: Invalid email JSON structure
KeyError: 'value'
AttributeError: 'NoneType' object has no attribute 'get'
```

#### 일반적인 원인
1. **Microsoft Graph JSON 구조 불일치**
2. **필수 필드 누락**
3. **잘못된 데이터 타입**

#### 해결 방법

##### 1. JSON 구조 검증 강화
```python
def validate_json_structure(self, json_data: Dict[str, Any]) -> bool:
    # Microsoft Graph 구조 확인
    if "@odata.context" not in json_data:
        logger.error("Missing @odata.context in JSON")
        return False
    
    # value 배열 확인
    if "value" not in json_data:
        logger.error("Missing 'value' array in JSON")
        return False
    
    # 첫 번째 이메일 구조 확인
    if json_data["value"]:
        first_email = json_data["value"][0]
        required_fields = ["id", "subject", "body", "sender"]
        
        for field in required_fields:
            if field not in first_email:
                logger.error(f"Missing required field: {field}")
                return False
    
    return True
```

##### 2. 안전한 데이터 추출
```python
def safe_extract_email_data(self, email_data: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "id": email_data.get("id", ""),
        "subject": email_data.get("subject", "No Subject"),
        "body_content": email_data.get("body", {}).get("content", ""),
        "sender_name": email_data.get("sender", {}).get("emailAddress", {}).get("name", "Unknown"),
        "sender_address": email_data.get("sender", {}).get("emailAddress", {}).get("address", ""),
        "created_datetime": self._parse_datetime(email_data.get("createdDateTime")),
    }
```

##### 3. 에러 복구 로직
```python
async def load_from_json_with_recovery(self, json_data: Dict[str, Any]) -> List[Email]:
    emails = []
    failed_count = 0
    
    for email_data in json_data.get("value", []):
        try:
            email = Email.from_graph_api(email_data)
            emails.append(email)
        except Exception as e:
            failed_count += 1
            logger.warning(f"Failed to parse email {email_data.get('id', 'unknown')}: {e}")
            continue
    
    logger.info(f"Successfully parsed {len(emails)} emails, failed: {failed_count}")
    return emails
```

### 3. 임베딩 생성 실패

#### 문제 증상
```
OpenAI API Error: Rate limit exceeded
OpenAI API Error: Invalid API key
TimeoutError: Request timeout
```

#### 해결 방법

##### 1. Rate Limiting 처리
```python
import asyncio
from tenacity import retry, stop_after_attempt, wait_exponential

class OpenAIEmbeddingAdapter:
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=4, max=10)
    )
    async def embed_texts(self, texts: List[str]) -> List[List[float]]:
        try:
            # 배치 크기 제한
            batch_size = 100
            all_embeddings = []
            
            for i in range(0, len(texts), batch_size):
                batch = texts[i:i + batch_size]
                
                response = await self.client.embeddings.create(
                    model=self.model_name,
                    input=batch
                )
                
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                # Rate limiting 방지
                await asyncio.sleep(0.1)
            
            return all_embeddings
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {e}")
            raise
```

##### 2. 대체 임베딩 모델
```python
async def embed_texts_with_fallback(self, texts: List[str]) -> List[List[float]]:
    try:
        # 1차: OpenAI API 시도
        return await self.openai_embedding.embed_texts(texts)
    except Exception as e:
        logger.warning(f"OpenAI embedding failed: {e}, trying fallback")
        
        try:
            # 2차: 로컬 모델 시도
            return await self.local_embedding.embed_texts(texts)
        except Exception as e2:
            logger.error(f"All embedding methods failed: {e2}")
            # 3차: 더미 벡터 반환 (개발/테스트용)
            return [[0.0] * 1536 for _ in texts]
```

##### 3. 컨텐츠 전처리
```python
def preprocess_content_for_embedding(self, content: str) -> str:
    # HTML 태그 제거
    import re
    clean_content = re.sub(r'<[^>]+>', '', content)
    
    # 특수 문자 정리
    clean_content = re.sub(r'[^\w\s가-힣]', ' ', clean_content)
    
    # 공백 정리
    clean_content = re.sub(r'\s+', ' ', clean_content).strip()
    
    # 길이 제한 (OpenAI 토큰 제한)
    max_length = 8000  # 안전 마진
    if len(clean_content) > max_length:
        clean_content = clean_content[:max_length]
    
    return clean_content
```

### 4. 벡터 스토어 연결 문제

#### 문제 증상
```
ConnectionError: Could not connect to Qdrant
TimeoutError: Qdrant request timeout
QdrantException: Collection not found
```

#### 해결 방법

##### 1. 연결 상태 확인
```python
async def check_vector_store_health(self) -> bool:
    try:
        # Qdrant 헬스 체크
        health = await self.vector_store.health_check()
        if not health:
            logger.error("Qdrant health check failed")
            return False
        
        # 컬렉션 존재 확인
        if not await self.vector_store.collection_exists("emails"):
            logger.warning("Email collection does not exist, creating...")
            await self.vector_store.create_collection(
                collection_name="emails",
                dimension=1536
            )
        
        return True
        
    except Exception as e:
        logger.error(f"Vector store health check failed: {e}")
        return False
```

##### 2. 자동 복구 로직
```python
async def ensure_vector_store_ready(self) -> VectorStorePort:
    # 1차: Qdrant 연결 시도
    try:
        if await self.qdrant_store.health_check():
            return self.qdrant_store
    except Exception as e:
        logger.warning(f"Qdrant connection failed: {e}")
    
    # 2차: FAISS 로컬 스토어 시도
    try:
        await self.faiss_store.initialize()
        logger.info("Switched to FAISS vector store")
        return self.faiss_store
    except Exception as e:
        logger.warning(f"FAISS initialization failed: {e}")
    
    # 3차: Mock 스토어 (개발/테스트용)
    logger.warning("Using Mock vector store as fallback")
    return self.mock_store
```

##### 3. 재연결 메커니즘
```python
class ResilientVectorStore:
    def __init__(self, primary_store, fallback_store):
        self.primary_store = primary_store
        self.fallback_store = fallback_store
        self.current_store = primary_store
        self.last_health_check = 0
        self.health_check_interval = 60  # 60초
    
    async def add_embeddings(self, embeddings: List[Embedding], collection_name: str):
        if await self._should_check_health():
            await self._check_and_switch_if_needed()
        
        try:
            return await self.current_store.add_embeddings(embeddings, collection_name)
        except Exception as e:
            logger.error(f"Primary store failed: {e}, switching to fallback")
            self.current_store = self.fallback_store
            return await self.current_store.add_embeddings(embeddings, collection_name)
```

### 5. 메모리 부족 문제

#### 문제 증상
```
MemoryError: Unable to allocate memory
OutOfMemoryError: CUDA out of memory
Process killed (OOM)
```

#### 해결 방법

##### 1. 배치 처리 최적화
```python
async def process_large_email_batch(self, emails: List[Email]) -> Dict[str, Any]:
    batch_size = 50  # 메모리에 따라 조정
    total_processed = 0
    
    for i in range(0, len(emails), batch_size):
        batch = emails[i:i + batch_size]
        
        try:
            # 배치 처리
            result = await self._process_email_batch(batch)
            total_processed += result['processed_count']
            
            # 메모리 정리
            import gc
            gc.collect()
            
            # 진행 상황 로깅
            logger.info(f"Processed {total_processed}/{len(emails)} emails")
            
        except Exception as e:
            logger.error(f"Batch processing failed: {e}")
            continue
    
    return {"total_processed": total_processed}
```

##### 2. 스트리밍 처리
```python
async def process_large_json_file(self, file_path: str):
    import ijson
    
    with open(file_path, 'rb') as file:
        # JSON 스트리밍 파싱
        emails = ijson.items(file, 'value.item')
        
        batch = []
        batch_size = 100
        
        for email_data in emails:
            batch.append(email_data)
            
            if len(batch) >= batch_size:
                # 배치 처리
                await self._process_email_batch(batch)
                batch = []
                
                # 메모리 정리
                gc.collect()
        
        # 마지막 배치 처리
        if batch:
            await self._process_email_batch(batch)
```

##### 3. 메모리 모니터링
```python
import psutil
import os

def monitor_memory_usage():
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    
    memory_mb = memory_info.rss / 1024 / 1024
    logger.info(f"Current memory usage: {memory_mb:.2f} MB")
    
    # 메모리 사용량이 임계치 초과 시 경고
    if memory_mb > 1000:  # 1GB
        logger.warning(f"High memory usage detected: {memory_mb:.2f} MB")
        
        # 강제 가비지 컬렉션
        import gc
        gc.collect()
```

### 6. API 응답 지연 문제

#### 문제 증상
```
Request timeout
Slow API response (> 30s)
Client disconnection
```

#### 해결 방법

##### 1. 비동기 처리
```python
from fastapi import BackgroundTasks

@router.post("/emails/process")
async def process_emails_async(
    email_data: dict,
    background_tasks: BackgroundTasks
):
    # 즉시 응답 반환
    task_id = str(uuid.uuid4())
    
    # 백그라운드에서 처리
    background_tasks.add_task(
        process_emails_background,
        task_id,
        email_data
    )
    
    return {
        "task_id": task_id,
        "status": "processing",
        "message": "Email processing started"
    }

async def process_emails_background(task_id: str, email_data: dict):
    try:
        result = await email_usecase.process_emails_from_json(email_data)
        # 결과를 캐시나 DB에 저장
        await save_task_result(task_id, result)
    except Exception as e:
        await save_task_error(task_id, str(e))
```

##### 2. 진행 상황 추적
```python
@router.get("/emails/process/{task_id}/status")
async def get_processing_status(task_id: str):
    status = await get_task_status(task_id)
    
    return {
        "task_id": task_id,
        "status": status.get("status", "unknown"),
        "progress": status.get("progress", 0),
        "result": status.get("result"),
        "error": status.get("error")
    }
```

##### 3. 타임아웃 설정
```python
from fastapi import HTTPException
import asyncio

async def process_with_timeout(email_data: dict, timeout: int = 300):
    try:
        result = await asyncio.wait_for(
            email_usecase.process_emails_from_json(email_data),
            timeout=timeout
        )
        return result
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=408,
            detail=f"Processing timeout after {timeout} seconds"
        )
```

## 🔧 디버깅 도구

### 1. 로그 분석
```bash
# 이메일 처리 관련 로그 필터링
grep "email" logs/app.log | tail -100

# 에러 로그만 확인
grep "ERROR" logs/app.log | grep "email"

# 특정 시간대 로그 확인
grep "2025-05-29 20:" logs/app.log
```

### 2. 헬스 체크 스크립트
```python
# check_email_system_health.py
async def check_email_system_health():
    checks = {
        "qdrant_connection": False,
        "openai_api": False,
        "email_collection": False,
        "embedding_generation": False
    }
    
    try:
        # Qdrant 연결 확인
        health = await vector_store.health_check()
        checks["qdrant_connection"] = health
        
        # OpenAI API 확인
        test_embedding = await embedding_model.embed_texts(["test"])
        checks["openai_api"] = len(test_embedding) > 0
        
        # 이메일 컬렉션 확인
        exists = await vector_store.collection_exists("emails")
        checks["email_collection"] = exists
        
        # 임베딩 생성 테스트
        test_result = await embedding_model.embed_texts(["Hello world"])
        checks["embedding_generation"] = len(test_result[0]) == 1536
        
    except Exception as e:
        logger.error(f"Health check failed: {e}")
    
    return checks
```

### 3. 성능 모니터링
```python
import time
from functools import wraps

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} completed in {execution_time:.2f}s")
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.2f}s: {e}")
            raise
    
    return wrapper
```

## 📊 모니터링 및 알림

### 1. 메트릭 수집
```python
# 주요 메트릭
metrics = {
    "emails_processed_total": 0,
    "emails_failed_total": 0,
    "embedding_generation_time_avg": 0.0,
    "vector_store_operations_total": 0,
    "api_response_time_avg": 0.0,
    "memory_usage_mb": 0.0,
    "error_rate_percent": 0.0
}
```

### 2. 알림 설정
```python
async def send_alert_if_needed(metric_name: str, value: float, threshold: float):
    if value > threshold:
        alert_message = f"ALERT: {metric_name} = {value} (threshold: {threshold})"
        
        # 로그 기록
        logger.critical(alert_message)
        
        # 외부 알림 (Slack, 이메일 등)
        await send_external_alert(alert_message)
```

## 🔗 관련 문서

- [이메일 시스템 가이드](05_email_system_guide.md)
- [성능 최적화](07_performance_optimization.md)
- [일반적인 문제](08_common_issues.md)
- [Qdrant 무한 루프 해결 보고서](qdrant_infinite_loop_fix_report.md)

---

**작성일**: 2025-05-29  
**버전**: 1.0  
**상태**: 활성
