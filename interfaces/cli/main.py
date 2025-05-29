"""
CLI interface for Document Embedding & Retrieval System.
"""

import click
import asyncio
import json
from pathlib import Path
from typing import Optional

from config.settings import config
from config.adapter_factory import AdapterFactory
from core.usecases.document_processing import DocumentProcessingUseCase
from core.usecases.document_retrieval import DocumentRetrievalUseCase
from interfaces.cli.email_commands import email


@click.group()
def cli():
    """Document Embedding & Retrieval System CLI."""
    pass


# Add email commands group
cli.add_command(email)


@cli.command()
@click.option('--file-path', required=True, help='Path to the PDF file to process')
@click.option('--output', default=None, help='Output file for results (JSON)')
@click.option('--chunker', type=click.Choice(['recursive', 'semantic']), default='semantic', help='Text chunker type')
@click.option('--embedding', type=click.Choice(['openai', 'huggingface']), default='openai', help='Embedding model type')
@click.option('--vector-store', type=click.Choice(['qdrant', 'faiss', 'mock']), default='qdrant', help='Vector store type')
@click.option('--loader', type=click.Choice(['pdf', 'json', 'web', 'unstructured']), default='pdf', help='Document loader type')
def process_document(file_path: str, output: Optional[str], chunker: str, embedding: str, vector_store: str, loader: str):
    """Process a single document: load, chunk, and embed."""
    
    async def _process():
        try:
            # Initialize adapter factory
            factory = AdapterFactory()
            
            click.echo(f"🔧 Initializing adapters...")
            click.echo(f"   Loader: {loader}")
            click.echo(f"   Chunker: {chunker}")
            click.echo(f"   Embedding: {embedding}")
            click.echo(f"   Vector Store: {vector_store}")
            
            # Create adapters using factory
            document_loader = factory.create_document_loader_adapter(loader)
            text_chunker = factory.create_text_chunker_adapter(
                chunker, 
                chunk_size=config.get_chunk_size(),
                chunk_overlap=config.get_chunk_overlap(),
                config=config
            )
            embedding_model = factory.create_embedding_adapter(embedding, config)
            vector_store_adapter = factory.create_vector_store_adapter(vector_store)
            
            # Health check for external services
            if vector_store in ['qdrant']:
                is_healthy = await vector_store_adapter.health_check()
                if not is_healthy:
                    click.echo(f"❌ {vector_store.title()} is not accessible. Make sure the server is running.")
                    if vector_store == 'qdrant':
                        click.echo("   docker run -p 6333:6333 qdrant/qdrant")
                    click.echo("   Or use --vector-store mock for testing")
                    return
            
            # Create use case
            use_case = DocumentProcessingUseCase(
                document_loader=document_loader,
                text_chunker=text_chunker,
                embedding_model=embedding_model,
                vector_store=vector_store_adapter,
                config=config
            )
            
            click.echo(f"\n📄 Processing document: {file_path}")
            
            # Process document
            result = await use_case.process_document_from_file(file_path)
            
            if result["success"]:
                click.echo(f"✅ Document processed successfully!")
                click.echo(f"   Document ID: {result['document_id']}")
                click.echo(f"   Title: {result['document_title']}")
                click.echo(f"   Chunks: {result['chunks_count']}")
                click.echo(f"   Embeddings: {result['embeddings_count']}")
                click.echo(f"   Collection: {result.get('collection_name', 'N/A')}")
            else:
                click.echo(f"❌ Error processing document: {result['error']}")
                return
            
            # Save results if output specified
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"Results saved to: {output}")
            
        except Exception as e:
            click.echo(f"❌ Unexpected error: {str(e)}")
    
    # Run async function
    asyncio.run(_process())


