# 메타데이터 누락 문제 분석 및 수정 계획

## 🔍 **문제 분석**

### **호출 스택 분석**
```
JSON 파일 → JsonEmailLoaderAdapter → Email 엔티티 → EmailProcessingUseCase → EmailEmbedding → QdrantVectorStoreAdapter
```

### **메타데이터 누락 원인**
1. **EmailProcessingUseCase._store_email_embeddings()** 에서 메타데이터를 올바르게 생성
2. **QdrantVectorStoreAdapter.add_embeddings()** 에서 payload 구조 문제
3. **현재 저장된 데이터**: 벡터만 있고 payload(메타데이터) 누락

### **현재 코드 문제점**
```python
# EmailProcessingUseCase._store_email_embeddings() - 올바름
payload = {
    "email_id": email_emb.email_id,
    "embedding_type": email_emb.embedding_type,
    "content": email_emb.content,
    # ... 모든 메타데이터 필드들
}

# QdrantVectorStoreAdapter.add_embeddings() - 문제
payload = {
    "document_id": embedding.document_id,
    "chunk_id": embedding.chunk_id,
    "metadata": embedding.metadata or {}  # 중첩 구조로 저장됨
}
```

## 🔧 **수정 계획**

### **1단계: QdrantVectorStoreAdapter 수정**
- `add_embeddings()` 메서드에서 메타데이터를 평면화(flatten)하여 저장
- 이메일 전용 필드들을 최상위 레벨로 이동

### **2단계: 기존 데이터 재처리**
- emails 컬렉션 삭제
- sample_emails.json 다시 로드
- 수정된 어댑터로 재저장

### **3단계: 검증**
- 메타데이터 저장 확인
- Thread/Sender 검색 테스트

## 📝 **구체적 수정 사항**

### **QdrantVectorStoreAdapter.add_embeddings() 수정**
```python
# 기존 (문제)
payload = {
    "document_id": embedding.document_id,
    "metadata": embedding.metadata or {}
}

# 수정 후 (해결)
payload = {
    "document_id": embedding.document_id,
    "chunk_id": embedding.chunk_id,
    # 메타데이터를 최상위로 평면화
    **embedding.metadata,  # 모든 메타데이터 필드를 최상위로
}
```

### **EmailEmbedding 메타데이터 구조 확인**
- `correspondence_thread`: 스레드 ID
- `sender_address`: 발신자 이메일
- `subject`: 이메일 제목
- `embedding_type`: subject/body 구분

## 🚀 **실행 순서**

1. **QdrantVectorStoreAdapter 수정**
2. **기존 emails 컬렉션 삭제**
3. **이메일 데이터 재처리**
4. **메타데이터 저장 확인**
5. **검색 기능 테스트**

## 📊 **예상 결과**

### **수정 전**
```json
{
  "id": "email_id_subject",
  "vector": [...],
  "payload": {}  // 비어있음
}
```

### **수정 후**
```json
{
  "id": "email_id_subject",
  "vector": [...],
  "payload": {
    "email_id": "...",
    "embedding_type": "subject",
    "correspondence_thread": "PL25008aKRd",
    "sender_address": "Darko.Dominovic@crs.hr",
    "subject": "PL25008aKRd - MSC 110/5...",
    "content": "...",
    "created_time": "2025-05-29T02:01:56Z"
  }
}
```

이렇게 수정하면 Thread/Sender 검색이 정상 작동할 것입니다.
