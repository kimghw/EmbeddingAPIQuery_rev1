"""
어댑터 교체 테스트 - Qdrant에서 FAISS로 교체 예시
"""

import asyncio
from config.settings import config
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.vector_store.faiss_vector_store import FaissVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from core.entities.document import Query


async def test_adapter_switch():
    """어댑터 교체 테스트"""
    
    print("=== 어댑터 교체 테스트 ===\n")
    
    # 공통 컴포넌트
    embedding_model = OpenAIEmbeddingAdapter(config)
    query = Query.create("What is the operating temperature range?")
    
    # 1. Qdrant 어댑터 사용
    print("1. Qdrant 어댑터로 검색:")
    qdrant_adapter = QdrantVectorStoreAdapter()
    qdrant_retriever = SimpleRetrieverAdapter(qdrant_adapter, embedding_model)
    qdrant_retriever.set_collection_name(config.get_collection_name())
    
    try:
        qdrant_results = await qdrant_retriever.retrieve(query, top_k=2)
        print(f"   - 결과 수: {len(qdrant_results)}")
        if qdrant_results:
            print(f"   - 첫 번째 결과 점수: {qdrant_results[0].score:.4f}")
            print(f"   - 내용 미리보기: {qdrant_results[0].content[:50]}...")
    except Exception as e:
        print(f"   - Qdrant 검색 실패: {e}")
    
    print()
    
    # 2. Mock 어댑터로 교체 (동일한 인터페이스)
    print("2. Mock 어댑터로 교체:")
    mock_adapter = MockVectorStoreAdapter()
    mock_retriever = SimpleRetrieverAdapter(mock_adapter, embedding_model)
    
    try:
        # Mock은 가짜 데이터를 반환
        mock_results = await mock_retriever.retrieve(query, top_k=2)
        print(f"   - 결과 수: {len(mock_results)}")
        if mock_results:
            print(f"   - 첫 번째 결과 점수: {mock_results[0].score:.4f}")
            print(f"   - Mock 데이터 내용: {mock_results[0].content[:50]}...")
    except Exception as e:
        print(f"   - Mock 검색 실패: {e}")
    
    print()
    
    # 3. 어댑터 교체의 핵심 포인트
    print("=== 어댑터 교체의 핵심 ===")
    print("✅ CORE 로직 변경 없음")
    print("✅ 포트 인터페이스 동일")
    print("✅ 의존성 주입만 변경")
    print("✅ 비즈니스 로직 재사용")
    
    print("\n=== CLI에서 어댑터 교체 방법 ===")
    print("interfaces/cli/main.py에서:")
    print("  기존: vector_store = QdrantVectorStoreAdapter()")
    print("  변경: vector_store = FaissVectorStoreAdapter()")
    print("  → 한 줄만 바꾸면 전체 시스템이 FAISS로 전환!")


if __name__ == "__main__":
    asyncio.run(test_adapter_switch())