@cli.command()
@click.option('--query', required=True, help='Search query text')
@click.option('--top-k', default=5, help='Number of results to return')
@click.option('--output', default=None, help='Output file for results (JSON)')
@click.option('--embedding', type=click.Choice(['openai', 'huggingface']), default='openai', help='Embedding model type')
@click.option('--vector-store', type=click.Choice(['qdrant', 'faiss', 'mock']), default='qdrant', help='Vector store type')
@click.option('--retriever', type=click.Choice(['simple', 'ensemble']), default='simple', help='Retriever type')
def search_documents(query: str, top_k: int, output: Optional[str], embedding: str, vector_store: str, retriever: str):
    """Search for documents using text query."""
    
    async def _search():
        try:
            # Initialize adapter factory
            factory = AdapterFactory()
            
            click.echo(f"🔧 Initializing search components...")
            click.echo(f"   Embedding: {embedding}")
            click.echo(f"   Vector Store: {vector_store}")
            click.echo(f"   Retriever: {retriever}")
            
            # Create adapters using factory
            embedding_model = factory.create_embedding_adapter(embedding, config)
            vector_store_adapter = factory.create_vector_store_adapter(vector_store)
            retriever_adapter = factory.create_retriever_adapter(
                retriever, 
                vector_store=vector_store_adapter, 
                embedding_model=embedding_model,
                config=config
            )
            
            # Health check for external services
            if vector_store in ['qdrant']:
                is_healthy = await vector_store_adapter.health_check()
                if not is_healthy:
                    click.echo(f"❌ {vector_store.title()} is not accessible. Make sure the server is running.")
                    return
            
            # Create retrieval use case
            retrieval_use_case = DocumentRetrievalUseCase(
                retriever=retriever_adapter,
                embedding_model=embedding_model,
                vector_store=vector_store_adapter,
                config=config
            )
            
            click.echo(f"\n🔍 Searching for: '{query}'")
            click.echo(f"   Top-K results: {top_k}")
            
            # Search documents
            result = await retrieval_use_case.search_documents(
                query_text=query,
                top_k=top_k
            )
            
            if result.success:
                results = result.results
                click.echo(f"✅ Found {len(results)} relevant documents")
                click.echo(f"   Query ID: {result.query_id}")
                click.echo(f"   Collection: {result.collection_name}")
                click.echo(f"   Retriever: {result.retriever_type}")
                
                for i, doc_result in enumerate(results, 1):
                    click.echo(f"\n   Result {i}:")
                    click.echo(f"     Score: {doc_result.score:.4f}")
                    click.echo(f"     Rank: {doc_result.rank}")
                    click.echo(f"     Document ID: {doc_result.document_id}")
                    click.echo(f"     Chunk ID: {doc_result.chunk_id}")
                    
                    # Show content preview
                    content = doc_result.content
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"     Content: {content_preview}")
                    
                    if doc_result.metadata:
                        click.echo(f"     Metadata: {doc_result.metadata}")
            else:
                click.echo(f"❌ Search failed: {getattr(result, 'error', 'Unknown error')}")
                return
            
            # Save results if output specified
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"Results saved to: {output}")
            
        except Exception as e:
            click.echo(f"❌ Unexpected error: {str(e)}")
    
    # Run async function
    asyncio.run(_search())


