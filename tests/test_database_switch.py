"""
데이터베이스 변경 테스트 - 실제 CLI 코드 수정 예시
"""

import asyncio
from config.settings import config
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from core.entities.document import Query


async def test_database_switch():
    """데이터베이스 변경 테스트"""
    
    print("=== 데이터베이스 변경 테스트 ===\n")
    
    # 공통 컴포넌트
    embedding_model = OpenAIEmbeddingAdapter(config)
    query = Query.create("What is the operating temperature range?")
    
    print("현재 CLI에서 사용하는 방식:")
    print("interfaces/cli/main.py의 search_documents 함수에서:")
    print("vector_store = QdrantVectorStoreAdapter(...)")
    print()
    
    # 1. 현재 방식 (Qdrant)
    print("1. 현재 데이터베이스 (Qdrant):")
    try:
        vector_store = QdrantVectorStoreAdapter(
            host="localhost",
            port=6333,
            vector_dimension=config.get_vector_dimension()
        )
        
        # Health check
        is_healthy = await vector_store.health_check()
        if is_healthy:
            retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
            retriever.set_collection_name(config.get_collection_name())
            
            results = await retriever.retrieve(query, top_k=2)
            print(f"   ✅ Qdrant 연결 성공")
            print(f"   - 결과 수: {len(results)}")
            if results:
                print(f"   - 첫 번째 결과 점수: {results[0].score:.4f}")
        else:
            print("   ❌ Qdrant 서버가 실행되지 않음")
    except Exception as e:
        print(f"   ❌ Qdrant 연결 실패: {e}")
    
    print()
    
    # 2. 변경된 방식 (Mock)
    print("2. 변경된 데이터베이스 (Mock):")
    print("   코드 변경: vector_store = MockVectorStoreAdapter()")
    try:
        vector_store = MockVectorStoreAdapter()
        retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
        
        results = await retriever.retrieve(query, top_k=2)
        print(f"   ✅ Mock 어댑터 사용 성공")
        print(f"   - 결과 수: {len(results)}")
        print("   - Mock은 빈 결과 반환 (정상)")
    except Exception as e:
        print(f"   ❌ Mock 어댑터 실패: {e}")
    
    print()
    
    # 3. 변경 방법 안내
    print("=== 실제 변경 방법 ===")
    print("📁 파일: interfaces/cli/main.py")
    print()
    print("🔍 찾을 코드 (여러 함수에 있음):")
    print("   vector_store = QdrantVectorStoreAdapter(")
    print("       host=\"localhost\",")
    print("       port=6333,")
    print("       vector_dimension=config.get_vector_dimension()")
    print("   )")
    print()
    print("✏️  변경할 코드:")
    print("   # vector_store = QdrantVectorStoreAdapter(...)  # 주석 처리")
    print("   from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter")
    print("   vector_store = MockVectorStoreAdapter()  # 새로 추가")
    print()
    print("📍 변경해야 할 함수들:")
    print("   - search_documents()")
    print("   - search_similar()")
    print("   - collection_stats()")
    print("   - test_qdrant()")
    print()
    print("💡 한 줄만 바꾸면 전체 시스템의 데이터베이스가 바뀝니다!")


if __name__ == "__main__":
    asyncio.run(test_database_switch())
