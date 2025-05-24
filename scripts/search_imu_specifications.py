#!/usr/bin/env python3
"""
IMU 데이터 사양에 대한 구체적인 벡터 검색
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import create_config
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter, get_retriever_adapter
from core.usecases.document_retrieval import DocumentRetrievalUseCase


async def search_imu_specifications():
    """IMU 데이터 사양에 대한 구체적인 검색 수행"""
    print("🔍 벡터 데이터베이스에서 IMU 관련 사양 검색 중...")
    
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
        
        # IMU 관련 다양한 쿼리로 검색
        queries = [
            "IMU specifications accelerometer gyroscope",
            "inertial measurement unit data specifications",
            "accelerometer gyroscope magnetometer specifications",
            "IMU sensor range accuracy noise",
            "inertial sensor technical specifications"
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n🔍 검색 쿼리: '{query}'")
            results = await retrieval_usecase.search_documents(query, top_k=3)
            
            if results and len(results) > 0:
                for result in results:
                    if hasattr(result, 'content') and result.content not in [r.get('content', '') for r in all_results]:
                        all_results.append({
                            'content': result.content,
                            'score': getattr(result, 'score', 0.0),
                            'metadata': getattr(result, 'metadata', {}),
                            'query': query
                        })
        
        # 점수 기준으로 정렬하고 상위 5개 선택
        all_results.sort(key=lambda x: x['score'], reverse=True)
        top_5_results = all_results[:5]
        
        print(f"\n📊 IMU 데이터 사양에 대한 상위 5개 답변")
        print("=" * 80)
        
        if not top_5_results:
            print("❌ 검색 결과가 없습니다.")
            return
        
        for i, result in enumerate(top_5_results, 1):
            print(f"\n🔸 답변 {i}")
            print(f"📄 문서: {result['metadata'].get('source', 'Unknown')}")
            print(f"📊 유사도 점수: {result['score']:.4f}")
            print(f"🔍 검색 쿼리: {result['query']}")
            print(f"📝 내용:")
            print("-" * 60)
            print(result['content'])
            print("-" * 60)
        
        print(f"\n✅ 총 {len(top_5_results)}개의 IMU 관련 답변을 찾았습니다.")
        
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(search_imu_specifications())
