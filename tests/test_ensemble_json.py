"""
EnsembleRetriever 수정된 테스트 스크립트
"""

import asyncio
import json
from pathlib import Path
from core.entities.document import Query
from adapters.vector_store.ensemble_retriever import EnsembleRetrieverAdapter, FusionStrategy
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.pdf.json_loader import JsonLoaderAdapter


async def test_ensemble_retriever():
    """EnsembleRetriever 기능 테스트"""
    print("=== EnsembleRetriever 테스트 시작 ===")
    
    try:
        # Mock 벡터 스토어들 생성 (실제 외부 의존성 없이 테스트)
        mock_store1 = MockVectorStoreAdapter()
        mock_store2 = MockVectorStoreAdapter()
        mock_store3 = MockVectorStoreAdapter()
        
        # Mock 임베딩 모델 (간단한 더미 클래스)
        class MockEmbeddingModel:
            def get_model_name(self):
                return "mock-embedding"
            
            def get_dimension(self):
                return 384
            
            def is_available(self):
                return True
            
            async def embed_query(self, text):
                # 간단한 더미 벡터 반환
                return [0.1] * 384
        
        embedding_model = MockEmbeddingModel()
        
        # 개별 리트리버들 생성
        retriever1 = SimpleRetrieverAdapter(mock_store1, embedding_model)
        retriever2 = SimpleRetrieverAdapter(mock_store2, embedding_model)
        retriever3 = SimpleRetrieverAdapter(mock_store3, embedding_model)
        
        retrievers = [retriever1, retriever2, retriever3]
        
        print("\n1. Rank Fusion 전략 테스트")
        ensemble_rrf = EnsembleRetrieverAdapter(
            retrievers=retrievers,
            fusion_strategy=FusionStrategy.RANK_FUSION,
            rrf_k=60
        )
        
        print(f"앙상블 리트리버 타입: {ensemble_rrf.get_retriever_type()}")
        
        # 리트리버 정보 출력
        info = await ensemble_rrf.get_retriever_info()
        print(f"리트리버 정보: {json.dumps(info, indent=2, ensure_ascii=False)}")
        
        print("\n2. Score Fusion 전략 테스트")
        ensemble_score = EnsembleRetrieverAdapter(
            retrievers=retrievers,
            fusion_strategy=FusionStrategy.SCORE_FUSION
        )
        
        print(f"앙상블 리트리버 타입: {ensemble_score.get_retriever_type()}")
        
        print("\n3. Weighted Score 전략 테스트")
        ensemble_weighted = EnsembleRetrieverAdapter(
            retrievers=retrievers,
            fusion_strategy=FusionStrategy.WEIGHTED_SCORE,
            weights=[0.5, 0.3, 0.2]  # 첫 번째 리트리버에 더 높은 가중치
        )
        
        print(f"앙상블 리트리버 타입: {ensemble_weighted.get_retriever_type()}")
        
        print("\n4. Voting 전략 테스트")
        ensemble_voting = EnsembleRetrieverAdapter(
            retrievers=retrievers,
            fusion_strategy=FusionStrategy.VOTING
        )
        
        print(f"앙상블 리트리버 타입: {ensemble_voting.get_retriever_type()}")
        
        print("\n5. 검색 테스트 (Mock 데이터 사용)")
        try:
            # Mock retriever만 사용해서 테스트 (실제 데이터 없이도 동작)
            mock_ensemble = EnsembleRetrieverAdapter(
                retrievers=[retriever1],
                fusion_strategy=FusionStrategy.RANK_FUSION
            )
            
            results = await mock_ensemble.retrieve_by_text(
                "test query",
                top_k=5
            )
            
            print(f"검색 결과 수: {len(results)}")
            for i, result in enumerate(results):
                print(f"  {i+1}. Score: {result.score:.4f}, Rank: {result.rank}")
                print(f"     Content: {result.content[:100]}...")
                
        except Exception as e:
            print(f"검색 테스트 중 오류: {e}")
        
        print("\n6. 헬스 체크 테스트")
        health = await ensemble_rrf.health_check()
        print(f"앙상블 리트리버 헬스 상태: {health}")
        
        print("\n7. 동적 리트리버 추가/제거 테스트")
        # 새로운 앙상블 생성
        dynamic_ensemble = EnsembleRetrieverAdapter(
            retrievers=[retriever1],
            fusion_strategy=FusionStrategy.RANK_FUSION
        )
        
        print(f"초기 리트리버 수: {len(dynamic_ensemble._retrievers)}")
        
        # 리트리버 추가
        dynamic_ensemble.add_retriever(retriever2, weight=0.7)
        print(f"추가 후 리트리버 수: {len(dynamic_ensemble._retrievers)}")
        
        # 리트리버 제거
        dynamic_ensemble.remove_retriever(0)
        print(f"제거 후 리트리버 수: {len(dynamic_ensemble._retrievers)}")
        
        # 전략 변경
        dynamic_ensemble.set_fusion_strategy(FusionStrategy.SCORE_FUSION)
        print(f"변경된 전략: {dynamic_ensemble.get_retriever_type()}")
        
        # 가중치 변경
        dynamic_ensemble.set_weights([1.0])
        print("가중치 변경 완료")
        
        print("\n=== EnsembleRetriever 테스트 완료 ===")
        
    except Exception as e:
        print(f"테스트 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


async def test_json_loader():
    """JSON 로더 테스트"""
    print("\n=== JSON 로더 테스트 시작 ===")
    
    try:
        # JSON 로더 생성
        json_loader = JsonLoaderAdapter()
        
        print(f"로더 타입: {json_loader.get_loader_type()}")
        print(f"지원 형식: {json_loader.get_supported_formats()}")
        
        # 테스트용 JSON 데이터 생성
        test_data = {
            "title": "Machine Learning Basics",
            "content": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            "author": "AI Researcher",
            "tags": ["AI", "ML", "Technology"],
            "metadata": {
                "created_date": "2024-01-01",
                "category": "Education"
            }
        }
        
        # 임시 JSON 파일 생성
        test_file = Path("test_data.json")
        with open(test_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f, ensure_ascii=False, indent=2)
        
        print(f"\n테스트 파일 생성: {test_file}")
        
        # 파일 유효성 검사
        is_valid = await json_loader.validate_file(str(test_file))
        print(f"파일 유효성: {is_valid}")
        
        # 파일에서 문서 로드
        document = await json_loader.load_from_file(str(test_file))
        
        print(f"\n로드된 문서:")
        print(f"  ID: {document.id}")  # document_id가 아니라 id
        print(f"  제목: {document.title}")
        print(f"  내용 길이: {len(document.content)}")
        print(f"  내용 미리보기: {document.content[:200]}...")
        print(f"  메타데이터 키: {list(document.metadata.keys())}")
        
        # 바이트에서 로드 테스트
        with open(test_file, 'rb') as f:
            file_bytes = f.read()
        
        document_from_bytes = await json_loader.load_from_bytes(
            file_bytes, 
            "test_data.json"
        )
        
        print(f"\n바이트에서 로드된 문서:")
        print(f"  ID: {document_from_bytes.id}")  # document_id가 아니라 id
        print(f"  제목: {document_from_bytes.title}")
        
        # JSONL 테스트 데이터 생성
        jsonl_data = [
            {"id": 1, "text": "First line of JSONL data"},
            {"id": 2, "text": "Second line of JSONL data"},
            {"id": 3, "text": "Third line of JSONL data"}
        ]
        
        jsonl_file = Path("test_data.jsonl")
        with open(jsonl_file, 'w', encoding='utf-8') as f:
            for item in jsonl_data:
                f.write(json.dumps(item, ensure_ascii=False) + '\n')
        
        print(f"\nJSONL 테스트 파일 생성: {jsonl_file}")
        
        # JSONL 파일 로드
        jsonl_document = await json_loader.load_from_file(str(jsonl_file))
        
        print(f"JSONL 문서:")
        print(f"  ID: {jsonl_document.id}")  # document_id가 아니라 id
        print(f"  제목: {jsonl_document.title}")
        print(f"  내용 미리보기: {jsonl_document.content[:100]}...")
        
        # 여러 파일 로드 테스트
        multiple_docs = await json_loader.load_multiple_files([
            str(test_file),
            str(jsonl_file)
        ])
        
        print(f"\n여러 파일 로드 결과: {len(multiple_docs)}개 문서")
        for i, doc in enumerate(multiple_docs):
            print(f"  문서 {i+1}: {doc.title}")
        
        # 정리
        test_file.unlink()
        jsonl_file.unlink()
        print("\n테스트 파일 정리 완료")
        
        print("=== JSON 로더 테스트 완료 ===")
        
    except Exception as e:
        print(f"JSON 로더 테스트 중 오류: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """메인 테스트 함수"""
    print("EnsembleRetriever와 JSON 로더 통합 테스트")
    print("=" * 50)
    
    # JSON 로더 테스트
    await test_json_loader()
    
    # EnsembleRetriever 테스트
    await test_ensemble_retriever()
    
    print("\n모든 테스트 완료!")


if __name__ == "__main__":
    asyncio.run(main())
