#!/usr/bin/env python3
"""
벡터 검색 결과 개수(top_k) 설정 테스트
"""

import os
from config.settings import create_config
from config.adapter_factory import DependencyContainer

def test_retrieval_top_k_settings():
    """검색 결과 개수 설정 테스트"""
    print("=== 벡터 검색 결과 개수 설정 테스트 ===\n")
    
    # 현재 설정 확인
    config = create_config()
    print(f"📊 현재 설정:")
    print(f"  - RETRIEVAL_TOP_K: {config.get_retrieval_top_k()}")
    print(f"  - RETRIEVAL_SCORE_THRESHOLD: {config.get_retrieval_score_threshold()}")
    print()
    
    # 다양한 top_k 값으로 테스트
    test_cases = [
        {"top_k": "3", "description": "적은 결과 (3개)"},
        {"top_k": "5", "description": "기본 결과 (5개)"},
        {"top_k": "10", "description": "많은 결과 (10개)"},
        {"top_k": "20", "description": "매우 많은 결과 (20개)"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔍 테스트 {i}: {test_case['description']}")
        
        # 환경 변수 설정
        os.environ["RETRIEVAL_TOP_K"] = test_case["top_k"]
        
        # 새로운 설정 생성
        config = create_config()
        container = DependencyContainer(config)
        
        # 리트리버 생성
        retriever = container.retriever
        
        print(f"  ✅ TOP_K 설정: {config.get_retrieval_top_k()}")
        print(f"  ✅ 리트리버 타입: {type(retriever).__name__}")
        
        # 리트리버 정보 확인 (비동기 메서드이므로 실제 호출은 생략)
        print(f"  📝 설정된 검색 개수: {test_case['top_k']}개")
        print()

def test_score_threshold_settings():
    """점수 임계값 설정 테스트"""
    print("=== 점수 임계값 설정 테스트 ===\n")
    
    test_cases = [
        {"threshold": "0.5", "description": "낮은 임계값 (0.5)"},
        {"threshold": "0.7", "description": "기본 임계값 (0.7)"},
        {"threshold": "0.8", "description": "높은 임계값 (0.8)"},
        {"threshold": "0.9", "description": "매우 높은 임계값 (0.9)"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🎯 테스트 {i}: {test_case['description']}")
        
        # 환경 변수 설정
        os.environ["RETRIEVAL_SCORE_THRESHOLD"] = test_case["threshold"]
        
        # 새로운 설정 생성
        config = create_config()
        
        print(f"  ✅ 점수 임계값: {config.get_retrieval_score_threshold()}")
        print(f"  📝 {test_case['threshold']} 이상의 점수를 가진 결과만 반환")
        print()

def test_ensemble_retriever_top_k():
    """앙상블 리트리버의 top_k 설정 테스트"""
    print("=== 앙상블 리트리버 TOP_K 설정 테스트 ===\n")
    
    # 앙상블 리트리버 설정
    os.environ["RETRIEVER_TYPE"] = "ensemble"
    os.environ["ENSEMBLE_WEIGHTS"] = "0.6,0.4"
    os.environ["ENSEMBLE_SEARCH_TYPES"] = "similarity,mmr"
    
    test_cases = [
        {"top_k": "5", "description": "앙상블 기본 (5개)"},
        {"top_k": "15", "description": "앙상블 많은 결과 (15개)"}
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"🔀 앙상블 테스트 {i}: {test_case['description']}")
        
        # 환경 변수 설정
        os.environ["RETRIEVAL_TOP_K"] = test_case["top_k"]
        
        # 새로운 설정 생성
        config = create_config()
        container = DependencyContainer(config)
        
        # 앙상블 리트리버 생성
        ensemble_retriever = container.retriever
        
        print(f"  ✅ 리트리버 타입: {type(ensemble_retriever).__name__}")
        print(f"  ✅ TOP_K 설정: {config.get_retrieval_top_k()}")
        print(f"  ✅ 앙상블 가중치: {config.get_ensemble_weights()}")
        print(f"  📝 각 리트리버가 {test_case['top_k']}개씩 검색 후 융합")
        print()

def show_retrieval_method_examples():
    """검색 메서드 사용 예시"""
    print("=== 검색 메서드 사용 예시 ===\n")
    
    examples = [
        {
            "method": "retrieve_by_text",
            "code": '''
# 기본 검색 (설정된 TOP_K 사용)
results = await retriever.retrieve_by_text("질의 텍스트")

# 사용자 지정 TOP_K
results = await retriever.retrieve_by_text(
    query_text="질의 텍스트",
    top_k=10,  # 10개 결과
    score_threshold=0.8  # 0.8 이상 점수
)
            ''',
            "description": "텍스트 기반 검색"
        },
        {
            "method": "retrieve",
            "code": '''
from core.entities.document import Query

# Query 객체 생성
query = Query.create("질의 텍스트")

# 검색 실행
results = await retriever.retrieve(
    query=query,
    top_k=5,  # 5개 결과
    score_threshold=0.7,  # 0.7 이상 점수
    filter_metadata={"category": "technical"}  # 메타데이터 필터
)
            ''',
            "description": "Query 객체 기반 검색"
        },
        {
            "method": "retrieve_similar_documents",
            "code": '''
# 특정 문서와 유사한 문서 찾기
similar_docs = await retriever.retrieve_similar_documents(
    document_id="doc_123",
    top_k=8,  # 8개 유사 문서
    score_threshold=0.75
)
            ''',
            "description": "유사 문서 검색"
        }
    ]
    
    for example in examples:
        print(f"📋 {example['description']} ({example['method']})")
        print(f"```python{example['code']}```")
        print()

def show_current_env_settings():
    """현재 환경 변수 설정 표시"""
    print("=== 현재 .env 파일 설정 ===\n")
    
    config = create_config()
    
    print("🔧 검색 관련 설정:")
    print(f"  RETRIEVAL_TOP_K = {config.get_retrieval_top_k()}")
    print(f"  RETRIEVAL_SCORE_THRESHOLD = {config.get_retrieval_score_threshold()}")
    print()
    
    print("🔀 앙상블 관련 설정:")
    print(f"  RETRIEVER_TYPE = {config.get_retriever_type()}")
    if config.get_retriever_type() == "ensemble":
        print(f"  ENSEMBLE_WEIGHTS = {config.get_ensemble_weights()}")
        print(f"  ENSEMBLE_SEARCH_TYPES = {config.get_ensemble_search_types()}")
    print()
    
    print("💡 설정 변경 방법:")
    print("  1. .env 파일에서 RETRIEVAL_TOP_K=원하는숫자 설정")
    print("  2. 환경 변수로 export RETRIEVAL_TOP_K=원하는숫자")
    print("  3. 코드에서 직접 top_k 파라미터 지정")
    print()

if __name__ == "__main__":
    print("🔍 벡터 검색 결과 개수 설정 테스트\n")
    
    # 기본 설정 복원
    os.environ.pop("RETRIEVAL_TOP_K", None)
    os.environ.pop("RETRIEVAL_SCORE_THRESHOLD", None)
    os.environ.pop("RETRIEVER_TYPE", None)
    
    show_current_env_settings()
    test_retrieval_top_k_settings()
    test_score_threshold_settings()
    test_ensemble_retriever_top_k()
    show_retrieval_method_examples()
    
    print("✅ 모든 검색 설정 테스트 완료!")
    print("\n📝 요약:")
    print("  - 기본 검색 결과 개수: RETRIEVAL_TOP_K (기본값: 5)")
    print("  - 점수 임계값: RETRIEVAL_SCORE_THRESHOLD (기본값: 0.7)")
    print("  - 메서드 호출 시 top_k 파라미터로 개별 지정 가능")
    print("  - 앙상블 리트리버도 동일한 설정 사용")
