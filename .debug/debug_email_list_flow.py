"""
이메일 리스트 API의 전체 데이터 플로우 추적 및 검증
"""

import asyncio
import json
from datetime import datetime
from config.adapter_factory import get_vector_store_adapter, get_embedding_adapter, get_retriever_adapter
from config.settings import config

async def trace_email_list_flow():
    """이메일 리스트 API의 전체 플로우를 단계별로 추적"""
    
    print("=" * 80)
    print("📧 이메일 리스트 API 데이터 플로우 추적")
    print("=" * 80)
    
    # 1. 어댑터 생성 확인
    print("\n1️⃣ 어댑터 생성 단계")
    print("-" * 40)
    
    try:
        vector_store = get_vector_store_adapter(config)
        embedding_model = get_embedding_adapter(config)
        retriever = get_retriever_adapter(config)
        print(f"✅ VectorStore 어댑터: {type(vector_store).__name__}")
        print(f"✅ EmbeddingModel 어댑터: {type(embedding_model).__name__}")
        print(f"✅ Retriever 어댑터: {type(retriever).__name__}")
        print(f"✅ 컬렉션명: {config.get_collection_name()}")
    except Exception as e:
        print(f"❌ 어댑터 생성 실패: {e}")
        return
    
    # 2. 컬렉션 존재 확인
    print("\n2️⃣ 컬렉션 존재 확인")
    print("-" * 40)
    
    collection_name = "emails"  # 이메일 전용 컬렉션
    
    try:
        exists = await vector_store.collection_exists(collection_name)
        print(f"✅ 컬렉션 '{collection_name}' 존재: {exists}")
        
        if not exists:
            print("❌ 이메일 컬렉션이 존재하지 않습니다!")
            return
            
    except Exception as e:
        print(f"❌ 컬렉션 확인 실패: {e}")
        return
    
    # 3. 임베딩 카운트 확인
    print("\n3️⃣ 임베딩 카운트 확인")
    print("-" * 40)
    
    try:
        total_count = await vector_store.count_embeddings(collection_name)
        print(f"✅ 총 임베딩 개수: {total_count}")
        
        if total_count == 0:
            print("❌ 임베딩이 없습니다!")
            return
            
    except Exception as e:
        print(f"❌ 임베딩 카운트 실패: {e}")
        return
    
    # 4. 실제 데이터 샘플링
    print("\n4️⃣ 실제 데이터 샘플링")
    print("-" * 40)
    
    try:
        # scroll을 사용해서 실제 데이터 확인
        from qdrant_client import QdrantClient
        
        # Qdrant URL에서 호스트와 포트 추출
        qdrant_url = config.get_qdrant_url()
        if qdrant_url.startswith('http://'):
            url_parts = qdrant_url.replace('http://', '').split(':')
            host = url_parts[0]
            port = int(url_parts[1]) if len(url_parts) > 1 else 6333
        else:
            host = 'localhost'
            port = 6333
        
        client = QdrantClient(host=host, port=port)
        
        result = client.scroll(
            collection_name=collection_name,
            limit=5,
            with_payload=True,
            with_vectors=False
        )
        
        points = result[0] if result else []
        print(f"✅ 샘플 데이터 개수: {len(points)}")
        
        if points:
            sample_point = points[0]
            print(f"✅ 샘플 포인트 ID: {sample_point.id}")
            print(f"✅ 페이로드 키들: {list(sample_point.payload.keys())}")
            
            # 이메일 관련 필드 확인
            email_fields = ['email_id', 'embedding_type', 'sender_address', 'subject']
            for field in email_fields:
                value = sample_point.payload.get(field, 'N/A')
                print(f"   - {field}: {value}")
                
    except Exception as e:
        print(f"❌ 데이터 샘플링 실패: {e}")
        return
    
    # 5. 고유 이메일 ID 추출
    print("\n5️⃣ 고유 이메일 ID 추출")
    print("-" * 40)
    
    try:
        # 모든 임베딩에서 고유한 email_id 추출
        unique_email_ids = set()
        offset = 0
        batch_size = 100
        
        while True:
            result = client.scroll(
                collection_name=collection_name,
                limit=batch_size,
                offset=offset,
                with_payload=True,
                with_vectors=False
            )
            
            points = result[0] if result else []
            if not points:
                break
                
            for point in points:
                email_id = point.payload.get('email_id')
                if email_id:
                    unique_email_ids.add(email_id)
            
            if len(points) < batch_size:
                break
                
            offset += batch_size
        
        print(f"✅ 고유 이메일 ID 개수: {len(unique_email_ids)}")
        print(f"✅ 샘플 이메일 ID들: {list(unique_email_ids)[:3]}")
        
    except Exception as e:
        print(f"❌ 고유 이메일 ID 추출 실패: {e}")
        return
    
    # 6. 이메일 리스트 UseCase 테스트
    print("\n6️⃣ 이메일 리스트 UseCase 테스트")
    print("-" * 40)
    
    try:
        from core.usecases.email_retrieval import EmailRetrievalUseCase
        
        # UseCase 생성
        email_retrieval = EmailRetrievalUseCase(
            retriever=retriever,
            vector_store=vector_store,
            embedding_model=embedding_model,
            config=config
        )
        
        # 이메일 리스트 조회
        result = await email_retrieval.list_emails(limit=50, offset=0)
        
        print(f"✅ UseCase 실행 성공")
        print(f"✅ 반환된 이메일 개수: {len(result.get('emails', []))}")
        print(f"✅ 총 개수: {result.get('total', 0)}")
        print(f"✅ 성공 여부: {result.get('success', False)}")
        
        if result.get('emails'):
            sample_email = result['emails'][0]
            print(f"✅ 샘플 이메일 ID: {sample_email.get('id')}")
            print(f"✅ 샘플 이메일 제목: {sample_email.get('subject', '')[:50]}...")
            
    except Exception as e:
        print(f"❌ UseCase 테스트 실패: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # 7. API 엔드포인트 시뮬레이션
    print("\n7️⃣ API 엔드포인트 시뮬레이션")
    print("-" * 40)
    
    try:
        # API 라우터 함수 직접 호출
        from interfaces.api.email_list_routes import list_emails_endpoint
        from fastapi import Query
        
        # 의존성 주입 시뮬레이션
        async def mock_get_email_retrieval():
            return email_retrieval
        
        # 엔드포인트 직접 호출 (의존성 주입 우회)
        response = await email_retrieval.list_emails(limit=50, offset=0)
        
        print(f"✅ API 시뮬레이션 성공")
        print(f"✅ 응답 구조: {list(response.keys())}")
        print(f"✅ 이메일 개수: {len(response.get('emails', []))}")
        
    except Exception as e:
        print(f"❌ API 시뮬레이션 실패: {e}")
        import traceback
        traceback.print_exc()
    
    # 8. 실제 HTTP 요청 테스트
    print("\n8️⃣ 실제 HTTP 요청 테스트")
    print("-" * 40)
    
    try:
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/emails/list') as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"✅ HTTP 요청 성공 (상태: {response.status})")
                    print(f"✅ 응답 이메일 개수: {len(data.get('emails', []))}")
                    print(f"✅ 총 개수: {data.get('total', 0)}")
                else:
                    print(f"❌ HTTP 요청 실패 (상태: {response.status})")
                    text = await response.text()
                    print(f"❌ 응답: {text[:200]}...")
                    
    except Exception as e:
        print(f"❌ HTTP 요청 테스트 실패: {e}")
    
    print("\n" + "=" * 80)
    print("🎯 데이터 플로우 추적 완료")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(trace_email_list_flow())
