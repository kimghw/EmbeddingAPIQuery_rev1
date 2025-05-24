#!/usr/bin/env python3
"""
스키마 임포트 실패 원인 확인
"""

import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

def check_schema_issue():
    """스키마 임포트 실패 원인 확인"""
    print("🔍 스키마 임포트 실패 원인 확인")
    print("=" * 60)
    
    # 1. schemas.document 모듈에서 사용 가능한 클래스들 확인
    try:
        import schemas.document as doc_schema
        print("✅ schemas.document 모듈 임포트 성공")
        
        # 모듈에서 사용 가능한 모든 클래스/함수 확인
        available_items = [item for item in dir(doc_schema) if not item.startswith('_')]
        print(f"📊 사용 가능한 항목들: {available_items}")
        
        # Pydantic 모델들만 필터링
        pydantic_models = []
        for item_name in available_items:
            item = getattr(doc_schema, item_name)
            if hasattr(item, '__bases__') and any('BaseModel' in str(base) for base in item.__bases__):
                pydantic_models.append(item_name)
        
        print(f"📊 Pydantic 모델들: {pydantic_models}")
        
    except ImportError as e:
        print(f"❌ schemas.document 모듈 임포트 실패: {e}")
        return
    
    # 2. 개별 클래스 임포트 테스트
    print(f"\n2️⃣ 개별 클래스 임포트 테스트:")
    
    test_classes = [
        'DocumentSearchResult',
        'DocumentSearchResponse', 
        'DocumentChunk',  # 이게 없어서 실패
        'DocumentChunkResponse',
        'DocumentUploadRequest',
        'DocumentUploadResponse'
    ]
    
    for class_name in test_classes:
        try:
            cls = getattr(doc_schema, class_name)
            print(f"✅ {class_name}: {cls}")
        except AttributeError:
            print(f"❌ {class_name}: 클래스가 존재하지 않음")
    
    # 3. 실제 필요한 클래스들 확인
    print(f"\n3️⃣ 실제 필요한 클래스들:")
    
    # DocumentSearchResult 확인
    try:
        from schemas.document import DocumentSearchResult
        print(f"✅ DocumentSearchResult 임포트 성공: {DocumentSearchResult}")
        
        # 필드 확인
        if hasattr(DocumentSearchResult, 'model_fields'):
            print(f"📊 DocumentSearchResult 필드들: {list(DocumentSearchResult.model_fields.keys())}")
        elif hasattr(DocumentSearchResult, '__fields__'):
            print(f"📊 DocumentSearchResult 필드들: {list(DocumentSearchResult.__fields__.keys())}")
            
    except ImportError as e:
        print(f"❌ DocumentSearchResult 임포트 실패: {e}")
    
    # DocumentSearchResponse 확인
    try:
        from schemas.document import DocumentSearchResponse
        print(f"✅ DocumentSearchResponse 임포트 성공: {DocumentSearchResponse}")
        
        # 필드 확인
        if hasattr(DocumentSearchResponse, 'model_fields'):
            print(f"📊 DocumentSearchResponse 필드들: {list(DocumentSearchResponse.model_fields.keys())}")
        elif hasattr(DocumentSearchResponse, '__fields__'):
            print(f"📊 DocumentSearchResponse 필드들: {list(DocumentSearchResponse.__fields__.keys())}")
            
    except ImportError as e:
        print(f"❌ DocumentSearchResponse 임포트 실패: {e}")
    
    # 4. 검색 결과와 스키마 매핑 확인
    print(f"\n4️⃣ 검색 결과와 스키마 매핑 확인:")
    
    # 실제 검색 결과 구조
    actual_result_keys = [
        'document_id', 'chunk_id', 'content', 'score', 'rank', 'metadata', 'is_chunk_result'
    ]
    print(f"📊 실제 검색 결과 키들: {actual_result_keys}")
    
    # DocumentSearchResult 스키마와 비교
    try:
        from schemas.document import DocumentSearchResult
        if hasattr(DocumentSearchResult, 'model_fields'):
            schema_keys = list(DocumentSearchResult.model_fields.keys())
        elif hasattr(DocumentSearchResult, '__fields__'):
            schema_keys = list(DocumentSearchResult.__fields__.keys())
        else:
            schema_keys = []
            
        print(f"📊 DocumentSearchResult 스키마 키들: {schema_keys}")
        
        # 매핑 확인
        missing_in_schema = set(actual_result_keys) - set(schema_keys)
        missing_in_actual = set(schema_keys) - set(actual_result_keys)
        
        if missing_in_schema:
            print(f"⚠️  스키마에 없는 실제 키들: {missing_in_schema}")
        if missing_in_actual:
            print(f"⚠️  실제 결과에 없는 스키마 키들: {missing_in_actual}")
        
        if not missing_in_schema and not missing_in_actual:
            print(f"✅ 스키마와 실제 결과가 완벽히 매칭됨")
            
    except Exception as e:
        print(f"❌ 스키마 매핑 확인 실패: {e}")
    
    print(f"\n✅ 스키마 확인 완료")


if __name__ == "__main__":
    check_schema_issue()
