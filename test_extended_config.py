"""
Extended configuration test for upload and chunking settings.
"""

import os
import asyncio
from config.settings import ConfigAdapter, TestConfig, create_config
from config.adapter_factory import DependencyContainer


async def test_extended_config():
    """Test extended configuration including upload and chunking settings."""
    print("=== 확장된 설정 테스트 ===")
    
    # 테스트 설정 생성
    config = ConfigAdapter(TestConfig())
    
    # 기본 설정 확인
    print(f"앱 이름: {config.get_app_name()}")
    print(f"디버그 모드: {config.get_debug()}")
    print(f"로그 레벨: {config.get_log_level()}")
    
    # 의존성 주입 설정 확인
    print(f"\n=== 의존성 주입 설정 ===")
    print(f"벡터 저장소 타입: {config.get_vector_store_type()}")
    print(f"임베딩 타입: {config.get_embedding_type()}")
    print(f"문서 로더 타입: {config.get_document_loader_type()}")
    print(f"텍스트 청킹 타입: {config.get_text_chunker_type()}")
    print(f"리트리버 타입: {config.get_retriever_type()}")
    
    # LLM 설정 확인
    print(f"\n=== LLM 설정 ===")
    print(f"LLM 모델 타입: {config.get_llm_model_type()}")
    print(f"LLM 모델명: {config.get_llm_model_name()}")
    print(f"LLM 온도: {config.get_llm_temperature()}")
    print(f"LLM 최대 토큰: {config.get_llm_max_tokens()}")
    
    # 업로드 설정 확인
    print(f"\n=== 업로드 설정 ===")
    print(f"최대 파일 크기: {config.get_upload_max_file_size():,} bytes")
    print(f"허용 확장자: {config.get_upload_allowed_extensions()}")
    print(f"업로드 디렉토리: {config.get_upload_directory()}")
    print(f"임시 디렉토리: {config.get_upload_temp_directory()}")
    
    # 고급 청킹 설정 확인
    print(f"\n=== 고급 청킹 설정 ===")
    print(f"시맨틱 청크 최소 크기: {config.get_semantic_chunk_min_size()}")
    print(f"시맨틱 청크 최대 크기: {config.get_semantic_chunk_max_size()}")
    print(f"시맨틱 유사도 임계값: {config.get_semantic_similarity_threshold()}")
    
    # 검색 설정 확인
    print(f"\n=== 검색 설정 ===")
    print(f"검색 Top-K: {config.get_retrieval_top_k()}")
    print(f"점수 임계값: {config.get_retrieval_score_threshold()}")
    
    # 앙상블 리트리버 설정 확인
    print(f"\n=== 앙상블 리트리버 설정 ===")
    print(f"앙상블 가중치: {config.get_ensemble_weights()}")
    print(f"검색 타입: {config.get_ensemble_search_types()}")
    
    # 의존성 컨테이너 테스트
    print(f"\n=== 의존성 컨테이너 테스트 ===")
    container = DependencyContainer(config)
    
    # 모든 어댑터 생성 테스트
    try:
        vector_store = container.vector_store
        print(f"✅ 벡터 저장소: {type(vector_store).__name__}")
        
        embedding = container.embedding_model
        print(f"✅ 임베딩 모델: {type(embedding).__name__}")
        
        document_loader = container.document_loader
        print(f"✅ 문서 로더: {type(document_loader).__name__}")
        
        text_chunker = container.text_chunker
        print(f"✅ 텍스트 청킹: {type(text_chunker).__name__}")
        
        retriever = container.retriever
        print(f"✅ 리트리버: {type(retriever).__name__}")
        
        print("✅ 모든 어댑터 생성 성공")
        
    except Exception as e:
        print(f"❌ 어댑터 생성 실패: {e}")
        return False
    
    # 환경 변수 기반 설정 변경 테스트
    print(f"\n=== 환경 변수 설정 변경 테스트 ===")
    
    # 업로드 설정 변경
    os.environ["UPLOAD_MAX_FILE_SIZE"] = "104857600"  # 100MB
    os.environ["UPLOAD_ALLOWED_EXTENSIONS"] = "pdf,txt,docx,pptx"
    os.environ["UPLOAD_DIRECTORY"] = "custom_uploads"
    
    # 청킹 설정 변경
    os.environ["SEMANTIC_CHUNK_MIN_SIZE"] = "200"
    os.environ["SEMANTIC_CHUNK_MAX_SIZE"] = "1500"
    os.environ["SEMANTIC_SIMILARITY_THRESHOLD"] = "0.75"
    
    # 검색 설정 변경
    os.environ["RETRIEVAL_TOP_K"] = "10"
    os.environ["RETRIEVAL_SCORE_THRESHOLD"] = "0.8"
    
    # 앙상블 설정 변경
    os.environ["ENSEMBLE_WEIGHTS"] = "0.7,0.3"
    os.environ["ENSEMBLE_SEARCH_TYPES"] = "similarity,similarity_score_threshold"
    
    # 새로운 설정으로 컨테이너 생성 (기존 컨테이너는 기존 설정을 유지하므로)
    new_config = create_config()
    new_container = DependencyContainer(new_config)
    
    print(f"변경된 최대 파일 크기: {new_config.get_upload_max_file_size():,} bytes")
    print(f"변경된 허용 확장자: {new_config.get_upload_allowed_extensions()}")
    print(f"변경된 업로드 디렉토리: {new_config.get_upload_directory()}")
    print(f"변경된 시맨틱 청크 최소 크기: {new_config.get_semantic_chunk_min_size()}")
    print(f"변경된 시맨틱 청크 최대 크기: {new_config.get_semantic_chunk_max_size()}")
    print(f"변경된 시맨틱 유사도 임계값: {new_config.get_semantic_similarity_threshold()}")
    print(f"변경된 검색 Top-K: {new_config.get_retrieval_top_k()}")
    print(f"변경된 점수 임계값: {new_config.get_retrieval_score_threshold()}")
    print(f"변경된 앙상블 가중치: {new_config.get_ensemble_weights()}")
    print(f"변경된 검색 타입: {new_config.get_ensemble_search_types()}")
    
    # 환경 변수 정리
    env_vars_to_clean = [
        "UPLOAD_MAX_FILE_SIZE", "UPLOAD_ALLOWED_EXTENSIONS", "UPLOAD_DIRECTORY",
        "SEMANTIC_CHUNK_MIN_SIZE", "SEMANTIC_CHUNK_MAX_SIZE", "SEMANTIC_SIMILARITY_THRESHOLD",
        "RETRIEVAL_TOP_K", "RETRIEVAL_SCORE_THRESHOLD",
        "ENSEMBLE_WEIGHTS", "ENSEMBLE_SEARCH_TYPES"
    ]
    
    for var in env_vars_to_clean:
        if var in os.environ:
            del os.environ[var]
    
    print("✅ 환경 변수 설정 변경 테스트 완료")
    
    # 어댑터 타입 전환 테스트
    print(f"\n=== 어댑터 타입 전환 테스트 ===")
    
    # 리트리버를 ensemble로 변경
    os.environ["RETRIEVER_TYPE"] = "ensemble"
    ensemble_config = create_config()
    ensemble_container = DependencyContainer(ensemble_config)
    
    try:
        ensemble_retriever = ensemble_container.retriever
        print(f"✅ 앙상블 리트리버 생성: {type(ensemble_retriever).__name__}")
    except Exception as e:
        print(f"❌ 앙상블 리트리버 생성 실패: {e}")
    
    # 텍스트 청킹을 semantic으로 변경
    os.environ["TEXT_CHUNKER_TYPE"] = "semantic"
    semantic_config = create_config()
    semantic_container = DependencyContainer(semantic_config)
    
    try:
        semantic_chunker = semantic_container.text_chunker
        print(f"✅ 시맨틱 청킹 생성: {type(semantic_chunker).__name__}")
    except Exception as e:
        print(f"❌ 시맨틱 청킹 생성 실패: {e}")
    
    # 환경 변수 정리
    if "RETRIEVER_TYPE" in os.environ:
        del os.environ["RETRIEVER_TYPE"]
    if "TEXT_CHUNKER_TYPE" in os.environ:
        del os.environ["TEXT_CHUNKER_TYPE"]
    
    print("✅ 어댑터 타입 전환 테스트 완료")
    
    # JSON 로더 테스트
    print(f"\n=== JSON 로더 테스트 ===")
    
    os.environ["DOCUMENT_LOADER_TYPE"] = "json"
    json_config = create_config()
    json_container = DependencyContainer(json_config)
    
    try:
        json_loader = json_container.document_loader
        print(f"✅ JSON 로더 생성: {type(json_loader).__name__}")
    except Exception as e:
        print(f"❌ JSON 로더 생성 실패: {e}")
    
    # 환경 변수 정리
    if "DOCUMENT_LOADER_TYPE" in os.environ:
        del os.environ["DOCUMENT_LOADER_TYPE"]
    
    print("✅ JSON 로더 테스트 완료")
    
    print("\n🎉 모든 확장된 설정 테스트 완료!")
    return True


if __name__ == "__main__":
    asyncio.run(test_extended_config())
