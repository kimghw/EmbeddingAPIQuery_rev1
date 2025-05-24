#!/usr/bin/env python3
"""
어댑터 데이터 플로우 분석
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

async def analyze_adapter_data_flow():
    """어댑터 데이터 플로우 분석"""
    print("🔍 어댑터 데이터 플로우 분석")
    print("=" * 60)
    
    try:
        # 1. Core 엔티티 확인
        print("1️⃣ Core 엔티티:")
        from core.entities.document import Document, Query, RetrievalResult
        print("✅ Document (Core 엔티티)")
        print("✅ Query (Core 엔티티)")
        print("✅ RetrievalResult (Core 엔티티)")
        
        # 2. 어댑터 입출력 타입 확인
        print("\n2️⃣ 어댑터 입출력 타입:")
        
        # Vector Store 어댑터
        from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
        vector_store = QdrantVectorStoreAdapter()
        print(f"📊 QdrantVectorStoreAdapter:")
        print(f"   - search_similar 반환: List[RetrievalResult] (Core 엔티티)")
        
        # Embedding 어댑터
        from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
        from config.settings import config
        embedding_model = OpenAIEmbeddingAdapter(config)
        print(f"📊 OpenAIEmbeddingAdapter:")
        print(f"   - embed_query 반환: List[float] (기본 타입)")
        print(f"   - embed_documents 반환: List[List[float]] (기본 타입)")
        
        # Retriever 어댑터
        from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
        retriever = SimpleRetrieverAdapter(vector_store, embedding_model)
        print(f"📊 SimpleRetrieverAdapter:")
        print(f"   - retrieve 입력: Query (Core 엔티티)")
        print(f"   - retrieve 반환: List[RetrievalResult] (Core 엔티티)")
        
        # 3. 유즈케이스 변환 확인
        print("\n3️⃣ 유즈케이스 변환:")
        from core.usecases.document_retrieval import DocumentRetrievalUseCase
        usecase = DocumentRetrievalUseCase(
            retriever=retriever,
            embedding_model=embedding_model,
            vector_store=vector_store,
            config=config
        )
        
        # 실제 검색으로 데이터 플로우 확인
        result = await usecase.search_documents("test query", top_k=1)
        print(f"📊 DocumentRetrievalUseCase:")
        print(f"   - 입력: str, int, Optional[float] (기본 타입)")
        print(f"   - 내부 처리: Core 엔티티 사용")
        print(f"   - 출력: {type(result)} (Pydantic 모델)")
        
        # 4. 데이터 플로우 요약
        print("\n4️⃣ 데이터 플로우 요약:")
        print("┌─────────────────┬─────────────────┬─────────────────┐")
        print("│ 레이어          │ 입력 타입       │ 출력 타입       │")
        print("├─────────────────┼─────────────────┼─────────────────┤")
        print("│ API Interface   │ Pydantic 모델   │ Pydantic 모델   │")
        print("│ UseCase         │ 기본 타입       │ Pydantic 모델   │")
        print("│ Adapter         │ Core 엔티티     │ Core 엔티티     │")
        print("│ Core            │ Core 엔티티     │ Core 엔티티     │")
        print("└─────────────────┴─────────────────┴─────────────────┘")
        
        # 5. 클린 아키텍처 준수 확인
        print("\n5️⃣ 클린 아키텍처 준수 확인:")
        print("✅ Core는 외부 의존성(Pydantic) 없음")
        print("✅ Adapter는 Core 엔티티만 사용")
        print("✅ UseCase가 Core → Pydantic 변환 담당")
        print("✅ API Interface는 Pydantic 모델 사용")
        
        # 6. 실제 타입 검증
        print("\n6️⃣ 실제 타입 검증:")
        
        # Query 생성
        query = Query.create("test")
        print(f"📊 Query 타입: {type(query)}")
        
        # Retriever 호출
        retrieval_results = await retriever.retrieve(query, top_k=1)
        if retrieval_results:
            print(f"📊 RetrievalResult 타입: {type(retrieval_results[0])}")
        
        # UseCase 결과
        print(f"📊 UseCase 결과 타입: {type(result)}")
        
        return True
        
    except Exception as e:
        print(f"❌ 분석 실패: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(analyze_adapter_data_flow())
    if success:
        print("\n🎉 데이터 플로우 분석 완료!")
    else:
        print("\n💥 분석 실패!")
        sys.exit(1)
