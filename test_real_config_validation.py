#!/usr/bin/env python3
"""
실제 데이터를 사용한 설정 파일 검증 테스트
Mock을 사용하지 않고 실제 환경변수와 설정값들을 검증합니다.
"""

import os
import sys
import tempfile
from pathlib import Path
from typing import Dict, Any

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import (
    create_config, 
    ConfigAdapter, 
    DevelopmentConfig, 
    ProductionConfig, 
    TestConfig,
    BaseConfig
)


class RealConfigValidator:
    """실제 설정값 검증 클래스"""
    
    def __init__(self):
        self.test_results = []
        self.config = create_config()
    
    def log_test(self, test_name: str, expected: Any, actual: Any, passed: bool):
        """테스트 결과 로깅"""
        result = {
            'test_name': test_name,
            'expected': expected,
            'actual': actual,
            'passed': passed
        }
        self.test_results.append(result)
        
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} {test_name}")
        print(f"   Expected: {expected}")
        print(f"   Actual: {actual}")
        print()
    
    def validate_basic_config(self):
        """기본 설정값 검증"""
        print("=== 기본 설정값 검증 ===")
        
        # OpenAI API Key 검증 (실제 값이 있는지)
        api_key = self.config.get_openai_api_key()
        self.log_test(
            "OpenAI API Key exists",
            "Non-empty string starting with 'sk-'",
            f"Length: {len(api_key)}, Starts with sk-: {api_key.startswith('sk-')}",
            len(api_key) > 0 and api_key.startswith('sk-')
        )
        
        # Qdrant URL 검증
        qdrant_url = self.config.get_qdrant_url()
        expected_url = "http://localhost:6333"
        self.log_test(
            "Qdrant URL",
            expected_url,
            qdrant_url,
            qdrant_url == expected_url
        )
        
        # 앱 이름 검증
        app_name = self.config.get_app_name()
        expected_name = "Document Embedding & Retrieval System"
        self.log_test(
            "App Name",
            expected_name,
            app_name,
            app_name == expected_name
        )
        
        # 디버그 모드 검증
        debug = self.config.get_debug()
        self.log_test(
            "Debug Mode",
            True,
            debug,
            debug == True
        )
    
    def validate_embedding_config(self):
        """임베딩 관련 설정 검증"""
        print("=== 임베딩 설정 검증 ===")
        
        # 임베딩 모델
        embedding_model = self.config.get_embedding_model()
        expected_model = "text-embedding-3-small"
        self.log_test(
            "Embedding Model",
            expected_model,
            embedding_model,
            embedding_model == expected_model
        )
        
        # 벡터 차원
        vector_dim = self.config.get_vector_dimension()
        expected_dim = 1536
        self.log_test(
            "Vector Dimension",
            expected_dim,
            vector_dim,
            vector_dim == expected_dim
        )
        
        # 청크 크기
        chunk_size = self.config.get_chunk_size()
        expected_size = 1000
        self.log_test(
            "Chunk Size",
            expected_size,
            chunk_size,
            chunk_size == expected_size
        )
        
        # 청크 오버랩
        chunk_overlap = self.config.get_chunk_overlap()
        expected_overlap = 200
        self.log_test(
            "Chunk Overlap",
            expected_overlap,
            chunk_overlap,
            chunk_overlap == expected_overlap
        )
    
    def validate_dependency_injection_config(self):
        """의존성 주입 설정 검증"""
        print("=== 의존성 주입 설정 검증 ===")
        
        # 벡터 스토어 타입
        vector_store_type = self.config.get_vector_store_type()
        expected_type = "qdrant"
        self.log_test(
            "Vector Store Type",
            expected_type,
            vector_store_type,
            vector_store_type == expected_type
        )
        
        # 임베딩 타입
        embedding_type = self.config.get_embedding_type()
        expected_type = "openai"
        self.log_test(
            "Embedding Type",
            expected_type,
            embedding_type,
            embedding_type == expected_type
        )
        
        # 문서 로더 타입
        loader_type = self.config.get_document_loader_type()
        expected_type = "pdf"
        self.log_test(
            "Document Loader Type",
            expected_type,
            loader_type,
            loader_type == expected_type
        )
        
        # 텍스트 청커 타입
        chunker_type = self.config.get_text_chunker_type()
        expected_type = "recursive"
        self.log_test(
            "Text Chunker Type",
            expected_type,
            chunker_type,
            chunker_type == expected_type
        )
        
        # 리트리버 타입
        retriever_type = self.config.get_retriever_type()
        expected_type = "simple"
        self.log_test(
            "Retriever Type",
            expected_type,
            retriever_type,
            retriever_type == expected_type
        )
    
    def validate_llm_config(self):
        """LLM 설정 검증"""
        print("=== LLM 설정 검증 ===")
        
        # LLM 모델 타입
        llm_type = self.config.get_llm_model_type()
        expected_type = "openai"
        self.log_test(
            "LLM Model Type",
            expected_type,
            llm_type,
            llm_type == expected_type
        )
        
        # LLM 모델 이름
        llm_name = self.config.get_llm_model_name()
        expected_name = "gpt-3.5-turbo"
        self.log_test(
            "LLM Model Name",
            expected_name,
            llm_name,
            llm_name == expected_name
        )
        
        # LLM 온도
        temperature = self.config.get_llm_temperature()
        expected_temp = 0.7
        self.log_test(
            "LLM Temperature",
            expected_temp,
            temperature,
            temperature == expected_temp
        )
        
        # LLM 최대 토큰
        max_tokens = self.config.get_llm_max_tokens()
        expected_tokens = 1000
        self.log_test(
            "LLM Max Tokens",
            expected_tokens,
            max_tokens,
            max_tokens == expected_tokens
        )
    
    def validate_upload_config(self):
        """업로드 설정 검증"""
        print("=== 업로드 설정 검증 ===")
        
        # 최대 파일 크기
        max_size = self.config.get_upload_max_file_size()
        expected_size = 10485760  # 10MB
        self.log_test(
            "Upload Max File Size",
            expected_size,
            max_size,
            max_size == expected_size
        )
        
        # 허용된 확장자
        extensions = self.config.get_upload_allowed_extensions()
        expected_extensions = ["pdf", "txt", "json", "docx", "html"]
        self.log_test(
            "Upload Allowed Extensions",
            expected_extensions,
            extensions,
            extensions == expected_extensions
        )
        
        # 업로드 디렉토리
        upload_dir = self.config.get_upload_directory()
        expected_dir = "uploads"
        self.log_test(
            "Upload Directory",
            expected_dir,
            upload_dir,
            upload_dir == expected_dir
        )
    
    def validate_retrieval_config(self):
        """검색 설정 검증"""
        print("=== 검색 설정 검증 ===")
        
        # Top K
        top_k = self.config.get_retrieval_top_k()
        expected_k = 5
        self.log_test(
            "Retrieval Top K",
            expected_k,
            top_k,
            top_k == expected_k
        )
        
        # 점수 임계값
        score_threshold = self.config.get_retrieval_score_threshold()
        expected_threshold = 0.7
        self.log_test(
            "Retrieval Score Threshold",
            expected_threshold,
            score_threshold,
            score_threshold == expected_threshold
        )
    
    def validate_ensemble_config(self):
        """앙상블 설정 검증"""
        print("=== 앙상블 설정 검증 ===")
        
        # 앙상블 가중치
        weights = self.config.get_ensemble_weights()
        expected_weights = [0.5, 0.5]
        self.log_test(
            "Ensemble Weights",
            expected_weights,
            weights,
            weights == expected_weights
        )
        
        # 앙상블 검색 타입
        search_types = self.config.get_ensemble_search_types()
        expected_types = ["similarity", "mmr"]
        self.log_test(
            "Ensemble Search Types",
            expected_types,
            search_types,
            search_types == expected_types
        )
    
    def validate_environment_switching(self):
        """환경별 설정 전환 검증"""
        print("=== 환경별 설정 전환 검증 ===")
        
        # 현재 환경 확인
        current_env = os.getenv("ENVIRONMENT", "development")
        print(f"Current Environment: {current_env}")
        
        # Development 설정 테스트
        dev_config = ConfigAdapter(DevelopmentConfig())
        dev_debug = dev_config.get_debug()
        dev_log_level = dev_config.get_log_level()
        
        self.log_test(
            "Development Debug Mode",
            True,
            dev_debug,
            dev_debug == True
        )
        
        self.log_test(
            "Development Log Level",
            "DEBUG",
            dev_log_level,
            dev_log_level == "DEBUG"
        )
        
        # Test 설정 테스트
        test_config = ConfigAdapter(TestConfig())
        test_api_key = test_config.get_openai_api_key()
        test_max_size = test_config.get_upload_max_file_size()
        
        self.log_test(
            "Test OpenAI API Key",
            "test-key",
            test_api_key,
            test_api_key == "test-key"
        )
        
        self.log_test(
            "Test Upload Max Size",
            10*1024*1024,  # 10MB
            test_max_size,
            test_max_size == 10*1024*1024
        )
    
    def validate_config_port_interface(self):
        """ConfigPort 인터페이스 검증"""
        print("=== ConfigPort 인터페이스 검증 ===")
        
        # 모든 필수 메서드가 구현되어 있는지 확인
        required_methods = [
            'get_openai_api_key', 'get_qdrant_url', 'get_qdrant_api_key',
            'get_app_name', 'get_app_version', 'get_debug', 'get_host', 'get_port',
            'get_log_level', 'get_vector_dimension', 'get_collection_name',
            'get_embedding_model', 'get_chunk_size', 'get_chunk_overlap',
            'get_vector_store_type', 'get_embedding_type', 'get_document_loader_type',
            'get_text_chunker_type', 'get_retriever_type', 'get_llm_model_type',
            'get_llm_model_name', 'get_llm_temperature', 'get_llm_max_tokens',
            'get_upload_max_file_size', 'get_upload_allowed_extensions',
            'get_upload_directory', 'get_upload_temp_directory',
            'get_semantic_chunk_min_size', 'get_semantic_chunk_max_size',
            'get_semantic_similarity_threshold', 'get_retrieval_top_k',
            'get_retrieval_score_threshold', 'get_ensemble_weights',
            'get_ensemble_search_types'
        ]
        
        missing_methods = []
        for method_name in required_methods:
            if not hasattr(self.config, method_name):
                missing_methods.append(method_name)
        
        self.log_test(
            "All ConfigPort methods implemented",
            [],
            missing_methods,
            len(missing_methods) == 0
        )
        
        # 각 메서드가 실제로 호출 가능한지 확인
        callable_methods = []
        for method_name in required_methods:
            try:
                method = getattr(self.config, method_name)
                result = method()
                callable_methods.append(method_name)
            except Exception as e:
                print(f"Error calling {method_name}: {e}")
        
        self.log_test(
            "All ConfigPort methods callable",
            len(required_methods),
            len(callable_methods),
            len(callable_methods) == len(required_methods)
        )
    
    def run_all_validations(self):
        """모든 검증 실행"""
        print("🚀 실제 데이터를 사용한 설정 파일 검증 시작\n")
        
        self.validate_basic_config()
        self.validate_embedding_config()
        self.validate_dependency_injection_config()
        self.validate_llm_config()
        self.validate_upload_config()
        self.validate_retrieval_config()
        self.validate_ensemble_config()
        self.validate_environment_switching()
        self.validate_config_port_interface()
        
        # 결과 요약
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print("=" * 50)
        print("📊 검증 결과 요약")
        print("=" * 50)
        print(f"총 테스트: {total_tests}")
        print(f"성공: {passed_tests} ✅")
        print(f"실패: {failed_tests} ❌")
        print(f"성공률: {(passed_tests/total_tests)*100:.1f}%")
        
        if failed_tests > 0:
            print("\n❌ 실패한 테스트:")
            for result in self.test_results:
                if not result['passed']:
                    print(f"  - {result['test_name']}")
                    print(f"    Expected: {result['expected']}")
                    print(f"    Actual: {result['actual']}")
        
        return failed_tests == 0


def main():
    """메인 실행 함수"""
    validator = RealConfigValidator()
    success = validator.run_all_validations()
    
    if success:
        print("\n🎉 모든 설정이 올바르게 적용되었습니다!")
        return 0
    else:
        print("\n⚠️  일부 설정에 문제가 있습니다. 위의 실패한 테스트를 확인해주세요.")
        return 1


if __name__ == "__main__":
    exit(main())
