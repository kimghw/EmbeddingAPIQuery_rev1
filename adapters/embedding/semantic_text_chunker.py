"""
Semantic Text Chunker Adapter - 의미 기반 텍스트 청킹
"""

import re
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from core.ports.text_chunker import TextChunkerPort
from core.entities.document import Document, DocumentChunk


class SemanticTextChunkerAdapter(TextChunkerPort):
    """의미 기반 텍스트 청킹 어댑터"""
    
    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        min_chunk_size: int = 100,
        sentence_split_regex: str = r'[.!?]+\s+'
    ):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.min_chunk_size = min_chunk_size
        self.sentence_split_regex = sentence_split_regex
    
    async def chunk_document(self, document: Document) -> List[DocumentChunk]:
        """문서를 의미 기반으로 청킹"""
        return await self.chunk_text(
            text=document.content,
            document_id=document.id,
            metadata=document.metadata
        )
    
    async def chunk_text(
        self, 
        text: str, 
        document_id: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[DocumentChunk]:
        """텍스트를 의미 기반으로 청킹"""
        if not text.strip():
            return []
        
        # 1. 문장 단위로 분할
        sentences = self._split_into_sentences(text)
        
        # 2. 의미적 그룹화
        semantic_groups = self._group_sentences_semantically(sentences)
        
        # 3. 청크 크기에 맞게 조정
        chunks = self._create_chunks_from_groups(semantic_groups, document_id, metadata)
        
        return chunks
    
    async def chunk_multiple_documents(self, documents: List[Document]) -> Dict[str, List[DocumentChunk]]:
        """여러 문서를 의미 기반으로 청킹"""
        result = {}
        for document in documents:
            chunks = await self.chunk_document(document)
            result[document.id] = chunks
        return result
    
    def _split_into_sentences(self, text: str) -> List[str]:
        """텍스트를 문장 단위로 분할"""
        # 정규식으로 문장 분할
        sentences = re.split(self.sentence_split_regex, text)
        
        # 빈 문장 제거 및 정리
        sentences = [s.strip() for s in sentences if s.strip()]
        
        return sentences
    
    def _group_sentences_semantically(self, sentences: List[str]) -> List[List[str]]:
        """문장들을 의미적으로 그룹화"""
        if not sentences:
            return []
        
        groups = []
        current_group = []
        current_length = 0
        
        for sentence in sentences:
            sentence_length = len(sentence)
            
            # 현재 그룹에 추가할지 결정
            if self._should_add_to_current_group(
                current_group, current_length, sentence, sentence_length
            ):
                current_group.append(sentence)
                current_length += sentence_length
            else:
                # 현재 그룹을 완료하고 새 그룹 시작
                if current_group:
                    groups.append(current_group)
                current_group = [sentence]
                current_length = sentence_length
        
        # 마지막 그룹 추가
        if current_group:
            groups.append(current_group)
        
        return groups
    
    def _should_add_to_current_group(
        self, 
        current_group: List[str], 
        current_length: int, 
        sentence: str, 
        sentence_length: int
    ) -> bool:
        """현재 그룹에 문장을 추가할지 결정"""
        # 첫 번째 문장이면 추가
        if not current_group:
            return True
        
        # 청크 크기를 초과하면 새 그룹
        if current_length + sentence_length > self.chunk_size:
            return False
        
        # 의미적 연관성 검사 (간단한 휴리스틱)
        return self._check_semantic_similarity(current_group, sentence)
    
    def _check_semantic_similarity(self, current_group: List[str], sentence: str) -> bool:
        """의미적 유사성 검사 (간단한 구현)"""
        if not current_group:
            return True
        
        last_sentence = current_group[-1].lower()
        current_sentence = sentence.lower()
        
        # 1. 공통 키워드 검사
        last_words = set(re.findall(r'\b\w+\b', last_sentence))
        current_words = set(re.findall(r'\b\w+\b', current_sentence))
        
        # 불용어 제거 (간단한 버전)
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'this', 'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they'
        }
        
        last_words -= stop_words
        current_words -= stop_words
        
        if not last_words or not current_words:
            return True
        
        # 공통 단어 비율 계산
        common_words = last_words.intersection(current_words)
        similarity_ratio = len(common_words) / min(len(last_words), len(current_words))
        
        # 2. 문장 시작 패턴 검사
        sentence_starters = [
            'however', 'therefore', 'moreover', 'furthermore', 'additionally',
            'consequently', 'meanwhile', 'similarly', 'likewise', 'in contrast',
            'on the other hand', 'for example', 'for instance', 'in fact',
            'indeed', 'specifically', 'particularly'
        ]
        
        starts_with_connector = any(
            current_sentence.startswith(starter) for starter in sentence_starters
        )
        
        # 3. 주제 연속성 검사 (간단한 버전)
        # 숫자나 목록 패턴
        has_numbering = bool(re.match(r'^\d+\.', sentence.strip()))
        last_has_numbering = bool(re.match(r'^\d+\.', current_group[-1].strip()))
        
        # 결정 로직
        if starts_with_connector:
            return True
        if has_numbering and last_has_numbering:
            return True
        if similarity_ratio > 0.3:  # 30% 이상 공통 단어
            return True
        
        return similarity_ratio > 0.1  # 최소 10% 공통 단어
    
    def _create_chunks_from_groups(
        self, 
        groups: List[List[str]], 
        document_id: str, 
        metadata: Optional[Dict[str, Any]]
    ) -> List[DocumentChunk]:
        """의미적 그룹들로부터 청크 생성"""
        chunks = []
        
        for i, group in enumerate(groups):
            # 그룹의 문장들을 합치기
            content = ' '.join(group)
            
            # 너무 작은 청크는 다음 청크와 합치기
            if len(content) < self.min_chunk_size and i < len(groups) - 1:
                # 다음 그룹과 합치기
                next_group = groups[i + 1]
                combined_content = content + ' ' + ' '.join(next_group)
                
                if len(combined_content) <= self.chunk_size:
                    # 다음 그룹을 현재 그룹에 합치고 다음 그룹은 건너뛰기
                    content = combined_content
                    groups[i + 1] = []  # 다음 그룹을 비우기
            
            if not content.strip():
                continue
            
            # 청크 생성
            chunk_id = f"{document_id}_chunk_{len(chunks) + 1}_{uuid.uuid4().hex[:8]}"
            
            chunk_metadata = {
                'chunk_index': len(chunks),
                'chunk_type': 'semantic',
                'sentence_count': len(group),
                'semantic_group_id': i
            }
            
            if metadata:
                chunk_metadata.update(metadata)
            
            # DocumentChunk 생성 (올바른 파라미터 사용)
            chunk = DocumentChunk(
                id=chunk_id,
                document_id=document_id,
                content=content,
                chunk_index=len(chunks),
                start_char=0,  # 의미적 청킹에서는 정확한 인덱스 계산이 복잡
                end_char=len(content),
                metadata=chunk_metadata,
                created_at=datetime.utcnow()
            )
            
            chunks.append(chunk)
        
        # 오버랩 처리
        if self.chunk_overlap > 0:
            chunks = self._add_overlap_to_chunks(chunks)
        
        return chunks
    
    def _add_overlap_to_chunks(self, chunks: List[DocumentChunk]) -> List[DocumentChunk]:
        """청크들에 오버랩 추가"""
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            content = chunk.content
            
            # 이전 청크의 끝부분 추가
            if i > 0 and self.chunk_overlap > 0:
                prev_chunk = chunks[i - 1]
                prev_words = prev_chunk.content.split()
                
                # 오버랩할 단어 수 계산
                overlap_words = min(
                    len(prev_words),
                    self.chunk_overlap // 5  # 대략 단어당 5글자로 추정
                )
                
                if overlap_words > 0:
                    overlap_text = ' '.join(prev_words[-overlap_words:])
                    content = overlap_text + ' ' + content
            
            # 새로운 청크 생성 (올바른 파라미터 사용)
            new_chunk = DocumentChunk(
                id=chunk.id,
                document_id=chunk.document_id,
                content=content,
                chunk_index=chunk.chunk_index,
                start_char=chunk.start_char,
                end_char=chunk.end_char,
                metadata=chunk.metadata,
                created_at=chunk.created_at
            )
            
            overlapped_chunks.append(new_chunk)
        
        return overlapped_chunks
    
    def get_chunk_size(self) -> int:
        """청크 크기 반환"""
        return self.chunk_size
    
    def get_chunk_overlap(self) -> int:
        """청크 오버랩 반환"""
        return self.chunk_overlap
    
    def set_chunk_size(self, size: int) -> None:
        """청크 크기 설정"""
        self.chunk_size = max(size, self.min_chunk_size)
    
    def set_chunk_overlap(self, overlap: int) -> None:
        """청크 오버랩 설정"""
        self.chunk_overlap = max(0, overlap)
    
    def get_chunker_type(self) -> str:
        """청킹 타입 반환"""
        return "semantic"
    
    def get_chunker_info(self) -> Dict[str, Any]:
        """청킹 어댑터 정보 반환"""
        return {
            "type": self.get_chunker_type(),
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "min_chunk_size": self.min_chunk_size,
            "sentence_split_regex": self.sentence_split_regex,
            "features": [
                "semantic_grouping",
                "sentence_boundary_detection",
                "keyword_similarity",
                "connector_word_detection",
                "numbering_pattern_recognition"
            ]
        }
