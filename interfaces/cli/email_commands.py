"""
CLI commands for email processing functionality.
"""

import asyncio
import json
import click
from typing import Dict, Any
from pathlib import Path

from adapters.email.json_email_loader import JsonEmailLoaderAdapter
from core.usecases.email_processing import EmailProcessingUseCase
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from config.adapter_factory import AdapterFactory


class MockEmbeddingModel:
    """Mock embedding model for CLI testing."""
    
    def __init__(self):
        self.model_name = "mock-embedding-model"
        self.dimension = 1536
        self.max_input_length = 8191
    
    async def embed_texts(self, texts):
        import random
        embeddings = []
        for text in texts:
            random.seed(hash(text) % 2**32)
            embedding = [random.uniform(-1, 1) for _ in range(self.dimension)]
            embeddings.append(embedding)
        return embeddings
    
    def get_model_name(self) -> str:
        return self.model_name
    
    def get_dimension(self) -> int:
        return self.dimension
    
    def get_max_input_length(self) -> int:
        return self.max_input_length


class MockConfig:
    """Mock configuration for CLI."""
    
    def get_openai_api_key(self) -> str:
        return "mock-api-key"
    
    def get_qdrant_url(self) -> str:
        return "http://localhost:6333"
    
    def get_qdrant_api_key(self) -> str:
        return "mock-qdrant-key"


@click.group()
def email():
    """Email processing commands."""
    pass


