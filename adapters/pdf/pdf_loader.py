"""
PDF document loader adapter implementation.
"""

import os
from typing import List, Optional, Dict, Any
from pathlib import Path
import asyncio
from datetime import datetime

try:
    import pypdf
    PYPDF_AVAILABLE = True
except ImportError:
    PYPDF_AVAILABLE = False

try:
    import fitz  # PyMuPDF
    PYMUPDF_AVAILABLE = True
except ImportError:
    PYMUPDF_AVAILABLE = False

from core.entities.document import Document
from core.ports.document_loader import DocumentLoaderPort


class PdfLoaderAdapter(DocumentLoaderPort):
    """PDF document loader adapter using PyPDF and PyMuPDF."""
    
    def __init__(self, preferred_library: str = "pypdf"):
        """
        Initialize PDF loader.
        
        Args:
            preferred_library: "pypdf" or "pymupdf"
        """
        self.preferred_library = preferred_library
        self._validate_dependencies()
    
    def _validate_dependencies(self):
        """Validate that required libraries are available."""
        if self.preferred_library == "pypdf" and not PYPDF_AVAILABLE:
            if PYMUPDF_AVAILABLE:
                self.preferred_library = "pymupdf"
            else:
                raise ImportError("Neither pypdf nor pymupdf is available")
        elif self.preferred_library == "pymupdf" and not PYMUPDF_AVAILABLE:
            if PYPDF_AVAILABLE:
                self.preferred_library = "pypdf"
            else:
                raise ImportError("Neither pypdf nor pymupdf is available")
    
    async def load_from_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """Load a PDF document from file path."""
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")
        
        file_path_obj = Path(file_path)
        if file_path_obj.suffix.lower() != '.pdf':
            raise ValueError(f"File is not a PDF: {file_path}")
        
        # Run PDF extraction in thread pool to avoid blocking
        content = await asyncio.get_event_loop().run_in_executor(
            None, self._extract_text_from_file, file_path
        )
        
        # Create document metadata
        doc_metadata = metadata or {}
        doc_metadata.update({
            "source": file_path,
            "file_name": file_path_obj.name,
            "file_size": file_path_obj.stat().st_size,
            "loader_type": "pdf",
            "library_used": self.preferred_library
        })
        
        return Document.create(
            title=file_path_obj.stem,
            content=content,
            metadata=doc_metadata
        )
    
    async def load_from_bytes(self, content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """Load a PDF document from bytes content."""
        if not filename.lower().endswith('.pdf'):
            raise ValueError(f"File is not a PDF: {filename}")
        
        # Run PDF extraction in thread pool to avoid blocking
        text_content = await asyncio.get_event_loop().run_in_executor(
            None, self._extract_text_from_bytes, content
        )
        
        # Create document metadata
        doc_metadata = metadata or {}
        doc_metadata.update({
            "source": "bytes",
            "file_name": filename,
            "file_size": len(content),
            "loader_type": "pdf",
            "library_used": self.preferred_library
        })
        
        return Document.create(
            title=Path(filename).stem,
            content=text_content,
            metadata=doc_metadata
        )
    
    async def load_from_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """Load a PDF document from URL."""
        import aiohttp
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if response.status != 200:
                    raise ValueError(f"Failed to download PDF from URL: {url}")
                
                content = await response.read()
                filename = url.split('/')[-1]
                if not filename.endswith('.pdf'):
                    filename += '.pdf'
                
                # Add URL to metadata
                url_metadata = metadata or {}
                url_metadata["source_url"] = url
                
                return await self.load_from_bytes(content, filename, url_metadata)
    
    async def load_multiple_files(self, file_paths: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """Load multiple PDF documents from file paths."""
        documents = []
        
        for file_path in file_paths:
            try:
                doc = await self.load_from_file(file_path, metadata)
                documents.append(doc)
            except Exception as e:
                # Log error but continue with other files
                print(f"Error loading {file_path}: {e}")
                continue
        
        return documents
    
    def get_supported_formats(self) -> List[str]:
        """Get list of supported file formats."""
        return [".pdf"]
    
    def is_format_supported(self, file_extension: str) -> bool:
        """Check if a file format is supported."""
        return file_extension.lower() in [".pdf"]
    
    def _extract_text_from_file(self, file_path: str) -> str:
        """Extract text from PDF file (synchronous)."""
        if self.preferred_library == "pypdf":
            return self._extract_with_pypdf_file(file_path)
        else:
            return self._extract_with_pymupdf_file(file_path)
    
    def _extract_text_from_bytes(self, content: bytes) -> str:
        """Extract text from PDF bytes (synchronous)."""
        if self.preferred_library == "pypdf":
            return self._extract_with_pypdf_bytes(content)
        else:
            return self._extract_with_pymupdf_bytes(content)
    
    def _extract_with_pypdf_file(self, file_path: str) -> str:
        """Extract text using PyPDF from file."""
        text_content = []
        
        with open(file_path, 'rb') as file:
            pdf_reader = pypdf.PdfReader(file)
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    page_text = page.extract_text()
                    if page_text.strip():
                        text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                except Exception as e:
                    print(f"Error extracting page {page_num + 1}: {e}")
                    continue
        
        return "\n\n".join(text_content)
    
    def _extract_with_pypdf_bytes(self, content: bytes) -> str:
        """Extract text using PyPDF from bytes."""
        import io
        
        text_content = []
        pdf_reader = pypdf.PdfReader(io.BytesIO(content))
        
        for page_num, page in enumerate(pdf_reader.pages):
            try:
                page_text = page.extract_text()
                if page_text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
            except Exception as e:
                print(f"Error extracting page {page_num + 1}: {e}")
                continue
        
        return "\n\n".join(text_content)
    
    def _extract_with_pymupdf_file(self, file_path: str) -> str:
        """Extract text using PyMuPDF from file."""
        text_content = []
        
        doc = fitz.open(file_path)
        
        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
            except Exception as e:
                print(f"Error extracting page {page_num + 1}: {e}")
                continue
        
        doc.close()
        return "\n\n".join(text_content)
    
    def _extract_with_pymupdf_bytes(self, content: bytes) -> str:
        """Extract text using PyMuPDF from bytes."""
        text_content = []
        
        doc = fitz.open(stream=content, filetype="pdf")
        
        for page_num in range(len(doc)):
            try:
                page = doc.load_page(page_num)
                page_text = page.get_text()
                if page_text.strip():
                    text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
            except Exception as e:
                print(f"Error extracting page {page_num + 1}: {e}")
                continue
        
        doc.close()
        return "\n\n".join(text_content)
