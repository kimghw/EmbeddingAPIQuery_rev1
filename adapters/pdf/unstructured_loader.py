"""
Unstructured Document Loader Adapter
"""

import uuid
from typing import List, Dict, Any, Optional
from datetime import datetime
from pathlib import Path
from core.ports.document_loader import DocumentLoaderPort
from core.entities.document import Document


class UnstructuredLoaderAdapter(DocumentLoaderPort):
    """Unstructured 문서 로더 어댑터"""
    
    def __init__(self):
        self.supported_extensions = [
            '.pdf', '.docx', '.doc', '.pptx', '.ppt', '.xlsx', '.xls',
            '.txt', '.md', '.html', '.htm', '.xml', '.csv', '.tsv',
            '.rtf', '.odt', '.odp', '.ods', '.epub'
        ]
        self._check_unstructured_availability()
    
    def _check_unstructured_availability(self):
        """Unstructured 라이브러리 가용성 확인"""
        try:
            import unstructured
            self.unstructured_available = True
        except ImportError:
            self.unstructured_available = False
            print("⚠️  Unstructured 라이브러리가 설치되지 않았습니다.")
            print("   설치 명령: pip install unstructured[all-docs]")
    
    async def load_from_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """파일에서 문서 로드"""
        if not self.unstructured_available:
            raise RuntimeError("Unstructured 라이브러리가 설치되지 않았습니다. 'pip install unstructured[all-docs]'로 설치해주세요.")
        
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"지원하지 않는 파일 형식: {path.suffix}")
        
        try:
            # Unstructured로 문서 파싱
            elements = self._parse_with_unstructured(str(path))
            
            # 텍스트 추출
            content = self._extract_text_from_elements(elements)
            
            # 메타데이터 생성
            doc_metadata = self._extract_metadata_from_elements(elements, path)
            
            # 사용자 제공 메타데이터 병합
            if metadata:
                doc_metadata.update(metadata)
            
            # Document 생성
            document = Document.create(
                title=path.stem,
                content=content,
                metadata=doc_metadata,
                document_id=str(uuid.uuid4())
            )
            
            return document
            
        except Exception as e:
            raise RuntimeError(f"Unstructured 문서 로드 중 오류 발생: {e}")
    
    async def load_from_bytes(self, content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """바이트 데이터에서 문서 로드"""
        if not self.unstructured_available:
            raise RuntimeError("Unstructured 라이브러리가 설치되지 않았습니다.")
        
        try:
            # 임시 파일로 저장 후 처리
            import tempfile
            import os
            
            file_path = Path(filename)
            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"지원하지 않는 파일 형식: {file_path.suffix}")
            
            # 임시 파일 생성
            with tempfile.NamedTemporaryFile(delete=False, suffix=file_path.suffix) as temp_file:
                temp_file.write(content)
                temp_file_path = temp_file.name
            
            try:
                # Unstructured로 파싱
                elements = self._parse_with_unstructured(temp_file_path)
                
                # 텍스트 추출
                text_content = self._extract_text_from_elements(elements)
                
                # 메타데이터 생성
                doc_metadata = {
                    'filename': filename,
                    'file_size': len(content),
                    'file_extension': file_path.suffix,
                    'loader_type': 'unstructured',
                    'created_at': datetime.utcnow().isoformat(),
                    'source': 'bytes',
                    'total_elements': len(elements)
                }
                
                # 요소별 메타데이터 추가
                element_metadata = self._extract_element_metadata(elements)
                doc_metadata.update(element_metadata)
                
                # 사용자 제공 메타데이터 병합
                if metadata:
                    doc_metadata.update(metadata)
                
                # Document 생성
                document = Document.create(
                    title=file_path.stem,
                    content=text_content,
                    metadata=doc_metadata,
                    document_id=str(uuid.uuid4())
                )
                
                return document
                
            finally:
                # 임시 파일 삭제
                os.unlink(temp_file_path)
                
        except Exception as e:
            raise RuntimeError(f"바이트 데이터 로드 중 오류 발생: {e}")
    
    async def load_from_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """URL에서 문서 로드 (구현하지 않음)"""
        raise NotImplementedError("Unstructured 로더는 URL 로드를 지원하지 않습니다. 웹 스크래퍼를 사용해주세요.")
    
    async def load_multiple_files(self, file_paths: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """여러 문서 파일 로드"""
        documents = []
        
        for file_path in file_paths:
            try:
                document = await self.load_from_file(file_path, metadata)
                documents.append(document)
            except Exception as e:
                print(f"파일 로드 실패 ({file_path}): {e}")
                continue
        
        return documents
    
    def get_supported_formats(self) -> List[str]:
        """지원하는 파일 형식 반환"""
        return self.supported_extensions.copy()
    
    def is_format_supported(self, file_extension: str) -> bool:
        """파일 형식 지원 여부 확인"""
        return file_extension.lower() in self.supported_extensions
    
    def _parse_with_unstructured(self, file_path: str) -> List:
        """Unstructured로 문서 파싱"""
        try:
            from unstructured.partition.auto import partition
            
            # 파일 확장자에 따른 파싱
            elements = partition(
                filename=file_path,
                strategy="auto",  # 자동 전략 선택
                include_page_breaks=True,
                infer_table_structure=True,
                chunking_strategy="by_title",
                max_characters=4000,
                new_after_n_chars=3800,
                combine_text_under_n_chars=2000
            )
            
            return elements
            
        except ImportError as e:
            raise RuntimeError(f"Unstructured 라이브러리 import 실패: {e}")
        except Exception as e:
            # 기본 파싱으로 재시도
            try:
                from unstructured.partition.auto import partition
                elements = partition(filename=file_path)
                return elements
            except Exception as retry_e:
                raise RuntimeError(f"Unstructured 파싱 실패: {retry_e}")
    
    def _extract_text_from_elements(self, elements: List) -> str:
        """Unstructured 요소들에서 텍스트 추출"""
        text_parts = []
        
        for element in elements:
            # 요소 타입별 처리
            element_type = str(type(element).__name__)
            text = str(element).strip()
            
            if not text:
                continue
            
            # 제목 요소 처리
            if 'Title' in element_type:
                text_parts.append(f"\n# {text}\n")
            
            # 부제목 요소 처리
            elif 'Header' in element_type:
                text_parts.append(f"\n## {text}\n")
            
            # 리스트 요소 처리
            elif 'ListItem' in element_type:
                text_parts.append(f"• {text}")
            
            # 표 요소 처리
            elif 'Table' in element_type:
                text_parts.append(f"\n[표]\n{text}\n")
            
            # 일반 텍스트 요소
            else:
                text_parts.append(text)
        
        # 텍스트 결합 및 정리
        content = '\n\n'.join(text_parts)
        content = self._clean_text(content)
        
        return content
    
    def _extract_metadata_from_elements(self, elements: List, file_path: Path) -> Dict[str, Any]:
        """Unstructured 요소들에서 메타데이터 추출"""
        metadata = {
            'file_path': str(file_path.absolute()),
            'file_name': file_path.name,
            'file_size': file_path.stat().st_size,
            'file_extension': file_path.suffix,
            'loader_type': 'unstructured',
            'created_at': datetime.utcnow().isoformat(),
            'total_elements': len(elements)
        }
        
        # 요소별 메타데이터 추가
        element_metadata = self._extract_element_metadata(elements)
        metadata.update(element_metadata)
        
        return metadata
    
    def _extract_element_metadata(self, elements: List) -> Dict[str, Any]:
        """요소들에서 메타데이터 추출"""
        metadata = {}
        
        # 요소 타입별 통계
        element_types = {}
        page_numbers = set()
        
        for element in elements:
            element_type = str(type(element).__name__)
            element_types[element_type] = element_types.get(element_type, 0) + 1
            
            # 페이지 번호 추출 (가능한 경우)
            if hasattr(element, 'metadata') and element.metadata:
                if hasattr(element.metadata, 'page_number'):
                    page_numbers.add(element.metadata.page_number)
        
        metadata['element_types'] = element_types
        
        if page_numbers:
            metadata['total_pages'] = len(page_numbers)
            metadata['page_numbers'] = sorted(list(page_numbers))
        
        # 문서 구조 분석
        titles = [str(e) for e in elements if 'Title' in str(type(e).__name__)]
        if titles:
            metadata['titles'] = titles[:5]  # 처음 5개 제목만
            metadata['title_count'] = len(titles)
        
        # 텍스트 길이 통계
        text_lengths = [len(str(e)) for e in elements if str(e).strip()]
        if text_lengths:
            metadata['avg_element_length'] = sum(text_lengths) / len(text_lengths)
            metadata['max_element_length'] = max(text_lengths)
            metadata['min_element_length'] = min(text_lengths)
        
        return metadata
    
    def _clean_text(self, text: str) -> str:
        """텍스트 정리"""
        import re
        
        # 연속된 공백 제거
        text = re.sub(r' +', ' ', text)
        
        # 연속된 줄바꿈 제거 (최대 2개까지)
        text = re.sub(r'\n{3,}', '\n\n', text)
        
        # 탭 문자를 공백으로 변경
        text = text.replace('\t', ' ')
        
        # 앞뒤 공백 제거
        text = text.strip()
        
        return text
    
    # 기존 메서드들과의 호환성을 위한 별칭
    async def load_document(self, file_path: str) -> Document:
        """단일 문서 로드 (호환성)"""
        return await self.load_from_file(file_path)
    
    async def load_multiple_documents(self, file_paths: List[str]) -> List[Document]:
        """여러 문서 로드 (호환성)"""
        return await self.load_multiple_files(file_paths)
    
    def get_supported_extensions(self) -> List[str]:
        """지원하는 파일 확장자 반환 (호환성)"""
        return self.get_supported_formats()
    
    def get_loader_type(self) -> str:
        """로더 타입 반환 (호환성)"""
        return "unstructured"
    
    def get_loader_info(self) -> Dict[str, Any]:
        """로더 정보 반환 (호환성)"""
        return {
            "type": self.get_loader_type(),
            "supported_extensions": self.get_supported_formats(),
            "available": self.unstructured_available,
            "features": [
                "multi_format_support",
                "automatic_parsing",
                "structure_detection",
                "table_extraction",
                "metadata_extraction",
                "chunking_strategies",
                "page_break_detection"
            ],
            "description": "Unstructured 라이브러리를 사용한 다양한 문서 형식 지원",
            "supported_formats": {
                "documents": ["PDF", "DOCX", "DOC", "RTF", "ODT"],
                "presentations": ["PPTX", "PPT", "ODP"],
                "spreadsheets": ["XLSX", "XLS", "ODS", "CSV", "TSV"],
                "web": ["HTML", "HTM", "XML"],
                "text": ["TXT", "MD"],
                "ebooks": ["EPUB"]
            }
        }
    
    async def validate_file(self, file_path: str) -> bool:
        """파일 유효성 검사 (호환성)"""
        if not self.unstructured_available:
            return False
        
        try:
            path = Path(file_path)
            
            # 파일 존재 확인
            if not path.exists():
                return False
            
            # 확장자 확인
            if not self.is_format_supported(path.suffix):
                return False
            
            # 파일 크기 확인 (100MB 제한)
            if path.stat().st_size > 100 * 1024 * 1024:
                return False
            
            # Unstructured로 파싱 테스트 (첫 번째 요소만)
            try:
                from unstructured.partition.auto import partition
                elements = partition(filename=file_path, max_characters=1000)
                return len(elements) > 0
            except Exception:
                return False
                
        except Exception:
            return False
    
    def is_available(self) -> bool:
        """Unstructured 라이브러리 사용 가능 여부 (호환성)"""
        return self.unstructured_available
    
    def get_installation_guide(self) -> str:
        """설치 가이드 반환 (호환성)"""
        return """
Unstructured 라이브러리 설치 가이드:

1. 기본 설치:
   pip install unstructured

2. 모든 문서 형식 지원:
   pip install unstructured[all-docs]

3. 특정 형식만 지원:
   pip install unstructured[pdf]     # PDF만
   pip install unstructured[docx]    # Word 문서만
   pip install unstructured[pptx]    # PowerPoint만

4. 시스템 의존성 (Ubuntu/Debian):
   sudo apt-get install poppler-utils
   sudo apt-get install tesseract-ocr
   sudo apt-get install libreoffice

5. 시스템 의존성 (macOS):
   brew install poppler
   brew install tesseract
   brew install libreoffice
"""
