"""
Debug script to check actual email data structure in Qdrant
"""

import asyncio
from config.adapter_factory import get_vector_store

async def debug_email_data():
    """Check actual email data structure in Qdrant"""
    print("🔍 Qdrant 이메일 데이터 구조 확인 중...")
    
    # Get vector store
    vector_store = get_vector_store()
    collection_name = "emails"
    
    try:
        # Check if collection exists
        exists = await vector_store.collection_exists(collection_name)
        print(f"✅ 컬렉션 존재 여부: {exists}")
        
        if not exists:
            print("❌ emails 컬렉션이 존재하지 않습니다.")
            return
        
        # Get all embeddings
        print("\n📊 모든 임베딩 조회 중...")
        all_embeddings = await vector_store.get_all_embeddings(collection_name, limit=100)
        print(f"✅ 총 임베딩 수: {len(all_embeddings)}")
        
        if not all_embeddings:
            print("❌ 임베딩이 없습니다.")
            return
        
        # Analyze first few embeddings
        print("\n🔍 첫 3개 임베딩 분석:")
        for i, embedding in enumerate(all_embeddings[:3]):
            print(f"\n--- 임베딩 {i+1} ---")
            print(f"ID: {embedding.id}")
            print(f"메타데이터 키들: {list(embedding.metadata.keys())}")
            
            # Print key metadata fields
            for key in ['email_id', 'embedding_type', 'content', 'sender_name', 'created_time']:
                value = embedding.metadata.get(key, 'N/A')
                if key == 'content' and len(str(value)) > 100:
                    value = str(value)[:100] + "..."
                print(f"  {key}: {value}")
        
        # Check embedding types
        print("\n📋 임베딩 타입별 분석:")
        type_counts = {}
        email_ids = set()
        
        for embedding in all_embeddings:
            embedding_type = embedding.metadata.get('embedding_type', 'unknown')
            email_id = embedding.metadata.get('email_id', 'unknown')
            
            type_counts[embedding_type] = type_counts.get(embedding_type, 0) + 1
            if email_id != 'unknown':
                email_ids.add(email_id)
        
        for embedding_type, count in type_counts.items():
            print(f"  {embedding_type}: {count}개")
        
        print(f"\n📧 고유 이메일 ID 수: {len(email_ids)}")
        print(f"📧 이메일 ID 목록: {list(email_ids)[:5]}{'...' if len(email_ids) > 5 else ''}")
        
    except Exception as e:
        print(f"❌ 오류 발생: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_email_data())
