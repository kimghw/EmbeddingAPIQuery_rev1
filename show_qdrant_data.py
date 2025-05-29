#!/usr/bin/env python3
"""
Qdrant에 저장된 데이터 출력 스크립트
"""

import asyncio
import json
from config.adapter_factory import get_vector_store

async def show_qdrant_data():
    print("🔍 Qdrant에 저장된 데이터 출력 중...")
    print("=" * 80)
    
    try:
        vector_store = get_vector_store()
        
        # 1. 컬렉션 목록 확인
        print("1️⃣ 사용 가능한 컬렉션:")
        collections = await vector_store.list_collections()
        for i, collection in enumerate(collections, 1):
            print(f"   {i}. {collection}")
        print()
        
        # 2. emails 컬렉션 데이터 상세 출력
        if 'emails' in collections:
            print("2️⃣ 'emails' 컬렉션 데이터:")
            all_embeddings = await vector_store.get_all_embeddings('emails')
            print(f"   📊 총 임베딩 수: {len(all_embeddings)}")
            print()
            
            # 각 임베딩 상세 정보 출력
            for i, embedding in enumerate(all_embeddings, 1):
                print(f"   📧 임베딩 {i}:")
                print(f"      🆔 ID: {embedding.id}")
                
                # 메타데이터 출력
                if hasattr(embedding, 'payload') and embedding.payload:
                    payload = embedding.payload
                    print(f"      📋 메타데이터:")
                    print(f"         - Type: {payload.get('type', 'N/A')}")
                    print(f"         - Email ID: {payload.get('email_id', 'N/A')}")
                    print(f"         - Thread ID: {payload.get('thread_id', 'N/A')}")
                    print(f"         - Sender: {payload.get('sender', 'N/A')}")
                    print(f"         - Subject: {payload.get('subject', 'N/A')}")
                    print(f"         - Created: {payload.get('created_datetime', 'N/A')}")
                    print(f"         - Has Attachments: {payload.get('has_attachments', 'N/A')}")
                    
                    # 내용 미리보기 (처음 200자)
                    content = payload.get('content', '')
                    if content:
                        preview = content[:200] + "..." if len(content) > 200 else content
                        print(f"         - Content Preview: {preview}")
                    
                    # 벡터 정보
                    if hasattr(embedding, 'vector') and embedding.vector:
                        print(f"         - Vector Dimension: {len(embedding.vector)}")
                        print(f"         - Vector Preview: [{embedding.vector[0]:.4f}, {embedding.vector[1]:.4f}, ...]")
                else:
                    print(f"      ⚠️  메타데이터 없음")
                
                print()
        
        # 3. 다른 컬렉션들도 간단히 확인
        for collection in collections:
            if collection != 'emails':
                print(f"3️⃣ '{collection}' 컬렉션:")
                try:
                    embeddings = await vector_store.get_all_embeddings(collection)
                    print(f"   📊 임베딩 수: {len(embeddings)}")
                    
                    if embeddings:
                        # 첫 번째 임베딩만 샘플로 출력
                        sample = embeddings[0]
                        print(f"   📄 샘플 임베딩:")
                        print(f"      🆔 ID: {sample.id}")
                        if hasattr(sample, 'payload') and sample.payload:
                            payload = sample.payload
                            print(f"      📋 메타데이터 키: {list(payload.keys())}")
                            # 내용이 있으면 미리보기
                            if 'content' in payload:
                                content = payload['content']
                                preview = content[:100] + "..." if len(content) > 100 else content
                                print(f"      📝 내용 미리보기: {preview}")
                    print()
                except Exception as e:
                    print(f"   ❌ 컬렉션 '{collection}' 읽기 실패: {e}")
                    print()
        
        # 4. 통계 정보
        print("4️⃣ 통계 정보:")
        if 'emails' in collections:
            email_embeddings = await vector_store.get_all_embeddings('emails')
            
            # 타입별 분류
            type_counts = {}
            thread_counts = {}
            sender_counts = {}
            
            for embedding in email_embeddings:
                if hasattr(embedding, 'payload') and embedding.payload:
                    payload = embedding.payload
                    
                    # 타입별 카운트
                    embed_type = payload.get('type', 'unknown')
                    type_counts[embed_type] = type_counts.get(embed_type, 0) + 1
                    
                    # 스레드별 카운트
                    thread_id = payload.get('thread_id', 'unknown')
                    thread_counts[thread_id] = thread_counts.get(thread_id, 0) + 1
                    
                    # 발신자별 카운트
                    sender = payload.get('sender', 'unknown')
                    sender_counts[sender] = sender_counts.get(sender, 0) + 1
            
            print(f"   📊 타입별 분포:")
            for embed_type, count in type_counts.items():
                print(f"      - {embed_type}: {count}개")
            
            print(f"   🧵 스레드별 분포:")
            for thread_id, count in thread_counts.items():
                print(f"      - {thread_id}: {count}개")
            
            print(f"   👤 발신자별 분포:")
            for sender, count in sender_counts.items():
                print(f"      - {sender}: {count}개")
        
    except Exception as e:
        print(f"❌ Qdrant 데이터 읽기 실패: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(show_qdrant_data())
