"""
의존성 주입 설정 테스트
"""

import os
from config.settings import ConfigAdapter, DevelopmentConfig, TestConfig
from config.adapter_factory import (
    AdapterFactory, 
    DependencyContainer,
    get_vector_store_adapter,
    get_embedding_adapter,
    get_document_loader_adapter,
    get_text_chunker_adapter,
    get_retriever_adapter
)
from core.ports.vector_store import VectorStorePort
from core.ports.embedding_model import EmbeddingModelPort
from core.ports.document_loader import DocumentLoaderPort
from core.ports.text_chunker import TextChunkerPort
from core.ports.retriever import RetrieverPort


def test_config_dependency_injection():
    """설정 기반 의존성 주입 테스트"""
    print("\n=== 의존성 주입 설정 테스트 ===")
    
    # 테스트 설정 생성
    config = ConfigAdapter(TestConfig())
    
    # 설정 값 확인
    print(f"벡터 저장소 타입: {config.get_vector_store_type()}")
    print(f"임베딩 타입: {config.get_embedding_type()}")
    print(f"문서 로더 타입: {config.get_document_loader_type()}")
    print(f"텍스트 청킹 타입: {config.get_text_chunker_type()}")
    print(f"리트리버 타입: {config.get_retriever_type()}")
    print(f"LLM 모델 타입: {config.get_llm_model_type()}")
    print(f"LLM 모델명: {config.get_llm_model_name()}")
    print(f"LLM 온도: {config.get_llm_temperature()}")
    print(f"LLM 최대 토큰: {config.get_llm_max_tokens()}")


def test_adapter_factory_with_config():
    """설정 기반 어댑터 팩토리 테스트"""
    print("\n=== 설정 기반 어댑터 팩토리 테스트 ===")
    
    # 테스트 설정 생성
    config = ConfigAdapter(TestConfig())
    
    # 각 어댑터 생성 테스트
    try:
        vector_store = get_vector_store_adapter(config)
        print(f"벡터 저장소 어댑터: {type(vector_store).__name__}")
        assert isinstance(vector_store, VectorStorePort)
        
        embedding_model = get_embedding_adapter(config)
        print(f"임베딩 어댑터: {type(embedding_model).__name__}")
        assert isinstance(embedding_model, EmbeddingModelPort)
        
        document_loader = get_document_loader_adapter(config)
        print(f"문서 로더 어댑터: {type(document_loader).__name__}")
        assert isinstance(document_loader, DocumentLoaderPort)
        
        text_chunker = get_text_chunker_adapter(config)
        print(f"텍스트 청킹 어댑터: {type(text_chunker).__name__}")
        assert isinstance(text_chunker, TextChunkerPort)
        
        retriever = get_retriever_adapter(config)
        print(f"리트리버 어댑터: {type(retriever).__name__}")
        assert isinstance(retriever, RetrieverPort)
        
        print("✅ 모든 어댑터 생성 성공")
        
    except Exception as e:
        print(f"❌ 어댑터 생성 실패: {e}")
        raise


def test_dependency_container():
    """의존성 컨테이너 테스트"""
    print("\n=== 의존성 컨테이너 테스트 ===")
    
    # 테스트 설정 생성
    config = ConfigAdapter(TestConfig())
    container = DependencyContainer(config)
    
    # 싱글톤 패턴 테스트
    vector_store1 = container.vector_store
    vector_store2 = container.vector_store
    assert vector_store1 is vector_store2, "벡터 저장소는 싱글톤이어야 함"
    print("✅ 벡터 저장소 싱글톤 확인")
    
    embedding1 = container.embedding_model
    embedding2 = container.embedding_model
    assert embedding1 is embedding2, "임베딩 모델은 싱글톤이어야 함"
    print("✅ 임베딩 모델 싱글톤 확인")
    
    # 컨테이너 정보 출력
    print(f"벡터 저장소: {type(container.vector_store).__name__}")
    print(f"임베딩 모델: {type(container.embedding_model).__name__}")
    print(f"문서 로더: {type(container.document_loader).__name__}")
    print(f"텍스트 청킹: {type(container.text_chunker).__name__}")
    print(f"리트리버: {type(container.retriever).__name__}")
    
    # 리셋 테스트
    container.reset()
    vector_store3 = container.vector_store
    assert vector_store1 is not vector_store3, "리셋 후 새 인스턴스가 생성되어야 함"
    print("✅ 컨테이너 리셋 확인")


def test_environment_based_config():
    """환경별 설정 테스트"""
    print("\n=== 환경별 설정 테스트 ===")
    
    # Development 환경
    dev_config = ConfigAdapter(DevelopmentConfig())
    print(f"Development - Debug: {dev_config.get_debug()}")
    print(f"Development - Log Level: {dev_config.get_log_level()}")
    
    # Test 환경
    test_config = ConfigAdapter(TestConfig())
    print(f"Test - Debug: {test_config.get_debug()}")
    print(f"Test - Log Level: {test_config.get_log_level()}")
    print(f"Test - OpenAI Key: {test_config.get_openai_api_key()}")


def test_adapter_switching():
    """어댑터 전환 테스트"""
    print("\n=== 어댑터 전환 테스트 ===")
    
    # Mock 벡터 저장소로 전환
    mock_vector_store = AdapterFactory.create_vector_store_adapter("mock")
    print(f"Mock 벡터 저장소: {type(mock_vector_store).__name__}")
    
    # FAISS 벡터 저장소로 전환
    faiss_vector_store = AdapterFactory.create_vector_store_adapter("faiss")
    print(f"FAISS 벡터 저장소: {type(faiss_vector_store).__name__}")
    
    # JSON 로더로 전환
    json_loader = AdapterFactory.create_document_loader_adapter("json")
    print(f"JSON 로더: {type(json_loader).__name__}")
    
    # Semantic 청킹으로 전환
    semantic_chunker = AdapterFactory.create_text_chunker_adapter("semantic")
    print(f"Semantic 청킹: {type(semantic_chunker).__name__}")
    
    print("✅ 어댑터 전환 테스트 완료")


if __name__ == "__main__":
    test_config_dependency_injection()
    test_adapter_factory_with_config()
    test_dependency_container()
    test_environment_based_config()
    test_adapter_switching()
    
    print("\n🎉 모든 의존성 주입 테스트 완료!")
