#!/usr/bin/env python3
"""
Pydantic 모델 통합 테스트
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

async def test_pydantic_integration():
    """Pydantic 모델 통합 테스트"""
    print("🔍 Pydantic 모델 통합 테스트")
    print("=" * 60)
    
    try:
        # 1. 스키마 임포트 테스트
        print("1️⃣ 스키마 임포트 테스트:")
        from schemas.document import DocumentSearchResponse, DocumentSearchResult
        print("✅ DocumentSearchResponse 임포트 성공")
        print("✅ DocumentSearchResult 임포트 성공")
        
        # 2. 유즈케이스 임포트 테스트
        print("\n2️⃣ 유즈케이스 임포트 테스트:")
        from core.usecases.document_retrieval import DocumentRetrievalUseCase
        print("✅ DocumentRetrievalUseCase 임포트 성공")
        
        # 3. 의존성 주입 테스트
        print("\n3️⃣ 의존성 주입 테스트:")
        from config.settings import config
        from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
        from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
        from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
        
        embedding_model = OpenAIEmbeddingAdapter(config)
        vector_store = QdrantVectorStoreAdapter()
        retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
        
        usecase = DocumentRetrievalUseCase(
            retriever=retriever,
            embedding_model=embedding_model,
            vector_store=vector_store,
            config=config
        )
        print("✅ 의존성 주입 성공")
        
        # 4. 실제 검색 테스트
        print("\n4️⃣ 실제 검색 테스트:")
        result = await usecase.search_documents(
            query_text="IMU specifications",
            top_k=2
        )
        
        print(f"📊 반환 타입: {type(result)}")
        print(f"📊 반환 클래스: {result.__class__}")
        print(f"📊 Pydantic 모델 여부: {hasattr(result, 'model_dump')}")
        
        # 5. Pydantic 모델 검증
        if hasattr(result, 'model_dump'):
            print("\n5️⃣ Pydantic 모델 검증:")
            model_dict = result.model_dump()
            print(f"✅ model_dump() 성공")
            print(f"📊 필드 개수: {len(model_dict)}")
            print(f"📊 주요 필드들: {list(model_dict.keys())}")
            
            # 개별 결과 검증
            if result.results:
                first_result = result.results[0]
                print(f"📊 개별 결과 타입: {type(first_result)}")
                print(f"📊 개별 결과 Pydantic 여부: {hasattr(first_result, 'model_dump')}")
                
                if hasattr(first_result, 'model_dump'):
                    result_dict = first_result.model_dump()
                    print(f"📊 개별 결과 필드들: {list(result_dict.keys())}")
        
        # 6. JSON 직렬화 테스트
        print("\n6️⃣ JSON 직렬화 테스트:")
        if hasattr(result, 'model_dump_json'):
            json_str = result.model_dump_json()
            print(f"✅ JSON 직렬화 성공 (길이: {len(json_str)})")
            
            # JSON 일부 출력
            import json
            json_obj = json.loads(json_str)
            print(f"📊 JSON 최상위 키들: {list(json_obj.keys())}")
        
        # 7. 스키마 검증 테스트
        print("\n7️⃣ 스키마 검증 테스트:")
        
        # 수동으로 Pydantic 모델 생성 테스트
        test_result = DocumentSearchResult(
            document_id="test-doc-id",
            chunk_id="test-chunk-id",
            content="Test content",
            score=0.95,
            rank=1,
            metadata={"test": "metadata"},
            is_chunk_result=True
        )
        print("✅ DocumentSearchResult 수동 생성 성공")
        
        test_response = DocumentSearchResponse(
            success=True,
            query_id="test-query-id",
            query_text="test query",
            results_count=1,
            results=[test_result],
            retriever_type="test_retriever",
            collection_name="test_collection"
        )
        print("✅ DocumentSearchResponse 수동 생성 성공")
        
        print(f"\n✅ Pydantic 모델 통합 테스트 완료")
        return True
        
    except Exception as e:
        print(f"❌ 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(test_pydantic_integration())
    if success:
        print("\n🎉 모든 테스트 통과!")
    else:
        print("\n💥 테스트 실패!")
        sys.exit(1)
