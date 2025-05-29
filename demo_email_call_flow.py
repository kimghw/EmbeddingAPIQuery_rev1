"""
이메일 시스템 호출 흐름 데모
실제 함수 호출 순서와 데이터 흐름을 보여줍니다.
"""

import asyncio
import json
from datetime import datetime
from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from core.usecases.email_retrieval import EmailRetrievalUseCase
from adapters.vector_store.qdrant_email_adapter import QdrantEmailVectorStoreAdapter
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from config.settings import config


class CallFlowTracker:
    """호출 흐름을 추적하는 클래스"""
    
    def __init__(self):
        self.call_stack = []
        self.indent_level = 0
    
    def log_call(self, function_name: str, params: str = "", result: str = ""):
        """함수 호출을 로깅"""
        indent = "  " * self.indent_level
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        
        if result:
            print(f"{timestamp} {indent}← {function_name} → {result}")
        else:
            print(f"{timestamp} {indent}→ {function_name}({params})")
            self.call_stack.append(function_name)
    
    def enter_function(self, function_name: str, params: str = ""):
        """함수 진입"""
        self.log_call(function_name, params)
        self.indent_level += 1
    
    def exit_function(self, function_name: str, result: str = ""):
        """함수 종료"""
        self.indent_level -= 1
        self.log_call(function_name, result=result)


# 전역 트래커
tracker = CallFlowTracker()