@cli.command()
@click.option('--document-id', required=True, help='Document ID to find similar documents')
@click.option('--top-k', default=5, help='Number of results to return')
@click.option('--output', default=None, help='Output file for results (JSON)')
def search_similar(document_id: str, top_k: int, output: Optional[str]):
    """Find documents similar to a given document."""
    
    async def _search():
        try:
            # Initialize adapters
            embedding_model = OpenAIEmbeddingAdapter(config)
            vector_store = QdrantVectorStoreAdapter(
                host="localhost",
                port=6333,
                vector_dimension=config.get_vector_dimension()
            )
            
            # Check Qdrant health
            is_healthy = await vector_store.health_check()
            if not is_healthy:
                click.echo("❌ Qdrant is not accessible. Make sure Qdrant server is running:")
                click.echo("   docker run -p 6333:6333 qdrant/qdrant")
                return
            
            # Initialize retriever
            retriever = SimpleRetrieverAdapter(
                vector_store=vector_store,
                embedding_model=embedding_model
            )
            
            # Create retrieval use case
            retrieval_use_case = DocumentRetrievalUseCase(
                retriever=retriever,
                embedding_model=embedding_model,
                vector_store=vector_store,
                config=config
            )
            
            click.echo(f"Finding documents similar to: {document_id}")
            click.echo(f"Top-K results: {top_k}")
            
            # Search similar documents
            result = await retrieval_use_case.search_similar_documents(
                document_id=document_id,
                top_k=top_k
            )
            
            if result["success"]:
                results = result["results"]
                click.echo(f"✅ Found {len(results)} similar documents")
                click.echo(f"   Reference Document: {result['reference_document_id']}")
                click.echo(f"   Collection: {result['collection_name']}")
                click.echo(f"   Retriever: {result['retriever_type']}")
                
                for i, doc_result in enumerate(results, 1):
                    click.echo(f"\n   Result {i}:")
                    click.echo(f"     Score: {doc_result['score']:.4f}")
                    click.echo(f"     Rank: {doc_result['rank']}")
                    click.echo(f"     Document ID: {doc_result['document_id']}")
                    click.echo(f"     Chunk ID: {doc_result['chunk_id']}")
                    
                    # Show content preview
                    content = doc_result['content']
                    content_preview = content[:200] + "..." if len(content) > 200 else content
                    click.echo(f"     Content: {content_preview}")
                    
                    if doc_result['metadata']:
                        click.echo(f"     Metadata: {doc_result['metadata']}")
            else:
                click.echo(f"❌ Search failed: {result['error']}")
                return
            
            # Save results if output specified
            if output:
                with open(output, 'w') as f:
                    json.dump(result, f, indent=2, default=str)
                click.echo(f"Results saved to: {output}")
            
        except Exception as e:
            click.echo(f"❌ Unexpected error: {str(e)}")
    
    # Run async function
    asyncio.run(_search())


@cli.command()
def collection_stats():
    """Show collection statistics."""
    
    async def _stats():
        try:
            # Initialize adapters
            embedding_model = OpenAIEmbeddingAdapter(config)
            vector_store = QdrantVectorStoreAdapter(
                host="localhost",
                port=6333,
                vector_dimension=config.get_vector_dimension()
            )
            
            # Check Qdrant health
            is_healthy = await vector_store.health_check()
            if not is_healthy:
                click.echo("❌ Qdrant is not accessible. Make sure Qdrant server is running:")
                click.echo("   docker run -p 6333:6333 qdrant/qdrant")
                return
            
            # Initialize retriever
            retriever = SimpleRetrieverAdapter(
                vector_store=vector_store,
                embedding_model=embedding_model
            )
            
            # Create retrieval use case
            retrieval_use_case = DocumentRetrievalUseCase(
                retriever=retriever,
                embedding_model=embedding_model,
                vector_store=vector_store,
                config=config
            )
            
            click.echo("Collection Statistics:")
            
            # Get retrieval stats
            result = await retrieval_use_case.get_retrieval_stats()
            
            if result["success"]:
                click.echo(f"✅ Collection exists: {result['collection_exists']}")
                
                if result['collection_exists']:
                    click.echo(f"   Collection name: {result['collection_name']}")
                    click.echo(f"   Total embeddings: {result['total_embeddings']}")
                    click.echo(f"   Embedding model: {result['embedding_model']}")
                    click.echo(f"   Vector dimension: {result['vector_dimension']}")
                    click.echo(f"   Retriever type: {result['retriever_type']}")
                    
                    if 'collection_info' in result:
                        info = result['collection_info']
                        click.echo(f"   Collection status: {info.get('status', 'N/A')}")
                        click.echo(f"   Points count: {info.get('points_count', 0)}")
                    
                    if 'retriever_info' in result:
                        ret_info = result['retriever_info']
                        click.echo(f"   Retriever capabilities: {ret_info.get('capabilities', [])}")
                else:
                    click.echo(f"   Collection '{result['collection_name']}' does not exist")
            else:
                click.echo(f"❌ Failed to get stats: {result['error']}")
            
        except Exception as e:
            click.echo(f"❌ Unexpected error: {str(e)}")
    
    # Run async function
    asyncio.run(_stats())


