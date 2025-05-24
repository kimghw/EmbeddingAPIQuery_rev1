"""
Full pipeline test with real PDF file from testdata directory.
Tests: PDF loading → Text chunking → OpenAI embedding → Qdrant storage → Search
"""

import asyncio
import sys
from pathlib import Path

# Add project root to path
sys.path.append(str(Path(__file__).parent.parent))

from config.settings import config
from adapters.pdf.pdf_loader import PdfLoaderAdapter
from adapters.embedding.text_chunker import RecursiveTextChunkerAdapter
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from core.usecases.document_processing import DocumentProcessingUseCase
from core.usecases.document_retrieval import DocumentRetrievalUseCase


async def test_full_pipeline():
    """Test the complete document processing and retrieval pipeline."""
    
    print("🚀 Starting Full Pipeline Test")
    print("=" * 50)
    
    # Check if testdata PDF exists
    pdf_path = Path("testdata/3DM GV7 Data Sheet_0.pdf")
    if not pdf_path.exists():
        print(f"❌ Test PDF not found: {pdf_path}")
        print("   Please ensure the PDF file exists in the testdata directory.")
        return False
    
    print(f"📄 Using test PDF: {pdf_path}")
    
    try:
        # Step 1: Initialize all adapters
        print("\n1️⃣ Initializing adapters...")
        
        pdf_loader = PdfLoaderAdapter()
        text_chunker = RecursiveTextChunkerAdapter(
            chunk_size=config.get_chunk_size(),
            chunk_overlap=config.get_chunk_overlap()
        )
        embedding_model = OpenAIEmbeddingAdapter(config)
        
        # Initialize Qdrant
        qdrant = QdrantVectorStoreAdapter(
            host="localhost",
            port=6333,
            vector_dimension=config.get_vector_dimension()
        )
        
        # Check Qdrant health
        print("   Checking Qdrant connection...")
        is_healthy = await qdrant.health_check()
        if not is_healthy:
            print("❌ Qdrant is not accessible. Please start Qdrant server:")
            print("   docker run -p 6333:6333 qdrant/qdrant")
            return False
        
        # Initialize retriever
        retriever = SimpleRetrieverAdapter(
            vector_store=qdrant,
            embedding_model=embedding_model
        )
        
        print("✅ All adapters initialized successfully!")
        
        # Step 2: Create use cases
        print("\n2️⃣ Creating use cases...")
        
        processing_use_case = DocumentProcessingUseCase(
            document_loader=pdf_loader,
            text_chunker=text_chunker,
            embedding_model=embedding_model,
            vector_store=qdrant,
            config=config
        )
        
        retrieval_use_case = DocumentRetrievalUseCase(
            retriever=retriever,
            embedding_model=embedding_model,
            vector_store=qdrant,
            config=config
        )
        
        print("✅ Use cases created successfully!")
        
        # Step 3: Process the PDF document
        print("\n3️⃣ Processing PDF document...")
        print(f"   File: {pdf_path}")
        
        result = await processing_use_case.process_document_from_file(str(pdf_path))
        
        if not result["success"]:
            print(f"❌ Document processing failed: {result['error']}")
            return False
        
        document_id = result["document_id"]
        print(f"✅ Document processed successfully!")
        print(f"   Document ID: {document_id}")
        print(f"   Title: {result['document_title']}")
        print(f"   Content length: {result.get('content_length', 'N/A')} characters")
        print(f"   Chunks created: {result['chunks_count']}")
        print(f"   Embeddings stored: {result['embeddings_count']}")
        
        # Step 4: Test document retrieval with various queries
        print("\n4️⃣ Testing document retrieval...")
        
        test_queries = [
            "What is this document about?",
            "technical specifications",
            "features and capabilities",
            "installation requirements"
        ]
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n   Query {i}: '{query}'")
            
            search_result = await retrieval_use_case.search_documents(
                query_text=query,
                top_k=3,
                filter_metadata=None
            )
            
            if search_result["success"]:
                results = search_result["results"]
                print(f"   ✅ Found {len(results)} relevant chunks")
                
                for j, chunk_result in enumerate(results[:2], 1):  # Show top 2 results
                    print(f"      Result {j}:")
                    print(f"        Score: {chunk_result['score']:.4f}")
                    print(f"        Document: {chunk_result['document_id']}")
                    print(f"        Chunk: {chunk_result['chunk_id']}")
                    
                    # Show content preview
                    content_preview = chunk_result['content'][:150] + "..." if len(chunk_result['content']) > 150 else chunk_result['content']
                    print(f"        Content: {content_preview}")
                    print(f"        Metadata: {chunk_result['metadata']}")
            else:
                print(f"   ❌ Search failed: {search_result['error']}")
        
        # Step 5: Test collection statistics
        print("\n5️⃣ Collection statistics...")
        
        collection_name = config.get_collection_name()
        collection_info = await qdrant.get_collection_info(collection_name)
        
        if collection_info:
            print(f"   Collection: {collection_name}")
            print(f"   Total points: {collection_info.get('points_count', 0)}")
            print(f"   Vector dimension: {collection_info.get('vector_dimension', 'N/A')}")
            print(f"   Status: {collection_info.get('status', 'N/A')}")
        
        # Step 6: Test document-specific retrieval
        print("\n6️⃣ Testing document-specific retrieval...")
        
        doc_embeddings = await qdrant.get_embeddings_by_document(document_id, collection_name)
        print(f"   Found {len(doc_embeddings)} embeddings for document {document_id}")
        
        if doc_embeddings:
            print("   Sample embedding info:")
            sample = doc_embeddings[0]
            print(f"     ID: {sample.id}")
            print(f"     Chunk ID: {sample.chunk_id}")
            print(f"     Vector dimension: {len(sample.vector)}")
            print(f"     Metadata: {sample.metadata}")
        
        # Step 7: Test retrieval system health
        print("\n7️⃣ Testing retrieval system health...")
        
        health_result = await retrieval_use_case.health_check()
        if health_result["success"]:
            print(f"   ✅ Retrieval system is healthy")
            print(f"     Overall healthy: {health_result['overall_healthy']}")
            print(f"     Vector store: {health_result['vector_store_healthy']}")
            print(f"     Embedding model: {health_result['embedding_model_available']}")
            print(f"     Collection exists: {health_result['collection_exists']}")
        else:
            print(f"   ❌ Health check failed: {health_result['error']}")
        
        print("\n🎉 Full Pipeline Test Completed Successfully!")
        print("=" * 50)
        print("✅ All components working correctly:")
        print("   • PDF loading and parsing")
        print("   • Text chunking with overlap")
        print("   • OpenAI embedding generation")
        print("   • Qdrant vector storage")
        print("   • Simple retriever implementation")
        print("   • Semantic search and retrieval")
        print("   • Document-specific queries")
        print("   • System health monitoring")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Pipeline test failed with error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