async def demo_email_list_flow():
    """이메일 목록 조회 흐름 데모"""
    print("\n" + "="*80)
    print("📋 이메일 목록 조회 호출 흐름 데모")
    print("="*80)
    
    # 1. 컴포넌트 초기화
    tracker.enter_function("initialize_components")
    
    embedding_model = OpenAIEmbeddingAdapter(config=config)
    vector_store = QdrantEmailVectorStoreAdapter(
        host="localhost", port=6333, vector_dimension=1536
    )
    retriever = SimpleRetrieverAdapter(
        vector_store=vector_store, embedding_model=embedding_model
    )
    retriever.set_collection_name("emails")
    
    email_retrieval = EmailRetrievalUseCase(
        retriever=retriever,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    tracker.exit_function("initialize_components", "✅ 컴포넌트 초기화 완료")
    
    # 2. 이메일 목록 조회
    tracker.enter_function("EmailRetrievalUseCase.list_emails", "limit=5, offset=0")
    
    # 실제 호출
    result = await email_retrieval.list_emails(limit=5, offset=0)
    
    tracker.exit_function("EmailRetrievalUseCase.list_emails", 
                         f"✅ {result['returned']}개 이메일 반환")
    
    # 결과 출력
    print(f"\n📊 결과:")
    print(f"   - 성공: {result['success']}")
    print(f"   - 총 이메일: {result['total']}")
    print(f"   - 반환된 이메일: {result['returned']}")
    print(f"   - 컬렉션 존재: {result['collection_exists']}")
    
    if result['emails']:
        print(f"\n📧 첫 번째 이메일:")
        email = result['emails'][0]
        print(f"   - ID: {email['id'][:20]}...")
        print(f"   - 제목: {email['subject'][:50]}...")
        print(f"   - 발신자: {email['sender_address']}")
        print(f"   - 임베딩 수: {email['embeddings_count']}")


async def demo_email_search_flow():
    """이메일 검색 호출 흐름 데모"""
    print("\n" + "="*80)
    print("🔍 이메일 검색 호출 흐름 데모")
    print("="*80)
    
    # 1. 컴포넌트 초기화 (재사용)
    tracker.enter_function("initialize_search_components")
    
    embedding_model = OpenAIEmbeddingAdapter(config=config)
    vector_store = QdrantEmailVectorStoreAdapter(
        host="localhost", port=6333, vector_dimension=1536
    )
    retriever = SimpleRetrieverAdapter(
        vector_store=vector_store, embedding_model=embedding_model
    )
    retriever.set_collection_name("emails")
    
    email_retrieval = EmailRetrievalUseCase(
        retriever=retriever,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    tracker.exit_function("initialize_search_components", "✅ 검색 컴포넌트 초기화 완료")
    
    # 2. 검색 쿼리 실행
    search_query = "maritime safety"
    tracker.enter_function("EmailRetrievalUseCase.search_emails", 
                          f"query='{search_query}', top_k=3")
    
    # 실제 검색 호출
    search_result = await email_retrieval.search_emails(
        query_text=search_query,
        top_k=3,
        search_type="both"
    )
    
    tracker.exit_function("EmailRetrievalUseCase.search_emails", 
                         f"✅ {search_result['total_results']}개 결과 반환")
    
    # 검색 결과 출력
    print(f"\n🎯 검색 결과:")
    print(f"   - 쿼리: '{search_query}'")
    print(f"   - 성공: {search_result['success']}")
    print(f"   - 결과 수: {search_result['total_results']}")
    print(f"   - 검색 타입: {search_result['search_type']}")
    
    if search_result['results']:
        print(f"\n📧 검색된 이메일들:")
        for i, result in enumerate(search_result['results'][:2]):
            print(f"   [{i+1}] 점수: {result['score']:.4f}")
            print(f"       제목: {result['subject'][:50]}...")
            print(f"       발신자: {result['sender_address']}")
            print(f"       타입: {result['embedding_type']}")


async def demo_email_processing_flow():
    """이메일 처리 호출 흐름 데모"""
    print("\n" + "="*80)
    print("📧 이메일 처리 호출 흐름 데모")
    print("="*80)
    
    # 1. 컴포넌트 초기화
    tracker.enter_function("initialize_processing_components")
    
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = OpenAIEmbeddingAdapter(config=config)
    vector_store = QdrantEmailVectorStoreAdapter(
        host="localhost", port=6333, vector_dimension=1536
    )
    
    email_processor = EmailProcessingUseCase(
        email_loader=email_loader,
        embedding_model=embedding_model,
        vector_store=vector_store,
        config=config
    )
    
    tracker.exit_function("initialize_processing_components", "✅ 처리 컴포넌트 초기화 완료")
    
    # 2. 샘플 데이터 로드
    tracker.enter_function("load_sample_data", "sample_emails.json")
    
    with open("sample_emails.json", "r", encoding="utf-8") as f:
        sample_data = json.load(f)
    
    tracker.exit_function("load_sample_data", f"✅ {len(sample_data.get('value', []))}개 이메일 로드")
    
    # 3. 이메일 처리 (컬렉션이 이미 존재하므로 빠르게 처리됨)
    tracker.enter_function("EmailProcessingUseCase.process_emails_from_json")
    
    # 기존 컬렉션 삭제 후 재생성 (데모용)
    if await vector_store.collection_exists("emails"):
        await vector_store.delete_collection("emails")
        tracker.log_call("delete_existing_collection", result="✅ 기존 컬렉션 삭제")
    
    # 실제 처리 호출
    process_result = await email_processor.process_emails_from_json(sample_data)
    
    tracker.exit_function("EmailProcessingUseCase.process_emails_from_json", 
                         f"✅ {process_result['processed_count']}개 이메일 처리 완료")
    
    # 처리 결과 출력
    print(f"\n⚙️ 처리 결과:")
    print(f"   - 성공: {process_result['success']}")
    print(f"   - 처리된 이메일: {process_result['processed_count']}")
    print(f"   - 생성된 임베딩: {process_result['embedded_count']}")
    print(f"   - 컬렉션: {process_result['collection_name']}")
    
    if 'statistics' in process_result:
        stats = process_result['statistics']
        print(f"\n📊 통계:")
        print(f"   - 총 이메일: {stats['email_counts']['total']}")
        print(f"   - 답장: {stats['email_counts']['replies']}")
        print(f"   - 전달: {stats['email_counts']['forwards']}")
        print(f"   - 평균 제목 길이: {stats['content_statistics']['avg_subject_length']}")
        print(f"   - 평균 본문 길이: {stats['content_statistics']['avg_body_length']}")


async def demo_component_interaction():
    """컴포넌트 간 상호작용 데모"""
    print("\n" + "="*80)
    print("🔄 컴포넌트 간 상호작용 데모")
    print("="*80)
    
    # 각 어댑터의 타입과 기능 확인
    tracker.enter_function("check_adapter_types")
    
    email_loader = JsonEmailLoaderAdapter()
    embedding_model = OpenAIEmbeddingAdapter(config=config)
    vector_store = QdrantEmailVectorStoreAdapter(
        host="localhost", port=6333, vector_dimension=1536
    )
    retriever = SimpleRetrieverAdapter(
        vector_store=vector_store, embedding_model=embedding_model
    )
    
    print(f"\n🔧 어댑터 정보:")
    print(f"   - Email Loader: {email_loader.get_loader_type()}")
    print(f"   - Embedding Model: {embedding_model.get_model_name()}")
    print(f"   - Vector Store: {vector_store.get_store_type()}")
    print(f"   - Retriever: {retriever.get_retriever_type()}")
    
    tracker.exit_function("check_adapter_types", "✅ 어댑터 타입 확인 완료")
    
    # 의존성 주입 확인
    tracker.enter_function("check_dependency_injection")
    
    print(f"\n🔗 의존성 관계:")
    print(f"   - EmailProcessingUseCase → EmailLoader, EmbeddingModel, VectorStore")
    print(f"   - EmailRetrievalUseCase → Retriever, EmbeddingModel, VectorStore")
    print(f"   - SimpleRetriever → VectorStore, EmbeddingModel")
    print(f"   - QdrantVectorStore → Qdrant Client")
    print(f"   - OpenAIEmbedding → OpenAI API")
    
    tracker.exit_function("check_dependency_injection", "✅ 의존성 관계 확인 완료")


async def main():
    """메인 데모 실행"""
    print("🚀 이메일 시스템 호출 흐름 데모 시작")
    print("=" * 80)
    
    try:
        # 1. 이메일 처리 흐름
        await demo_email_processing_flow()
        
        # 2. 이메일 목록 조회 흐름
        await demo_email_list_flow()
        
        # 3. 이메일 검색 흐름
        await demo_email_search_flow()
        
        # 4. 컴포넌트 상호작용
        await demo_component_interaction()
        
        print("\n" + "="*80)
        print("🎉 모든 호출 흐름 데모 완료!")
        print("="*80)
        
        print(f"\n📋 전체 호출 스택:")
        for i, call in enumerate(tracker.call_stack, 1):
            print(f"   {i:2d}. {call}")
            
    except Exception as e:
        print(f"\n❌ 데모 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
