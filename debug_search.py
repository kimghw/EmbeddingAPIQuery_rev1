#!/usr/bin/env python3
"""
검색 결과 디버깅
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import create_config
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter, get_retriever_adapter
from core.usecases.document_retrieval import DocumentRetrievalUseCase


async def debug_search():
    """검색 결과 디버깅"""
    print("🔍 검색 시스템 디버깅 중...")
    
    try:
        # 설정 로드
        config = create_config()
        print(f"✅ 설정 로드 완료: {type(config)}")
        
        # 어댑터 생성
        vector_store = get_vector_store_adapter(config)
        embedding_model = get_embedding_adapter(config)
        retriever = get_retriever_adapter(config)
        print("✅ 어댑터 생성 완료")
        
        # 검색 유즈케이스 생성
        retrieval_usecase = DocumentRetrievalUseCase(
            vector_store=vector_store,
            embedding_model=embedding_model,
            retriever=retriever,
            config=config
        )
        print("✅ 검색 유즈케이스 생성 완료")
        
        # 간단한 쿼리로 테스트
        query = "technical specifications"
        print(f"\n🔍 검색 쿼리: '{query}'")
        
        results = await retrieval_usecase.search_documents(query, top_k=3)
        print(f"📊 검색 결과 타입: {type(results)}")
        print(f"📊 검색 결과 길이: {len(results) if results else 0}")
        
        if results and isinstance(results, dict):
            print(f"📊 딕셔너리 키들: {list(results.keys())}")
            
            for key, value in results.items():
                print(f"\n🔸 키: {key}")
                print(f"   값 타입: {type(value)}")
                print(f"   값: {value}")
                
            # 'results' 키가 있는지 확인
            if 'results' in results:
                actual_results = results['results']
                print(f"\n📊 실제 검색 결과:")
                print(f"   타입: {type(actual_results)}")
                print(f"   길이: {len(actual_results) if actual_results else 0}")
                
                if actual_results:
                    for i, result in enumerate(actual_results):
                        print(f"\n🔸 결과 {i+1}:")
                        print(f"   타입: {type(result)}")
                        if hasattr(result, 'content'):
                            print(f"   내용: {result.content[:200]}...")
                        elif isinstance(result, dict):
                            print(f"   딕셔너리 키들: {list(result.keys())}")
                        else:
                            print(f"   값: {str(result)[:200]}...")
        else:
            print("❌ 검색 결과가 없거나 예상과 다른 형식입니다.")
        
    except Exception as e:
        print(f"❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(debug_search())
