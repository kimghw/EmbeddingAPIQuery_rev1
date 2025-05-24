#!/usr/bin/env python3
"""
검색 결과 딕셔너리 원본 출력 및 Pydantic 사용 여부 확인
"""

import sys
import asyncio
import json
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import create_config
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter, get_retriever_adapter
from core.usecases.document_retrieval import DocumentRetrievalUseCase


async def show_raw_output():
    """검색 결과 딕셔너리 원본 출력 및 Pydantic 사용 여부 확인"""
    print("🔍 검색 결과 딕셔너리 원본 출력 및 Pydantic 확인")
    print("=" * 80)
    
    try:
        # 설정 로드
        config = create_config()
        
        # 어댑터 생성
        vector_store = get_vector_store_adapter(config)
        embedding_model = get_embedding_adapter(config)
        retriever = get_retriever_adapter(config)
        
        # 검색 유즈케이스 생성
        retrieval_usecase = DocumentRetrievalUseCase(
            vector_store=vector_store,
            embedding_model=embedding_model,
            retriever=retriever,
            config=config
        )
        
        # 검색 실행
        query = "IMU specifications"
        print(f"🔍 검색 쿼리: '{query}'")
        
        search_result = await retrieval_usecase.search_documents(query, top_k=2)
        
        # 1. 원본 딕셔너리 출력
        print(f"\n1️⃣ 반환된 딕셔너리 원본:")
        print("=" * 60)
        print(json.dumps(search_result, indent=2, ensure_ascii=False))
        print("=" * 60)
        
        # 2. Pydantic 사용 여부 확인
        print(f"\n2️⃣ Pydantic 사용 여부 확인:")
        print(f"📊 최상위 객체 타입: {type(search_result)}")
        print(f"📊 최상위 객체 클래스: {search_result.__class__}")
        print(f"📊 최상위 객체 모듈: {search_result.__class__.__module__}")
        
        # Pydantic 모델인지 확인
        is_pydantic = hasattr(search_result, 'model_dump') or hasattr(search_result, 'dict')
        print(f"📊 Pydantic 모델 여부: {is_pydantic}")
        
        if hasattr(search_result, '__dict__'):
            print(f"📊 객체 속성들: {list(search_result.__dict__.keys())}")
        
        # 3. 개별 결과 항목 Pydantic 확인
        if isinstance(search_result, dict) and 'results' in search_result:
            results = search_result['results']
            if results and len(results) > 0:
                first_result = results[0]
                print(f"\n3️⃣ 개별 결과 항목 Pydantic 확인:")
                print(f"📊 개별 결과 타입: {type(first_result)}")
                print(f"📊 개별 결과 클래스: {first_result.__class__}")
                print(f"📊 개별 결과 모듈: {first_result.__class__.__module__}")
                
                is_result_pydantic = hasattr(first_result, 'model_dump') or hasattr(first_result, 'dict')
                print(f"📊 개별 결과 Pydantic 모델 여부: {is_result_pydantic}")
        
        # 4. 스키마 파일 확인
        print(f"\n4️⃣ 스키마 파일 확인:")
        try:
            from schemas.document import DocumentSearchResult, DocumentChunk
            print(f"✅ DocumentSearchResult 스키마 존재: {DocumentSearchResult}")
            print(f"✅ DocumentChunk 스키마 존재: {DocumentChunk}")
            
            # Pydantic 모델인지 확인
            print(f"📊 DocumentSearchResult 베이스 클래스: {DocumentSearchResult.__bases__}")
            print(f"📊 DocumentChunk 베이스 클래스: {DocumentChunk.__bases__}")
            
        except ImportError as e:
            print(f"❌ 스키마 임포트 실패: {e}")
        
        # 5. 유즈케이스에서 반환 타입 확인
        print(f"\n5️⃣ 유즈케이스 반환 타입 확인:")
        import inspect
        signature = inspect.signature(retrieval_usecase.search_documents)
        print(f"📊 search_documents 시그니처: {signature}")
        
        # 유즈케이스 소스 코드 확인
        try:
            source_lines = inspect.getsource(retrieval_usecase.search_documents)
            print(f"📊 search_documents 소스 코드 일부:")
            lines = source_lines.split('\n')[:10]  # 첫 10줄만
            for i, line in enumerate(lines):
                print(f"   {i+1:2d}: {line}")
        except Exception as e:
            print(f"❌ 소스 코드 확인 실패: {e}")
        
        print(f"\n✅ 원본 출력 및 Pydantic 확인 완료")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(show_raw_output())
