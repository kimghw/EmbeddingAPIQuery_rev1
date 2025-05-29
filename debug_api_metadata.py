"""
Debug API metadata issue
"""
import asyncio
from config.adapter_factory import get_vector_store_adapter
from config.settings import Settings

async def debug_api_metadata():
    """Debug what metadata is actually returned from vector store."""
    print("🔍 API 메타데이터 디버깅...")
    
    # Get vector store
    config = Settings()
    vector_store = get_vector_store_adapter(config)
    collection_name = "emails"
    
    # Get all embeddings
    all_embeddings = await vector_store.get_all_embeddings(collection_name, limit=10)
    
    print(f"📊 총 {len(all_embeddings)} 개 임베딩 발견")
    
    for i, embedding in enumerate(all_embeddings):
        print(f"\n📧 임베딩 {i+1}:")
        print(f"   ID: {embedding.id}")
        print(f"   Document ID: {embedding.document_id}")
        print(f"   Chunk ID: {embedding.chunk_id}")
        print(f"   메타데이터 키들: {list(embedding.metadata.keys())}")
        
        # Check specific fields
        email_id = embedding.metadata.get('email_id')
        subject = embedding.metadata.get('subject')
        sender_address = embedding.metadata.get('sender_address')
        correspondence_thread = embedding.metadata.get('correspondence_thread')
        
        print(f"   email_id: {email_id}")
        print(f"   subject: {subject}")
        print(f"   sender_address: {sender_address}")
        print(f"   correspondence_thread: {correspondence_thread}")
        
        # Check if it's a subject embedding
        is_subject = embedding.id.endswith('_subject')
        print(f"   is_subject: {is_subject}")
        
        if is_subject:
            print(f"   ✅ 이것은 subject 임베딩입니다")
            print(f"   📋 전체 메타데이터:")
            for key, value in embedding.metadata.items():
                print(f"      {key}: {value}")

if __name__ == "__main__":
    asyncio.run(debug_api_metadata())