@cli.command()
def test_embedding():
    """Test OpenAI embedding functionality."""
    
    async def _test():
        try:
            click.echo("Testing OpenAI embedding...")
            
            # Initialize embedding model
            embedding_model = OpenAIEmbeddingAdapter(config)
            
            # Test simple text embedding
            test_text = "This is a test sentence for embedding."
            click.echo(f"Test text: {test_text}")
            
            vector = await embedding_model.embed_text(test_text)
            
            click.echo(f"✅ Embedding generated successfully!")
            click.echo(f"   Model: {embedding_model.get_model_name()}")
            click.echo(f"   Dimension: {len(vector)}")
            click.echo(f"   First 5 values: {vector[:5]}")
            
            # Test model info
            model_info = await embedding_model.get_model_info()
            click.echo(f"   Model available: {model_info['available']}")
            
        except Exception as e:
            click.echo(f"❌ Error testing embedding: {str(e)}")
    
    # Run async function
    asyncio.run(_test())


@cli.command()
@click.option('--file-path', required=True, help='Path to the PDF file to test')
def test_pdf_loader(file_path: str):
    """Test PDF loading functionality."""
    
    async def _test():
        try:
            click.echo(f"Testing PDF loader with: {file_path}")
            
            # Check if file exists
            if not Path(file_path).exists():
                click.echo(f"❌ File not found: {file_path}")
                return
            
            # Initialize PDF loader
            pdf_loader = PdfLoaderAdapter()
            
            # Load document
            document = await pdf_loader.load_from_file(file_path)
            
            click.echo(f"✅ PDF loaded successfully!")
            click.echo(f"   Document ID: {document.id}")
            click.echo(f"   Title: {document.title}")
            click.echo(f"   Content length: {len(document.content)} characters")
            click.echo(f"   Metadata: {document.metadata}")
            
            # Show first 200 characters of content
            preview = document.content[:200] + "..." if len(document.content) > 200 else document.content
            click.echo(f"   Content preview: {preview}")
            
        except Exception as e:
            click.echo(f"❌ Error testing PDF loader: {str(e)}")
    
    # Run async function
    asyncio.run(_test())


@cli.command()
def test_chunker():
    """Test text chunking functionality."""
    
    async def _test():
        try:
            click.echo("Testing text chunker...")
            
            # Sample text
            sample_text = """
            This is the first paragraph of our test document. It contains some information about testing.
            
            This is the second paragraph. It has different content and should be processed separately.
            
            Here's a third paragraph with more content to test the chunking functionality. We want to make sure that the chunker works properly with different types of text and can handle various scenarios.
            
            Finally, this is the last paragraph of our sample document. It should be chunked appropriately based on our configuration.
            """
            
            # Initialize chunker
            chunker = RecursiveTextChunkerAdapter(
                chunk_size=200,  # Small size for testing
                chunk_overlap=50
            )
            
            # Create chunks
            chunks = await chunker.chunk_text(sample_text, "test-doc-id")
            
            click.echo(f"✅ Text chunked successfully!")
            click.echo(f"   Chunker type: {chunker.get_chunker_type()}")
            click.echo(f"   Chunk size: {chunker.get_chunk_size()}")
            click.echo(f"   Chunk overlap: {chunker.get_chunk_overlap()}")
            click.echo(f"   Number of chunks: {len(chunks)}")
            
            for i, chunk in enumerate(chunks):
                click.echo(f"\n   Chunk {i + 1}:")
                click.echo(f"     ID: {chunk.id}")
                click.echo(f"     Length: {chunk.get_length()}")
                click.echo(f"     Range: {chunk.get_char_range()}")
                preview = chunk.content[:100] + "..." if len(chunk.content) > 100 else chunk.content
                click.echo(f"     Content: {preview}")
            
        except Exception as e:
            click.echo(f"❌ Error testing chunker: {str(e)}")
    
    # Run async function
    asyncio.run(_test())


