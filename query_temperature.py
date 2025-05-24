#!/usr/bin/env python3
"""
작동 온도 관련 질의 스크립트
"""
import asyncio
import sys
import os

# 프로젝트 루트를 Python 경로에 추가
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import config
from config.adapter_factory import AdapterFactory
from core.usecases.document_retrieval import DocumentRetrievalUseCase

async def query_operating_temperature():
    """작동 온도 관련 정보 검색"""
    print("🌡️ 3DM GV7 작동 온도 정보 검색")
    print("=" * 50)
    
    try:
        # 어댑터 초기화
        print("🔧 어댑터 초기화 중...")
        vector_store = AdapterFactory.create_vector_store("qdrant", config)
        embedding_model = AdapterFactory.create_embedding_model("openai", config)
        retriever = AdapterFactory.create_retriever("simple", config, vector_store, embedding_model)
        
        # 유스케이스 생성
        retrieval_usecase = DocumentRetrievalUseCase(retriever)
        
        # 온도 관련 질의들
        temperature_queries = [
            "작동 온도는 몇도인가",
            "operating temperature",
            "temperature range",
            "온도 범위",
            "동작 온도",
            "temperature specifications",
            "환경 조건",
            "environmental conditions"
        ]
        
        print(f"🔍 {len(temperature_queries)}개의 온도 관련 질의 실행 중...\n")
        
        all_results = {}
        
        for i, query in enumerate(temperature_queries, 1):
            print(f"📋 질의 {i}: '{query}'")
            print("-" * 40)
            
            try:
                results = await retrieval_usecase.search_documents(
                    query=query,
                    limit=5,
                    score_threshold=0.1
                )
                
                if results:
                    print(f"✅ {len(results)} 개의 관련 결과 발견")
                    
                    for j, result in enumerate(results, 1):
                        print(f"\n   결과 {j}:")
                        print(f"     점수: {result.score:.4f}")
                        print(f"     내용 미리보기: {result.content[:150]}...")
                        
                        # 온도 관련 키워드가 포함된 경우 전체 내용 표시
                        content_lower = result.content.lower()
                        temp_keywords = ['temperature', '온도', '°c', '°f', 'celsius', 'fahrenheit', 'operating', '동작', '작동', 'environmental', 'thermal']
                        
                        if any(keyword in content_lower for keyword in temp_keywords):
                            print(f"     🌡️ 온도 관련 내용 발견!")
                            print(f"     전체 내용:\n{result.content}")
                            
                            # 결과 저장
                            if query not in all_results:
                                all_results[query] = []
                            all_results[query].append({
                                'score': result.score,
                                'content': result.content,
                                'metadata': result.metadata
                            })
                else:
                    print("❌ 관련 결과를 찾을 수 없습니다.")
                    
            except Exception as e:
                print(f"❌ 질의 실행 중 오류: {e}")
            
            print("\n")
        
        # 최종 요약
        print("🎯 작동 온도 정보 요약")
        print("=" * 50)
        
        if all_results:
            # 가장 관련성 높은 결과들 추출
            best_results = []
            for query, results in all_results.items():
                for result in results:
                    best_results.append((query, result))
            
            # 점수순으로 정렬
            best_results.sort(key=lambda x: x[1]['score'], reverse=True)
            
            if best_results:
                print("📊 가장 관련성 높은 온도 정보:")
                for i, (query, result) in enumerate(best_results[:5], 1):
                    print(f"\n{i}. 질의: '{query}' (점수: {result['score']:.4f})")
                    print(f"   내용: {result['content']}")
                    print(f"   메타데이터: {result['metadata'].get('source', 'N/A')}")
            else:
                print("⚠️ 온도 관련 정보를 찾지 못했습니다.")
        else:
            print("❌ 온도 관련 정보를 찾을 수 없습니다.")
            
    except Exception as e:
        print(f"❌ 전체 프로세스 실행 중 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(query_operating_temperature())
