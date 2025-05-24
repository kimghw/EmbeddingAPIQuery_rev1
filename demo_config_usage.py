#!/usr/bin/env python3
"""
설정 사용법 데모 스크립트
EnsembleRetriever와 JSON 로더 설정 방법을 보여줍니다.
"""

import os
from config.settings import create_config
from config.adapter_factory import DependencyContainer

def demo_basic_config():
    """기본 설정 사용법"""
    print("=== 기본 설정 사용법 ===")
    
    # 설정 생성
    config = create_config()
    
    # 기본 설정 확인
    print(f"앱 이름: {config.get_app_name()}")
    print(f"벡터 저장소 타입: {config.get_vector_store_type()}")
    print(f"문서 로더 타입: {config.get_document_loader_type()}")
    print(f"리트리버 타입: {config.get_retriever_type()}")
    print()

def demo_json_loader_config():
    """JSON 로더 설정 방법"""
    print("=== JSON 로더 설정 방법 ===")
    
    # 환경 변수로 JSON 로더 설정
    os.environ["DOCUMENT_LOADER_TYPE"] = "json"
    
    # 새로운 설정 생성
    config = create_config()
    container = DependencyContainer(config)
    
    # JSON 로더 생성
    json_loader = container.document_loader
    print(f"✅ JSON 로더 생성됨: {type(json_loader).__name__}")
    print(f"문서 로더 타입: {config.get_document_loader_type()}")
    print()

def demo_ensemble_retriever_config():
    """EnsembleRetriever 설정 방법"""
    print("=== EnsembleRetriever 설정 방법 ===")
    
    # 환경 변수로 앙상블 리트리버 설정
    os.environ["RETRIEVER_TYPE"] = "ensemble"
    os.environ["ENSEMBLE_WEIGHTS"] = "0.7,0.3"
    os.environ["ENSEMBLE_SEARCH_TYPES"] = "similarity,mmr"
    
    # 새로운 설정 생성
    config = create_config()
    container = DependencyContainer(config)
    
    # 앙상블 리트리버 생성
    ensemble_retriever = container.retriever
    print(f"✅ 앙상블 리트리버 생성됨: {type(ensemble_retriever).__name__}")
    print(f"리트리버 타입: {config.get_retriever_type()}")
    print(f"앙상블 가중치: {config.get_ensemble_weights()}")
    print(f"검색 타입: {config.get_ensemble_search_types()}")
    print()

def demo_semantic_chunker_config():
    """시맨틱 청킹 설정 방법"""
    print("=== 시맨틱 청킹 설정 방법 ===")
    
    # 환경 변수로 시맨틱 청킹 설정
    os.environ["TEXT_CHUNKER_TYPE"] = "semantic"
    os.environ["SEMANTIC_CHUNK_MIN_SIZE"] = "200"
    os.environ["SEMANTIC_CHUNK_MAX_SIZE"] = "1500"
    os.environ["SEMANTIC_SIMILARITY_THRESHOLD"] = "0.75"
    
    # 새로운 설정 생성
    config = create_config()
    container = DependencyContainer(config)
    
    # 시맨틱 청킹 생성
    semantic_chunker = container.text_chunker
    print(f"✅ 시맨틱 청킹 생성됨: {type(semantic_chunker).__name__}")
    print(f"텍스트 청킹 타입: {config.get_text_chunker_type()}")
    print(f"최소 청크 크기: {config.get_semantic_chunk_min_size()}")
    print(f"최대 청크 크기: {config.get_semantic_chunk_max_size()}")
    print(f"유사도 임계값: {config.get_semantic_similarity_threshold()}")
    print()

def demo_vector_store_switching():
    """벡터 저장소 전환 방법"""
    print("=== 벡터 저장소 전환 방법 ===")
    
    # FAISS로 전환
    os.environ["VECTOR_STORE_TYPE"] = "faiss"
    config = create_config()
    container = DependencyContainer(config)
    faiss_store = container.vector_store
    print(f"✅ FAISS 벡터 저장소: {type(faiss_store).__name__}")
    
    # Mock으로 전환
    os.environ["VECTOR_STORE_TYPE"] = "mock"
    config = create_config()
    container = DependencyContainer(config)
    mock_store = container.vector_store
    print(f"✅ Mock 벡터 저장소: {type(mock_store).__name__}")
    
    # 다시 Qdrant로 복원
    os.environ["VECTOR_STORE_TYPE"] = "qdrant"
    config = create_config()
    container = DependencyContainer(config)
    qdrant_store = container.vector_store
    print(f"✅ Qdrant 벡터 저장소: {type(qdrant_store).__name__}")
    print()