@cli.command()
def test_qdrant():
    """Test Qdrant vector store functionality."""
    
    async def _test():
        try:
            click.echo("Testing Qdrant vector store...")
            
            # Import Qdrant adapter and entities
            from core.entities.document import Embedding
            import uuid
            
            # Initialize Qdrant adapter
            qdrant = QdrantVectorStoreAdapter(
                host="localhost",
                port=6333,
                vector_dimension=config.get_vector_dimension()
            )
            
            collection_name = config.get_collection_name()
            
            # Test health check
            click.echo("Checking Qdrant health...")
            is_healthy = await qdrant.health_check()
            
            if not is_healthy:
                click.echo("❌ Qdrant is not accessible. Make sure Qdrant server is running.")
                click.echo("   You can start Qdrant with: docker run -p 6333:6333 qdrant/qdrant")
                return
            
            click.echo("✅ Qdrant is healthy!")
            
            # List collections
            collections = await qdrant.list_collections()
            click.echo(f"   Available collections: {collections}")
            
            # Check if collection exists, create if not
            exists = await qdrant.collection_exists(collection_name)
            if not exists:
                click.echo(f"Creating collection: {collection_name}")
                await qdrant.create_collection(collection_name, config.get_vector_dimension())
            
            # Get collection info
            collection_info = await qdrant.get_collection_info(collection_name)
            if collection_info:
                click.echo(f"   Collection: {collection_name}")
                click.echo(f"   Vector dimension: {collection_info.get('vector_dimension', 'N/A')}")
                click.echo(f"   Points count: {collection_info.get('points_count', 0)}")
                click.echo(f"   Status: {collection_info.get('status', 'N/A')}")
            
            # Test storing and searching vectors
            click.echo("\nTesting vector storage and search...")
            
            # Create test embeddings
            test_embeddings = [
                Embedding(
                    id=str(uuid.uuid4()),
                    document_id="test-doc-1",
                    chunk_id="chunk-0",
                    vector=[0.1] * config.get_vector_dimension(),
                    metadata={"source": "test", "category": "AI"}
                ),
                Embedding(
                    id=str(uuid.uuid4()),
                    document_id="test-doc-1",
                    chunk_id="chunk-1",
                    vector=[0.2] * config.get_vector_dimension(),
                    metadata={"source": "test", "category": "Programming"}
                )
            ]
            
            # Store embeddings
            success = await qdrant.add_embeddings(test_embeddings, collection_name)
            if success:
                click.echo(f"✅ Stored {len(test_embeddings)} test embeddings")
            else:
                click.echo("❌ Failed to store embeddings")
                return
            
            # Search for similar vectors
            query_vector = [0.15] * config.get_vector_dimension()  # Mock query vector
            search_results = await qdrant.search_similar(
                query_vector, 
                collection_name, 
                top_k=2
            )
            
            click.echo(f"✅ Found {len(search_results)} similar vectors")
            for i, result in enumerate(search_results):
                click.echo(f"   Result {i + 1}:")
                click.echo(f"     Score: {result.score:.4f}")
                click.echo(f"     Document ID: {result.embedding.document_id}")
                click.echo(f"     Chunk ID: {result.embedding.chunk_id}")
                click.echo(f"     Metadata: {result.metadata}")
            
            # Count embeddings
            count = await qdrant.count_embeddings(collection_name)
            click.echo(f"   Total embeddings in collection: {count}")
            
            # Clean up test data
            for embedding in test_embeddings:
                await qdrant.delete_embedding(embedding.id, collection_name)
            click.echo("✅ Cleaned up test data")
            
        except Exception as e:
            click.echo(f"❌ Error testing Qdrant: {str(e)}")
            if "Connection refused" in str(e) or "ConnectError" in str(e):
                click.echo("   Make sure Qdrant server is running:")
                click.echo("   docker run -p 6333:6333 qdrant/qdrant")
    
    # Run async function
    asyncio.run(_test())


@cli.command()
def config_info():
    """Show current configuration."""
    click.echo("Current Configuration:")
    click.echo(f"  App Name: {config.get_app_name()}")
    click.echo(f"  App Version: {config.get_app_version()}")
    click.echo(f"  Debug: {config.get_debug()}")
    click.echo(f"  OpenAI API Key: {'***' + config.get_openai_api_key()[-4:] if config.get_openai_api_key() else 'Not set'}")
    click.echo(f"  Qdrant URL: {config.get_qdrant_url()}")
    click.echo(f"  Embedding Model: {config.get_embedding_model()}")
    click.echo(f"  Vector Dimension: {config.get_vector_dimension()}")
    click.echo(f"  Chunk Size: {config.get_chunk_size()}")
    click.echo(f"  Chunk Overlap: {config.get_chunk_overlap()}")
    click.echo(f"  Collection Name: {config.get_collection_name()}")


if __name__ == '__main__':
    cli()
