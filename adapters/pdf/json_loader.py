"""
JSON Document Loader Adapter
"""

import json
import uuid
from typing import List, Dict, Any, Optional, Union
from datetime import datetime
from pathlib import Path
from core.ports.document_loader import DocumentLoaderPort
from core.entities.document import Document


class JsonLoaderAdapter(DocumentLoaderPort):
    """JSON 문서 로더 어댑터"""
    
    def __init__(self):
        self.supported_extensions = ['.json', '.jsonl']
    
    async def load_from_file(self, file_path: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """파일에서 JSON 문서 로드"""
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {file_path}")
        
        if path.suffix.lower() not in self.supported_extensions:
            raise ValueError(f"지원하지 않는 파일 형식: {path.suffix}")
        
        try:
            with open(path, 'r', encoding='utf-8') as file:
                if path.suffix.lower() == '.jsonl':
                    # JSONL 파일 처리 (각 줄이 JSON 객체)
                    content = self._load_jsonl(file)
                else:
                    # 일반 JSON 파일 처리
                    content = self._load_json(file)
            
            # 메타데이터 생성
            doc_metadata = {
                'file_path': str(path.absolute()),
                'file_name': path.name,
                'file_size': path.stat().st_size,
                'file_extension': path.suffix,
                'loader_type': 'json',
                'created_at': datetime.utcnow().isoformat()
            }
            
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
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        except Exception as e:
            raise RuntimeError(f"JSON 파일 로드 중 오류 발생: {e}")
    
    async def load_from_bytes(self, content: bytes, filename: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """바이트 데이터에서 JSON 문서 로드"""
        try:
            # 바이트를 문자열로 변환
            text_content = content.decode('utf-8')
            
            # 파일명에서 확장자 확인
            file_path = Path(filename)
            if file_path.suffix.lower() not in self.supported_extensions:
                raise ValueError(f"지원하지 않는 파일 형식: {file_path.suffix}")
            
            # JSON 파싱
            if file_path.suffix.lower() == '.jsonl':
                # JSONL 처리
                lines = text_content.strip().split('\n')
                parsed_content = []
                for line in lines:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            parsed_content.append(self._json_to_text(data))
                        except json.JSONDecodeError:
                            continue
                content_text = '\n\n'.join(parsed_content)
            else:
                # 일반 JSON 처리
                data = json.loads(text_content)
                content_text = self._json_to_text(data)
            
            # 메타데이터 생성
            doc_metadata = {
                'filename': filename,
                'file_size': len(content),
                'file_extension': file_path.suffix,
                'loader_type': 'json',
                'created_at': datetime.utcnow().isoformat(),
                'source': 'bytes'
            }
            
            # 사용자 제공 메타데이터 병합
            if metadata:
                doc_metadata.update(metadata)
            
            # Document 생성
            document = Document.create(
                title=file_path.stem,
                content=content_text,
                metadata=doc_metadata,
                document_id=str(uuid.uuid4())
            )
            
            return document
            
        except json.JSONDecodeError as e:
            raise ValueError(f"JSON 파싱 오류: {e}")
        except UnicodeDecodeError as e:
            raise ValueError(f"텍스트 디코딩 오류: {e}")
        except Exception as e:
            raise RuntimeError(f"바이트 데이터 로드 중 오류 발생: {e}")
    
    async def load_from_url(self, url: str, metadata: Optional[Dict[str, Any]] = None) -> Document:
        """URL에서 JSON 문서 로드 (구현하지 않음)"""
        raise NotImplementedError("JSON 로더는 URL 로드를 지원하지 않습니다. 웹 스크래퍼를 사용해주세요.")
    
    async def load_multiple_files(self, file_paths: List[str], metadata: Optional[Dict[str, Any]] = None) -> List[Document]:
        """여러 JSON 파일 로드"""
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
    
    def _load_json(self, file) -> str:
        """일반 JSON 파일 로드"""
        data = json.load(file)
        return self._json_to_text(data)
    
    def _load_jsonl(self, file) -> str:
        """JSONL 파일 로드 (각 줄이 JSON 객체)"""
        lines = []
        for line in file:
            line = line.strip()
            if line:
                try:
                    data = json.loads(line)
                    lines.append(self._json_to_text(data))
                except json.JSONDecodeError:
                    continue
        
        return '\n\n'.join(lines)
    
    def _json_to_text(self, data: Union[Dict, List, str, int, float, bool, None]) -> str:
        """JSON 데이터를 텍스트로 변환"""
        if isinstance(data, dict):
            return self._dict_to_text(data)
        elif isinstance(data, list):
            return self._list_to_text(data)
        elif isinstance(data, str):
            return data
        elif data is None:
            return ""
        else:
            return str(data)
    
    def _dict_to_text(self, data: Dict[str, Any]) -> str:
        """딕셔너리를 텍스트로 변환"""
        text_parts = []
        
        for key, value in data.items():
            if isinstance(value, (dict, list)):
                # 중첩된 구조는 재귀적으로 처리
                nested_text = self._json_to_text(value)
                if nested_text.strip():
                    text_parts.append(f"{key}: {nested_text}")
            elif isinstance(value, str) and value.strip():
                text_parts.append(f"{key}: {value}")
            elif value is not None:
                text_parts.append(f"{key}: {str(value)}")
        
        return '\n'.join(text_parts)
    
    def _list_to_text(self, data: List[Any]) -> str:
        """리스트를 텍스트로 변환"""
        text_parts = []
        
        for i, item in enumerate(data):
            if isinstance(item, (dict, list)):
                nested_text = self._json_to_text(item)
                if nested_text.strip():
                    text_parts.append(f"Item {i+1}: {nested_text}")
            elif isinstance(item, str) and item.strip():
                text_parts.append(item)
            elif item is not None:
                text_parts.append(str(item))
        
        return '\n'.join(text_parts)
    
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
        return "json"
    
    async def validate_file(self, file_path: str) -> bool:
        """파일 유효성 검사 (호환성)"""
        try:
            path = Path(file_path)
            
            # 파일 존재 확인
            if not path.exists():
                return False
            
            # 확장자 확인
            if not self.is_format_supported(path.suffix):
                return False
            
            # JSON 파싱 테스트
            with open(path, 'r', encoding='utf-8') as file:
                if path.suffix.lower() == '.jsonl':
                    # JSONL 첫 줄만 테스트
                    first_line = file.readline().strip()
                    if first_line:
                        json.loads(first_line)
                else:
                    # JSON 파일 전체 테스트
                    json.load(file)
            
            return True
            
        except Exception:
            return False
