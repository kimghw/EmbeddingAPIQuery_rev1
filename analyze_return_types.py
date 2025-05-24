#!/usr/bin/env python3
"""
검색 결과의 반환 타입과 벡터 데이터 구조 분석
"""

import sys
import asyncio
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import create_config
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter, get_retriever_adapter
from core.usecases.document_retrieval import DocumentRetrievalUseCase


async def analyze_return_types():
    """검색 결과의 반환 타입과 벡터 데이터 구조 분석"""
    print("🔍 검색 결과 반환 타입 및 벡터 데이터 구조 분석")
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
        
        # 1. 검색 결과 타입 분석
        query = "IMU specifications"
        print(f"\n1️⃣ 검색 쿼리: '{query}'")
        
        search_result = await retrieval_usecase.search_documents(query, top_k=2)
        
        print(f"\n📊 최상위 반환 타입: {type(search_result)}")
        print(f"📊 최상위 반환 구조:")
        if isinstance(search_result, dict):
            for key, value in search_result.items():
                print(f"   - {key}: {type(value)} = {value if key != 'results' else f'[{len(value)} items]'}")
        
        # 2. 개별 검색 결과 구조 분석
        if search_result and 'results' in search_result:
            results = search_result['results']
            print(f"\n2️⃣ 개별 검색 결과 구조 분석 (총 {len(results)}개)")
            
            for i, result in enumerate(results[:1]):  # 첫 번째 결과만 분석
                print(f"\n🔸 결과 {i+1} 상세 구조:")
                print(f"   타입: {type(result)}")
                
                if isinstance(result, dict):
                    for key, value in result.items():
                        if key == 'metadata':
                            print(f"   - {key}: {type(value)} (메타데이터)")
                            for meta_key, meta_value in value.items():
                                print(f"     └─ {meta_key}: {type(meta_value)}")
                        elif key == 'content':
                            print(f"   - {key}: {type(value)} (길이: {len(value)} 문자)")
                        else:
                            print(f"   - {key}: {type(value)} = {value}")
        
        # 3. 벡터 임베딩 확인
        print(f"\n3️⃣ 벡터 임베딩 데이터 확인")
        
        # 쿼리 임베딩 생성
        query_embedding = await embedding_model.embed_text(query)
        print(f"📊 쿼리 임베딩:")
        print(f"   타입: {type(query_embedding)}")
        print(f"   차원: {len(query_embedding) if hasattr(query_embedding, '__len__') else 'N/A'}")
        print(f"   첫 5개 값: {query_embedding[:5] if hasattr(query_embedding, '__getitem__') else 'N/A'}")
        
        # 4. 벡터 스토어에서 직접 검색
        print(f"\n4️⃣ 벡터 스토어 직접 검색 결과")
        
        try:
            # 벡터 스토어에서 직접 검색
            vector_results = await vector_store.search(
                query_vector=query_embedding,
                top_k=2,
                collection_name=config.get_collection_name()
            )
            
            print(f"📊 벡터 스토어 직접 검색 결과:")
            print(f"   타입: {type(vector_results)}")
            print(f"   길이: {len(vector_results) if hasattr(vector_results, '__len__') else 'N/A'}")
            
            if vector_results and len(vector_results) > 0:
                first_result = vector_results[0]
                print(f"   첫 번째 결과 타입: {type(first_result)}")
                
                if hasattr(first_result, '__dict__'):
                    print(f"   첫 번째 결과 속성들: {list(first_result.__dict__.keys())}")
                elif isinstance(first_result, dict):
                    print(f"   첫 번째 결과 키들: {list(first_result.keys())}")
                    
        except Exception as e:
            print(f"   ❌ 벡터 스토어 직접 검색 실패: {str(e)}")
        
        # 5. 리트리버 직접 호출
        print(f"\n5️⃣ 리트리버 직접 호출 결과")
        
        try:
            retriever_results = await retriever.retrieve(
                query=query,
                top_k=2,
                vector_store=vector_store,
                embedding_model=embedding_model,
                config=config
            )
            
            print(f"📊 리트리버 직접 호출 결과:")
            print(f"   타입: {type(retriever_results)}")
            
            if retriever_results:
                if hasattr(retriever_results, '__len__'):
                    print(f"   길이: {len(retriever_results)}")
                
                if hasattr(retriever_results, '__iter__'):
                    for i, item in enumerate(list(retriever_results)[:1]):
                        print(f"   항목 {i+1} 타입: {type(item)}")
                        if hasattr(item, '__dict__'):
                            print(f"   항목 {i+1} 속성들: {list(item.__dict__.keys())}")
                        
        except Exception as e:
            print(f"   ❌ 리트리버 직접 호출 실패: {str(e)}")
        
        print(f"\n✅ 반환 타입 분석 완료")
        
    except Exception as e:
        print(f"❌ 분석 중 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(analyze_return_types())
