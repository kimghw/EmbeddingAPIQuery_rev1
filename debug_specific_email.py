"""
Debug specific email embeddings
"""

import asyncio
from config.adapter_factory import get_vector_store

async def debug_specific_email():
    """Debug specific email embeddings"""
    email_id = "bb9a9349-fb23-4810-b04a-35b61d795d8a"
    print(f"🔍 이메일 ID {email_id}의 임베딩 확인 중...")
    
    vector_store = get_vector_store()
    collection_name = "emails"
    
    try:
        # Get embeddings for this specific email
        embeddings = await vector_store.get_embeddings_by_document(email_id, collection_name)
        print(f"✅ 찾은 임베딩 수: {len(embeddings)}")
        
        for i, embedding in enumerate(embeddings):
            print(f"\n--- 임베딩 {i+1} ---")
            print(f"ID: {embedding.id}")
            print(f"메타데이터: {embedding.metadata}")
            
            # Check if it's subject or body
            if embedding.id.endswith('_subject'):
                print("📧 타입: Subject")
            elif embedding.id.endswith('_body'):
                print("📧 타입: Body")
            else:
                print("❓ 타입: Unknown")
        
        # Also get all embeddings and filter manually
        print(f"\n🔍 전체 임베딩에서 {email_id} 검색:")
        all_embeddings = await vector_store.get_all_embeddings(collection_name, limit=100)
        
        matching_embeddings = []
        for embedding in all_embeddings:
            if embedding.metadata.get('email_id') == email_id:
                matching_embeddings.append(embedding)
        
        print(f"✅ 매칭된 임베딩 수: {len(matching_embeddings)}")
        for embedding in matching_embeddings:
            print(f"  - ID: {embedding.id}")
            print(f"    Content: {embedding.metadata.get('content', 'N/A')[:100]}...")
        
    except Exception as e:
        print(f"❌ 오류: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(debug_specific_email())
