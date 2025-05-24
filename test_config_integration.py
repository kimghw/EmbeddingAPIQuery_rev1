#!/usr/bin/env python3
"""
설정 파일과 어댑터 팩토리 통합 테스트
실제 데이터를 사용하여 설정이 어댑터 생성에 올바르게 적용되는지 검증합니다.
"""

import os
import sys
from pathlib import Path

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import create_config, ConfigAdapter, DevelopmentConfig, TestConfig
from config.adapter_factory import (
    AdapterFactory, 
    get_vector_store_adapter,
    get_embedding_adapter,
    get_document_loader_adapter,
    get_text_chunker_adapter,
    get_retriever_adapter
)


class ConfigIntegrationTester:
    """설정과 어댑터 팩토리 통합 테스트"""
    
    def __init__(self):
        self.test_results = []
        self.config = create_config()
    
    def log_test(self, test_name: str, expected: str, actual: str, passed: bool):
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
    
    def test_vector_store_creation(self):
        """벡터 스토어 생성 테스트"""
        print("=== 벡터 스토어 생성 테스트 ===")
        
        # 설정에서 벡터 스토어 타입 확인
        vector_store_type = self.config.get_vector_store_type()
        print(f"설정된 벡터 스토어 타입: {vector_store_type}")
        
        # 어댑터 팩토리로 벡터 스토어 생성
        try:
            vector_store = get_vector_store_adapter(self.config)
            actual_type = type(vector_store).__name__
            
            # Qdrant 설정이면 QdrantVectorStore가 생성되어야 함
            if vector_store_type == "qdrant":
                expected_type = "QdrantVectorStore"
            elif vector_store_type == "faiss":
                expected_type = "FAISSVectorStore"
            else:
                expected_type = "MockVectorStore"
            
            self.log_test(
                "Vector Store Creation",
                expected_type,
                actual_type,
                expected_type in actual_type
            )
            
            # 벡터 스토어 설정 확인
            if hasattr(vector_store, 'collection_name'):
                collection_name = vector_store.collection_name
                expected_collection = self.config.get_collection_name()
                self.log_test(
                    "Vector Store Collection Name",
                    expected_collection,
                    collection_name,
                    collection_name == expected_collection
                )
            
        except Exception as e:
            self.log_test(
                "Vector Store Creation",
                "Success",
                f"Error: {str(e)}",
                False
            )
    
    def test_embedding_model_creation(self):
        """임베딩 모델 생성 테스트"""
        print("=== 임베딩 모델 생성 테스트 ===")
        
        # 설정에서 임베딩 타입 확인
        embedding_type = self.config.get_embedding_type()
        print(f"설정된 임베딩 타입: {embedding_type}")
        
        try:
            embedding_model = get_embedding_adapter(self.config)
            actual_type = type(embedding_model).__name__
            
            # OpenAI 설정이면 OpenAIEmbedding이 생성되어야 함
            if embedding_type == "openai":
                expected_type = "OpenAIEmbedding"
            else:
                expected_type = "MockEmbedding"
            
            self.log_test(
                "Embedding Model Creation",
                expected_type,
                actual_type,
                expected_type in actual_type
            )
            
            # 임베딩 모델 설정 확인
            if hasattr(embedding_model, 'model_name'):
                model_name = embedding_model.model_name
                expected_model = self.config.get_embedding_model()
                self.log_test(
                    "Embedding Model Name",
                    expected_model,
                    model_name,
                    model_name == expected_model
                )
            
        except Exception as e:
            self.log_test(
                "Embedding Model Creation",
                "Success",
                f"Error: {str(e)}",
                False
            )
    
    def test_document_loader_creation(self):
        """문서 로더 생성 테스트"""
        print("=== 문서 로더 생성 테스트 ===")
        
        # 설정에서 문서 로더 타입 확인
        loader_type = self.config.get_document_loader_type()
        print(f"설정된 문서 로더 타입: {loader_type}")
        
        try:
            document_loader = get_document_loader_adapter(self.config)
            actual_type = type(document_loader).__name__
            
            # PDF 설정이면 PdfLoaderAdapter가 생성되어야 함
            if loader_type == "pdf":
                expected_type = "PdfLoaderAdapter"
            elif loader_type == "json":
                expected_type = "JsonLoaderAdapter"
            elif loader_type == "web_scraper":
                expected_type = "WebScraperLoaderAdapter"
            elif loader_type == "unstructured":
                expected_type = "UnstructuredLoaderAdapter"
            else:
                expected_type = "MockLoaderAdapter"
            
            self.log_test(
                "Document Loader Creation",
                expected_type,
                actual_type,
                expected_type in actual_type
            )
            
        except Exception as e:
            self.log_test(
                "Document Loader Creation",
                "Success",
                f"Error: {str(e)}",
                False
            )
    
    def test_text_chunker_creation(self):
        """텍스트 청커 생성 테스트"""
        print("=== 텍스트 청커 생성 테스트 ===")
        
        # 설정에서 텍스트 청커 타입 확인
        chunker_type = self.config.get_text_chunker_type()
        print(f"설정된 텍스트 청커 타입: {chunker_type}")
        
        try:
            text_chunker = get_text_chunker_adapter(self.config)
            actual_type = type(text_chunker).__name__
            
            # Recursive 설정이면 TextChunker가 생성되어야 함
            if chunker_type == "recursive":
                expected_type = "TextChunker"
            elif chunker_type == "semantic":
                expected_type = "SemanticTextChunker"
            else:
                expected_type = "MockChunker"
            
            self.log_test(
                "Text Chunker Creation",
                expected_type,
                actual_type,
                expected_type in actual_type
            )
            
            # 청크 크기 설정 확인
            if hasattr(text_chunker, 'chunk_size'):
                chunk_size = text_chunker.chunk_size
                expected_size = self.config.get_chunk_size()
                self.log_test(
                    "Text Chunker Size",
                    expected_size,
                    chunk_size,
                    chunk_size == expected_size
                )
            
            # 청크 오버랩 설정 확인
            if hasattr(text_chunker, 'chunk_overlap'):
                chunk_overlap = text_chunker.chunk_overlap
                expected_overlap = self.config.get_chunk_overlap()
                self.log_test(
                    "Text Chunker Overlap",
                    expected_overlap,
                    chunk_overlap,
                    chunk_overlap == expected_overlap
                )
            
        except Exception as e:
            self.log_test(
                "Text Chunker Creation",
                "Success",
                f"Error: {str(e)}",
                False
            )
    
    def test_retriever_creation(self):
        """리트리버 생성 테스트"""
        print("=== 리트리버 생성 테스트 ===")
        
        # 설정에서 리트리버 타입 확인
        retriever_type = self.config.get_retriever_type()
        print(f"설정된 리트리버 타입: {retriever_type}")
        
        try:
            retriever = get_retriever_adapter(self.config)
            actual_type = type(retriever).__name__
            
            # Simple 설정이면 SimpleRetriever가 생성되어야 함
            if retriever_type == "simple":
                expected_type = "SimpleRetriever"
            elif retriever_type == "ensemble":
                expected_type = "EnsembleRetriever"
            else:
                expected_type = "MockRetriever"
            
            self.log_test(
                "Retriever Creation",
                expected_type,
                actual_type,
                expected_type in actual_type
            )
            
        except Exception as e:
            self.log_test(
                "Retriever Creation",
                "Success",
                f"Error: {str(e)}",
                False
            )
    
    def test_environment_specific_config(self):
        """환경별 설정 테스트"""
        print("=== 환경별 설정 테스트 ===")
        
        # Test 환경 설정 테스트
        test_config = ConfigAdapter(TestConfig())
        
        # Test 환경에서는 test-key를 사용해야 함
        api_key = test_config.get_openai_api_key()
        self.log_test(
            "Test Environment API Key",
            "test-key",
            api_key,
            api_key == "test-key"
        )
        
        # Development 환경 설정 테스트
        dev_config = ConfigAdapter(DevelopmentConfig())
        log_level = dev_config.get_log_level()
        self.log_test(
            "Development Environment Log Level",
            "DEBUG",
            log_level,
            log_level == "DEBUG"
        )
    
    def test_config_consistency(self):
        """설정 일관성 테스트"""
        print("=== 설정 일관성 테스트 ===")
        
        # 같은 설정으로 여러 번 어댑터를 생성해도 동일한 타입이어야 함
        try:
            vector_store1 = get_vector_store_adapter(self.config)
            vector_store2 = get_vector_store_adapter(self.config)
            
            type1 = type(vector_store1).__name__
            type2 = type(vector_store2).__name__
            
            self.log_test(
                "Vector Store Consistency",
                type1,
                type2,
                type1 == type2
            )
            
        except Exception as e:
            self.log_test(
                "Vector Store Consistency",
                "Success",
                f"Error: {str(e)}",
                False
            )
    
    def run_all_tests(self):
        """모든 통합 테스트 실행"""
        print("🚀 설정 파일과 어댑터 팩토리 통합 테스트 시작\n")
        
        self.test_vector_store_creation()
        self.test_embedding_model_creation()
        self.test_document_loader_creation()
        self.test_text_chunker_creation()
        self.test_retriever_creation()
        self.test_environment_specific_config()
        self.test_config_consistency()
        
        # 결과 요약
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results if result['passed'])
        failed_tests = total_tests - passed_tests
        
        print("=" * 50)
        print("📊 통합 테스트 결과 요약")
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
    tester = ConfigIntegrationTester()
    success = tester.run_all_tests()
    
    if success:
        print("\n🎉 모든 설정이 어댑터 팩토리와 올바르게 통합되었습니다!")
        return 0
    else:
        print("\n⚠️  일부 통합 테스트에 문제가 있습니다. 위의 실패한 테스트를 확인해주세요.")
        return 1


if __name__ == "__main__":
    exit(main())
