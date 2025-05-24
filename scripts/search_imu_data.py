#!/usr/bin/env python3
"""
IMU 데이터 사양에 대한 벡터 검색 테스트
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import create_config
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter, get_retriever_adapter
from core.usecases.document_retrieval import DocumentRetrievalUseCase


async def search_imu_data():
    """IMU 데이터 사양에 대한 검색 수행"""
    print("🔍 벡터 데이터베이스에서 'IMU 데이터 사양' 검색 중...")
    
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
        
        # 검색 수행 (top_k=5)
        query = "IMU 데이터 사양"
        results = await retrieval_usecase.search_documents(query, top_k=5)
        
        print(f"\n📊 검색 결과: '{query}'에 대한 상위 5개 답변\n")
        print("=" * 80)
        
        if not results:
            print("❌ 검색 결과가 없습니다.")
            return
        
        for i, result in enumerate(results, 1):
            print(f"\n🔸 답변 {i}")
            print("-" * 60)
            
            # 결과가 문자열인지 객체인지 확인
            if isinstance(result, str):
                print(result)
            else:
                # 객체인 경우 속성 확인
                if hasattr(result, 'metadata'):
                    print(f"📄 문서: {result.metadata.get('source', 'Unknown')}")
                if hasattr(result, 'score'):
                    print(f"📊 유사도 점수: {result.score:.4f}")
                if hasattr(result, 'content'):
                    print(f"📝 내용:\n{result.content}")
                else:
                    print(f"📝 내용:\n{result}")
            
            print("-" * 60)
        
        print(f"\n✅ 총 {len(results)}개의 관련 답변을 찾았습니다.")
        
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(search_imu_data())