def demo_complete_pipeline_config():
    """완전한 파이프라인 설정 예시"""
    print("=== 완전한 파이프라인 설정 예시 ===")
    
    # 고급 설정 조합
    config_settings = {
        "VECTOR_STORE_TYPE": "qdrant",
        "EMBEDDING_TYPE": "openai", 
        "DOCUMENT_LOADER_TYPE": "json",
        "TEXT_CHUNKER_TYPE": "semantic",
        "RETRIEVER_TYPE": "ensemble",
        "ENSEMBLE_WEIGHTS": "0.6,0.4",
        "ENSEMBLE_SEARCH_TYPES": "similarity,similarity_score_threshold",
        "SEMANTIC_CHUNK_MIN_SIZE": "150",
        "SEMANTIC_CHUNK_MAX_SIZE": "1800",
        "RETRIEVAL_TOP_K": "10",
        "RETRIEVAL_SCORE_THRESHOLD": "0.75"
    }
    
    # 환경 변수 설정
    for key, value in config_settings.items():
        os.environ[key] = value
    
    # 설정 생성 및 컨테이너 초기화
    config = create_config()
    container = DependencyContainer(config)
    
    # 모든 컴포넌트 생성
    vector_store = container.vector_store
    embedding_model = container.embedding_model
    document_loader = container.document_loader
    text_chunker = container.text_chunker
    retriever = container.retriever
    
    print("🚀 완전한 파이프라인 구성:")
    print(f"  - 벡터 저장소: {type(vector_store).__name__}")
    print(f"  - 임베딩 모델: {type(embedding_model).__name__}")
    print(f"  - 문서 로더: {type(document_loader).__name__}")
    print(f"  - 텍스트 청킹: {type(text_chunker).__name__}")
    print(f"  - 리트리버: {type(retriever).__name__}")
    print()

def show_env_file_example():
    """환경 변수 파일 예시"""
    print("=== .env 파일 설정 예시 ===")
    print("""
# EnsembleRetriever 사용하려면:
RETRIEVER_TYPE=ensemble
ENSEMBLE_WEIGHTS=0.7,0.3
ENSEMBLE_SEARCH_TYPES=similarity,mmr

# JSON 로더 사용하려면:
DOCUMENT_LOADER_TYPE=json

# 시맨틱 청킹 사용하려면:
TEXT_CHUNKER_TYPE=semantic
SEMANTIC_CHUNK_MIN_SIZE=100
SEMANTIC_CHUNK_MAX_SIZE=2000
SEMANTIC_SIMILARITY_THRESHOLD=0.8

# FAISS 벡터 저장소 사용하려면:
VECTOR_STORE_TYPE=faiss

# 고급 검색 설정:
RETRIEVAL_TOP_K=10
RETRIEVAL_SCORE_THRESHOLD=0.75
    """)

if __name__ == "__main__":
    print("🔧 Document Embedding & Retrieval System - 설정 사용법 데모\n")
    
    # 기본 설정 복원
    os.environ.pop("DOCUMENT_LOADER_TYPE", None)
    os.environ.pop("RETRIEVER_TYPE", None)
    os.environ.pop("TEXT_CHUNKER_TYPE", None)
    os.environ.pop("VECTOR_STORE_TYPE", None)
    
    demo_basic_config()
    demo_json_loader_config()
    demo_ensemble_retriever_config()
    demo_semantic_chunker_config()
    demo_vector_store_switching()
    demo_complete_pipeline_config()
    show_env_file_example()
    
    print("✅ 모든 설정 데모 완료!")
    print("\n💡 팁: .env 파일을 수정하거나 환경 변수를 설정하여 시스템 동작을 변경할 수 있습니다.")
