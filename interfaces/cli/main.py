"""
CLI interface for Document Embedding & Retrieval System.
"""

import click
import asyncio
import json
from pathlib import Path
from typing import Optional

from config.settings import config
from adapters.pdf.pdf_loader import PdfLoaderAdapter
from adapters.embedding.text_chunker import RecursiveTextChunkerAdapter
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter
from core.usecases.document_processing import DocumentProcessingUseCase


@click.group()
def cli():
    """Document Embedding & Retrieval System CLI."""
    pass


@cli.command()
@click.option('--file-path', required=True, help='Path to the PDF file to process')
@click.option('--output', default=None, help='Output file for results (JSON)')
def process_document(file_path: str, output: Optional[str]):
    """Process a single document: load, chunk, and embed."""
    
    async def _process():
        try:
            # Initialize adapters
            pdf_loader = PdfLoaderAdapter()
            text_chunker = RecursiveTextChunkerAdapter(
                chunk_size=config.get_chunk_size(),
                chunk_overlap=config.get_chunk_overlap()
            )
            embedding_model = OpenAIEmbeddingAdapter(config)
            
            # For now, we'll just process without vector store
            # Create a mock vector store for testing
            from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
            vector_store = MockVectorStoreAdapter()
            
            # Create use case
            use_case = DocumentProcessingUseCase(
                document_loader=pdf_loader,
                text_chunker=text_chunker,
                embedding_model=embedding_model,
                vector_store=vector_store,
                config=config
            )
            
            click.echo(f"Processing document: {file_path}")
            
            # Process document
            result = await use_case.process_document_from_file(file_path)
            
            if result["success"]:
                click.echo(f"✅ Document processed successfully!")
                click.echo(f"   Document ID: {result['document_id']}")
                click.echo(f"   Title: {result['document_title']}")
                click.echo(f"   Chunks: {result['chunks_count']}")
                click.echo(f"   Embeddings: {result['embeddings_count']}")
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
def config_info():
    """Show current configuration."""
    click.echo("Current Configuration:")
    click.echo(f"  App Name: {config.get_app_name()}")
    click.echo(f"  App Version: {config.get_app_version()}")
    click.echo(f"  Debug: {config.get_debug()}")
    click.echo(f"  OpenAI API Key: {'***' + config.get_openai_api_key()[-4:] if config.get_openai_api_key() else 'Not set'}")
    click.echo(f"  Embedding Model: {config.get_embedding_model()}")
    click.echo(f"  Vector Dimension: {config.get_vector_dimension()}")
    click.echo(f"  Chunk Size: {config.get_chunk_size()}")
    click.echo(f"  Chunk Overlap: {config.get_chunk_overlap()}")
    click.echo(f"  Collection Name: {config.get_collection_name()}")


if __name__ == '__main__':
    cli()