@email.command()
@click.option('--json-file', '-f', required=True, help='Path to JSON file containing emails')
@click.option('--output', '-o', default='json', type=click.Choice(['json', 'summary']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def process_json(json_file: str, output: str, verbose: bool):
    """Process emails from JSON file."""
    
    async def _process():
        try:
            # Load JSON file
            json_path = Path(json_file)
            if not json_path.exists():
                click.echo(f"❌ Error: File {json_file} not found", err=True)
                return False
            
            with open(json_path, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Initialize components
            email_loader = JsonEmailLoaderAdapter()
            embedding_model = MockEmbeddingModel()
            vector_store = MockVectorStoreAdapter()
            config = MockConfig()
            
            # Create use case
            email_processor = EmailProcessingUseCase(
                email_loader=email_loader,
                embedding_model=embedding_model,
                vector_store=vector_store,
                config=config
            )
            
            if verbose:
                click.echo(f"📧 Processing emails from {json_file}...")
            
            # Process emails
            result = await email_processor.process_emails_from_json(json_data)
            
            if not result['success']:
                click.echo(f"❌ Error: {result.get('error', 'Unknown error')}", err=True)
                return False
            
            # Output results
            if output == 'json':
                click.echo(json.dumps(result, indent=2, ensure_ascii=False))
            else:  # summary
                click.echo(f"✅ Successfully processed {result['processed_count']} emails")
                click.echo(f"🔢 Generated {result['embedded_count']} embeddings")
                click.echo(f"📁 Collection: {result['collection_name']}")
                
                if verbose:
                    stats = result['statistics']
                    click.echo(f"\n📈 Statistics:")
                    click.echo(f"  Email counts: {stats['email_counts']}")
                    click.echo(f"  Embedding counts: {stats['embedding_counts']}")
                    click.echo(f"  Content stats: {stats['content_statistics']}")
                    
                    click.echo(f"\n📧 Processed emails:")
                    for i, email_info in enumerate(result['emails'], 1):
                        click.echo(f"  {i}. {email_info['subject'][:60]}...")
                        click.echo(f"     From: {email_info['sender']}")
                        click.echo(f"     Thread: {email_info['correspondence_thread']}")
            
            return True
            
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    success = asyncio.run(_process())
    if not success:
        exit(1)


@email.command()
@click.option('--json-file', '-f', required=True, help='Path to JSON file to validate')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def validate(json_file: str, verbose: bool):
    """Validate JSON file structure for email processing."""
    
    try:
        # Load JSON file
        json_path = Path(json_file)
        if not json_path.exists():
            click.echo(f"❌ Error: File {json_file} not found", err=True)
            exit(1)
        
        with open(json_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
        
        # Initialize loader
        email_loader = JsonEmailLoaderAdapter()
        
        # Validate structure
        is_valid = email_loader.validate_json_structure(json_data)
        
        if is_valid:
            click.echo(f"✅ JSON file {json_file} is valid")
            
            if verbose:
                # Get statistics
                stats = email_loader.get_statistics(json_data)
                click.echo(f"\n📊 File Statistics:")
                click.echo(f"  Total emails: {stats.get('total_emails', 0)}")
                click.echo(f"  User ID: {stats.get('user_id', 'unknown')}")
                click.echo(f"  OData context: {stats.get('odata_context', 'unknown')}")
                
                if 'sender_distribution' in stats:
                    click.echo(f"  Top senders: {list(stats['sender_distribution'].keys())[:5]}")
                
                if 'thread_distribution' in stats:
                    click.echo(f"  Threads: {list(stats['thread_distribution'].keys())[:5]}")
        else:
            click.echo(f"❌ JSON file {json_file} is not valid", err=True)
            exit(1)
            
    except json.JSONDecodeError as e:
        click.echo(f"❌ Error: Invalid JSON format - {str(e)}", err=True)
        exit(1)
    except Exception as e:
        click.echo(f"❌ Error: {str(e)}", err=True)
        if verbose:
            import traceback
            traceback.print_exc()
        exit(1)


@email.command()
@click.option('--output', '-o', default='sample_emails.json', help='Output file path')
def create_sample(output: str):
    """Create a sample email JSON file for testing."""
    
    sample_data = {
        "@odata.context": "https://graph.microsoft.com/v1.0/$metadata#users('sample-user')/messages",
        "value": [
            {
                "id": "sample-email-1",
                "createdDateTime": "2025-05-29T10:00:00Z",
                "subject": "Sample Email - Test Subject",
                "bodyPreview": "This is a sample email for testing purposes...",
                "importance": "normal",
                "hasAttachments": False,
                "isRead": False,
                "sender": {
                    "emailAddress": {
                        "name": "Sample Sender",
                        "address": "sender@example.com"
                    }
                },
                "toRecipients": [
                    {
                        "emailAddress": {
                            "name": "Sample Recipient",
                            "address": "recipient@example.com"
                        }
                    }
                ],
                "ccRecipients": [],
                "bccRecipients": [],
                "body": {
                    "contentType": "text",
                    "content": "This is a sample email content for testing the email processing system. It contains some text that can be used to test the embedding and vector storage functionality."
                },
                "webLink": "https://outlook.office365.com/owa/sample-link",
                "conversationId": "sample-conversation-1"
            }
        ]
    }
    
    try:
        with open(output, 'w', encoding='utf-8') as f:
            json.dump(sample_data, f, indent=2, ensure_ascii=False)
        
        click.echo(f"✅ Sample email JSON created: {output}")
        click.echo(f"📧 Contains {len(sample_data['value'])} sample email(s)")
        
    except Exception as e:
        click.echo(f"❌ Error creating sample file: {str(e)}", err=True)
        exit(1)


@email.command()
def stats():
    """Get email processing statistics."""
    
    async def _get_stats():
        try:
            # Initialize components
            email_loader = JsonEmailLoaderAdapter()
            embedding_model = MockEmbeddingModel()
            vector_store = MockVectorStoreAdapter()
            config = MockConfig()
            
            # Create use case
            email_processor = EmailProcessingUseCase(
                email_loader=email_loader,
                embedding_model=embedding_model,
                vector_store=vector_store,
                config=config
            )
            
            # Get statistics
            stats = await email_processor.get_processing_stats()
            
            if stats['success']:
                click.echo(f"📊 Email Processing Statistics:")
                click.echo(f"  Collection exists: {stats['collection_exists']}")
                click.echo(f"  Total embeddings: {stats['total_embeddings']}")
                click.echo(f"  Estimated emails: {stats['estimated_email_count']}")
                click.echo(f"  Collection name: {stats['collection_name']}")
                click.echo(f"  Embedding model: {stats['embedding_model']}")
                click.echo(f"  Vector dimension: {stats['vector_dimension']}")
                click.echo(f"  Loader type: {stats['loader_type']}")
                
                if 'collection_info' in stats:
                    info = stats['collection_info']
                    click.echo(f"  Store type: {info.get('store_type', 'unknown')}")
            else:
                click.echo(f"❌ Error getting statistics: {stats.get('error', 'Unknown error')}", err=True)
                return False
            
            return True
            
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            return False
    
    success = asyncio.run(_get_stats())
    if not success:
        exit(1)


@email.command()
@click.option('--webhook-data', '-d', required=True, help='JSON string or file path containing webhook data')
@click.option('--output', '-o', default='json', type=click.Choice(['json', 'summary']), help='Output format')
@click.option('--verbose', '-v', is_flag=True, help='Verbose output')
def process_webhook(webhook_data: str, output: str, verbose: bool):
    """Process emails from webhook data."""
    
    async def _process():
        try:
            # Parse webhook data
            if webhook_data.startswith('{'):
                # JSON string
                data = json.loads(webhook_data)
            else:
                # File path
                webhook_path = Path(webhook_data)
                if not webhook_path.exists():
                    click.echo(f"❌ Error: File {webhook_data} not found", err=True)
                    return False
                
                with open(webhook_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
            
            # Initialize components
            email_loader = JsonEmailLoaderAdapter()
            embedding_model = MockEmbeddingModel()
            vector_store = MockVectorStoreAdapter()
            config = MockConfig()
            
            # Create use case
            email_processor = EmailProcessingUseCase(
                email_loader=email_loader,
                embedding_model=embedding_model,
                vector_store=vector_store,
                config=config
            )
            
            if verbose:
                click.echo(f"📧 Processing webhook data...")
            
            # Process webhook
            result = await email_processor.process_emails_from_webhook(data)
            
            if not result['success']:
                click.echo(f"❌ Error: {result.get('error', 'Unknown error')}", err=True)
                return False
            
            # Output results
            if output == 'json':
                click.echo(json.dumps(result, indent=2, ensure_ascii=False))
            else:  # summary
                click.echo(f"✅ Successfully processed {result['processed_count']} emails from webhook")
                click.echo(f"🔢 Generated {result['embedded_count']} embeddings")
                click.echo(f"🔗 Webhook type: {result.get('webhook_type', 'unknown')}")
                
                if verbose and result['emails']:
                    click.echo(f"\n📧 Processed emails:")
                    for i, email_info in enumerate(result['emails'], 1):
                        click.echo(f"  {i}. {email_info['subject'][:60]}...")
                        click.echo(f"     From: {email_info['sender']}")
                        click.echo(f"     Thread: {email_info['correspondence_thread']}")
            
            return True
            
        except json.JSONDecodeError as e:
            click.echo(f"❌ Error: Invalid JSON format - {str(e)}", err=True)
            return False
        except Exception as e:
            click.echo(f"❌ Error: {str(e)}", err=True)
            if verbose:
                import traceback
                traceback.print_exc()
            return False
    
    success = asyncio.run(_process())
    if not success:
        exit(1)


if __name__ == '__main__':
    email()
