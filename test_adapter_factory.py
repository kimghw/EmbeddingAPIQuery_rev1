"""
어댑터 팩토리 테스트 - 설정을 통한 어댑터 교체
"""

import asyncio
from config.settings import config
from config.adapter_factory import AdapterFactory
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from core.entities.document import Query


async def test_adapter_factory():
    """어댑터 팩토리를 통한 어댑터 교체 테스트"""
    
    print("=== 어댑터 팩토리 테스트 ===\n")
    
    query = Query.create("What is the operating temperature range?")
    
    # 1. Qdrant 어댑터 (기본값)
    print("1. Qdrant 어댑터 (팩토리로 생성):")
    try:
        vector_store = AdapterFactory.create_vector_store_adapter("qdrant")
        embedding_model = AdapterFactory.create_embedding_adapter("openai", config)
        retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
        retriever.set_collection_name(config.get_collection_name())
        
        results = await retriever.retrieve(query, top_k=2)
        print(f"   - 결과 수: {len(results)}")
        if results:
            print(f"   - 첫 번째 결과 점수: {results[0].score:.4f}")
            print(f"   - 내용: {results[0].content[:50]}...")
    except Exception as e:
        print(f"   - Qdrant 테스트 실패: {e}")
    
    print()
    
    # 2. Mock 어댑터 (팩토리로 교체)
    print("2. Mock 어댑터 (팩토리로 교체):")
    try:
        vector_store = AdapterFactory.create_vector_store_adapter("mock")
        embedding_model = AdapterFactory.create_embedding_adapter("openai", config)
        retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
        
        results = await retriever.retrieve(query, top_k=2)
        print(f"   - 결과 수: {len(results)}")
        print("   - Mock 어댑터는 빈 결과 반환 (정상)")
    except Exception as e:
        print(f"   - Mock 테스트 실패: {e}")
    
    print()
    
    # 3. FAISS 어댑터 (팩토리로 교체)
    print("3. FAISS 어댑터 (팩토리로 교체):")
    try:
        vector_store = AdapterFactory.create_vector_store_adapter("faiss")
        embedding_model = AdapterFactory.create_embedding_adapter("openai", config)
        retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
        
        results = await retriever.retrieve(query, top_k=2)
        print(f"   - 결과 수: {len(results)}")
        print("   - FAISS는 새 인덱스라서 데이터가 없음 (정상)")
    except Exception as e:
        print(f"   - FAISS 테스트 실패: {e}")
    
    print()
    
    # 4. 지원하지 않는 어댑터 타입
    print("4. 지원하지 않는 어댑터 타입 테스트:")
    try:
        vector_store = AdapterFactory.create_vector_store_adapter("unsupported")
    except ValueError as e:
        print(f"   - 예상된 오류: {e}")
    
    print()
    
    # 5. 다른 어댑터들도 테스트
    print("5. 다른 어댑터 타입들:")
    
    # 문서 로더
    try:
        doc_loader = AdapterFactory.create_document_loader_adapter("pdf")
        print("   - PDF 로더 생성 성공")
    except Exception as e:
        print(f"   - PDF 로더 생성 실패: {e}")
    
    # 텍스트 청킹
    try:
        text_chunker = AdapterFactory.create_text_chunker_adapter("recursive", 1000, 200)
        print("   - Recursive 청킹 어댑터 생성 성공")
    except Exception as e:
        print(f"   - 청킹 어댑터 생성 실패: {e}")
    
    print("\n=== 어댑터 팩토리의 장점 ===")
    print("✅ 중앙화된 어댑터 생성 관리")
    print("✅ 타입 안전성 보장")
    print("✅ 설정 기반 어댑터 선택")
    print("✅ 확장 가능한 구조")
    print("✅ 의존성 주입 간소화")


if __name__ == "__main__":
    asyncio.run(test_adapter_factory())
