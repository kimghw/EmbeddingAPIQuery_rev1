#!/usr/bin/env python3
"""
Debug email list API with detailed information.
"""

import requests
import json
import asyncio
from config.adapter_factory import create_adapter_factory
from core.usecases.email_retrieval import EmailRetrievalUseCase

async def debug_direct_retrieval():
    """Test direct retrieval without API."""
    print("\n🔍 DIRECT RETRIEVAL TEST")
    print("=" * 50)
    
    try:
        # Create adapter factory
        factory = create_adapter_factory()
        
        # Get vector store
        vector_store = factory.get_vector_store()
        
        # Create retrieval use case
        retrieval_use_case = EmailRetrievalUseCase(
            vector_store=vector_store,
            embedding_model=factory.get_embedding_model()
        )
        
        # Get emails directly
        result = await retrieval_use_case.list_emails(
            page=1,
            page_size=10
        )
        
        print(f"Success: {result['success']}")
        print(f"Total emails: {result.get('total', 0)}")
        print(f"Number of emails returned: {len(result.get('emails', []))}")
        
        if result.get('emails'):
            print("\nFirst email:")
            email = result['emails'][0]
            print(f"  ID: {email.get('id')}")
            print(f"  Subject: {email.get('subject')}")
            print(f"  Sender: {email.get('sender')}")
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

def debug_api():
    """Test API endpoint."""
    print("\n🔍 API ENDPOINT TEST")
    print("=" * 50)
    
    base_url = "http://localhost:8000"
    
    # Test list endpoint
    print("\n1. List Emails API:")
    try:
        response = requests.get(f"{base_url}/emails/list")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test stats endpoint
    print("\n2. Email Stats API:")
    try:
        response = requests.get(f"{base_url}/emails/stats")
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            print(f"   Response: {json.dumps(data, indent=2)}")
        else:
            print(f"   Error: {response.text}")
            
    except Exception as e:
        print(f"   ❌ Error: {e}")

async def main():
    # Test direct retrieval first
    await debug_direct_retrieval()
    
    # Then test API
    debug_api()

if __name__ == "__main__":
    asyncio.run(main())