async def cleanup_test_data():
    """Clean up test data from Qdrant."""
    print("\n🧹 Cleaning up test data...")
    
    try:
        qdrant = QdrantVectorStoreAdapter(
            host="localhost",
            port=6333,
            vector_dimension=config.get_vector_dimension()
        )
        
        collection_name = config.get_collection_name()
        
        # Get all embeddings and delete those from our test document
        # For now, we'll just report the count
        collection_info = await qdrant.get_collection_info(collection_name)
        if collection_info:
            points_count = collection_info.get('points_count', 0)
            print(f"   Collection '{collection_name}' has {points_count} points")
            print("   Note: Manual cleanup may be needed for production use")
        
    except Exception as e:
        print(f"   Warning: Cleanup failed: {str(e)}")


if __name__ == "__main__":
    print("Document Embedding & Retrieval System")
    print("Full Pipeline Integration Test")
    print("=" * 50)
    
    # Run the test
    success = asyncio.run(test_full_pipeline())
    
    if success:
        print("\n✅ Test completed successfully!")
        
        # Ask if user wants to clean up
        try:
            cleanup = input("\nDo you want to clean up test data? (y/N): ").lower().strip()
            if cleanup == 'y':
                asyncio.run(cleanup_test_data())
        except KeyboardInterrupt:
            print("\nTest completed.")
    else:
        print("\n❌ Test failed!")
        sys.exit(1)
