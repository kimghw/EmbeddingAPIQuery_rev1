#!/usr/bin/env python3
"""
IMU 데이터 사양에 대한 최종 벡터 검색 - 실제 데이터 사용
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
    """IMU 데이터 사양에 대한 최종 검색 수행"""
    print("🔍 벡터 데이터베이스에서 IMU 데이터 사양 검색 중...")
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
        
        # IMU 관련 다양한 쿼리로 검색
        queries = [
            "IMU specifications accelerometer gyroscope",
            "inertial measurement unit technical specifications",
            "accelerometer gyroscope magnetometer range accuracy",
            "IMU sensor noise bias specifications",
            "3DM-GV7 technical specifications"
        ]
        
        all_results = []
        
        for query in queries:
            print(f"\n🔍 검색 쿼리: '{query}'")
            
            search_result = await retrieval_usecase.search_documents(query, top_k=3)
            
            if search_result and isinstance(search_result, dict) and 'results' in search_result:
                results = search_result['results']
                print(f"   ✅ {len(results)}개 결과 발견")
                
                for result in results:
                    # 중복 제거를 위해 content 기준으로 확인
                    content = result.get('content', '')
                    if content and not any(r.get('content') == content for r in all_results):
                        all_results.append({
                            'content': content,
                            'score': result.get('score', 0.0),
                            'metadata': result.get('metadata', {}),
                            'query': query,
                            'document_id': result.get('document_id', ''),
                            'chunk_id': result.get('chunk_id', '')
                        })
            else:
                print("   ❌ 검색 결과 없음")
        
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
        
        # 설정 파일이 잘 적용되었는지 확인
        print(f"\n🔧 설정 파일 적용 상태:")
        print(f"   벡터 스토어: {config.get_vector_store_type()}")
        print(f"   임베딩 모델: {config.get_embedding_model()}")
        print(f"   리트리버: {config.get_retriever_type()}")
        print(f"   컬렉션명: {config.get_collection_name()}")
        print(f"   검색 상위 K: {config.get_retrieval_top_k()}")
        print(f"   점수 임계값: {config.get_retrieval_score_threshold()}")
        
    except Exception as e:
        print(f"❌ 검색 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(search_imu_specifications())
