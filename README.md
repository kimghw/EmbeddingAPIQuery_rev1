# Document Embedding & Retrieval System

A clean architecture-based system for document processing, embedding generation, and semantic retrieval using FastAPI and CLI interfaces.

## 🏗️ Architecture

This project follows **Clean Architecture** principles with **Port/Adapter pattern**:

- **Core**: Business logic, entities, and use cases (no external dependencies)
- **Ports**: Interface definitions for external dependencies
- **Adapters**: Implementations of port interfaces
- **Interfaces**: Thin adapters for API and CLI entry points

## 📁 Project Structure

```
project/
├── core/
│   ├── entities/          # Domain entities (Document, Embedding, etc.)
│   ├── ports/            # Interface definitions
│   ├── usecases/         # Business logic
│   └── services/         # Domain services
├── adapters/
│   ├── db/               # Database adapters
│   ├── external_api/     # External API adapters
│   ├── pdf/              # PDF processing adapters
│   ├── embedding/        # Embedding model adapters
│   └── vector_store/     # Vector store adapters
├── interfaces/
│   ├── api/              # FastAPI routers
│   └── cli/              # CLI commands
├── schemas/              # Pydantic models
├── config/               # Configuration management
├── tests/                # Test modules
└── docs/                 # Documentation
```

## 🚀 Features

### Core Capabilities
- **Document Loading**: PDF, JSON, and web document processing
- **Text Chunking**: Semantic and character-based text splitting
- **Embedding Generation**: OpenAI and HuggingFace model support
- **Vector Storage**: Qdrant, FAISS, and ChromaDB integration
- **Semantic Retrieval**: Multi-vector and query-based search

### Interfaces
- **REST API**: FastAPI-based web interface
- **CLI**: Command-line interface for batch operations
- **Async Support**: Full asynchronous processing

## 🛠️ Technology Stack

- **Language**: Python 3.12+
- **Web Framework**: FastAPI
- **CLI**: Click
- **Data Models**: Pydantic
- **Document Processing**: PyPDF, PyMuPDF
- **Embeddings**: OpenAI API, LangChain
- **Vector Stores**: Qdrant, FAISS
- **Testing**: pytest, pytest-asyncio

## 📦 Installation

### 1. Clone and Setup Environment

```bash
git clone <repository-url>
cd EmbeddingAPIQuery_rev1

# Create virtual environment
python3 -m venv embedding_env
source embedding_env/bin/activate  # Linux/Mac
# or
embedding_env\Scripts\activate     # Windows
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Environment Configuration

```bash
cp .env.example .env
# Edit .env with your configuration
```

Required environment variables:
- `OPENAI_API_KEY`: Your OpenAI API key
- `QDRANT_URL`: Qdrant server URL (default: http://localhost:6333)

## 🚀 Usage

### API Server

```bash
# Start FastAPI server
python main.py

# Or with uvicorn directly
uvicorn main:app --host 0.0.0.0 --port 8000
```

Access the API documentation at: http://localhost:8000/docs

### CLI Commands

```bash
# Process a document
python main.py cli process-document --file-path /path/to/document.pdf

# Search documents
python main.py cli search --query "your search query" --top-k 5

# Get system stats
python main.py cli stats
```

## 🔧 Configuration

The system uses environment-based configuration with support for:
- Development, Production, and Test environments
- Port/Adapter pattern for configuration management
- Pydantic Settings for validation

Key configuration options:
- Embedding model selection
- Vector store configuration
- Chunk size and overlap settings
- API rate limiting

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=core --cov=adapters --cov=interfaces

# Run specific test categories
pytest tests/unit/
pytest tests/integration/
```

## 📚 API Documentation

### Document Processing Endpoints

- `POST /documents/upload` - Upload and process documents
- `GET /documents/{document_id}` - Get document information
- `DELETE /documents/{document_id}` - Delete document

### Search Endpoints

- `POST /search` - Search documents by text query
- `POST /search/vector` - Search by embedding vector
- `POST /search/similar/{document_id}` - Find similar documents

### System Endpoints

- `GET /health` - Health check
- `GET /stats` - System statistics

## 🏛️ Architecture Principles

### Clean Architecture Benefits
1. **Independence**: Core business logic independent of frameworks
2. **Testability**: Easy unit testing without external dependencies
3. **Flexibility**: Easy to swap implementations (e.g., vector stores)
4. **Maintainability**: Clear separation of concerns

### Port/Adapter Pattern
- **Ports**: Define what the application needs (interfaces)
- **Adapters**: Implement how external systems provide it
- **Dependency Inversion**: Core depends on abstractions, not concretions

## 🔄 Development Workflow

### Adding New Features
1. Define entities in `core/entities/`
2. Create port interfaces in `core/ports/`
3. Implement use cases in `core/usecases/`
4. Create adapters in `adapters/`
5. Add API/CLI interfaces
6. Write tests

### Extending Vector Stores
1. Implement `VectorStorePort` interface
2. Add adapter in `adapters/vector_store/`
3. Update configuration
4. Add tests

## 🤝 Contributing

1. Follow clean architecture principles
2. Maintain port/adapter separation
3. Write comprehensive tests
4. Update documentation
5. Follow Python coding standards (Black, isort, flake8)

## 📄 License

[Add your license information here]

## 🆘 Support

For issues and questions:
1. Check the documentation
2. Review existing issues
3. Create a new issue with detailed information

---

**Built with Clean Architecture principles for maintainable, testable, and scalable document processing.**
