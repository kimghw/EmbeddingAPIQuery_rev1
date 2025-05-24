"""
FAISS Vector Store Adapter - 완전한 구현
"""

import asyncio
import faiss
import numpy as np
import pickle
import os
from typing import List, Optional, Dict, Any
from core.ports.vector_store import VectorStorePort
from core.entities.document import DocumentChunk, RetrievalResult, Embedding


class FaissVectorStoreAdapter(VectorStorePort):
    """FAISS를 사용한 벡터 저장소 어댑터"""
    
    def __init__(self, storage_path: str = "./faiss_storage"):
        self.storage_path = storage_path
        self.collections = {}  # collection_name -> index 매핑
        self.metadata_storage = {}  # collection_name -> metadata 매핑
        self.id_mappings = {}  # collection_name -> id 매핑
        
        # 저장소 디렉토리 생성
        os.makedirs(storage_path, exist_ok=True)
    
    async def create_collection(self, collection_name: str, vector_dimension: int) -> bool:
        """컬렉션(인덱스) 생성"""
        try:
            # HNSW 인덱스 생성 (Qdrant와 유사한 성능)
            index = faiss.IndexHNSWFlat(vector_dimension, 32)
            index.hnsw.efConstruction = 200
            index.hnsw.efSearch = 50
            
            self.collections[collection_name] = {
                'index': index,
                'dimension': vector_dimension,
                'next_id': 0
            }
            self.metadata_storage[collection_name] = {}
            self.id_mappings[collection_name] = {}
            
            return True
        except Exception as e:
            print(f"FAISS 인덱스 생성 실패: {e}")
            return False
    
    async def collection_exists(self, collection_name: str) -> bool:
        """컬렉션 존재 여부 확인"""
        return collection_name in self.collections
    
    async def delete_collection(self, collection_name: str) -> bool:
        """컬렉션 삭제"""
        try:
            if collection_name in self.collections:
                del self.collections[collection_name]
                del self.metadata_storage[collection_name]
                del self.id_mappings[collection_name]
            return True
        except Exception as e:
            print(f"FAISS 컬렉션 삭제 실패: {e}")
            return False
    
    async def list_collections(self) -> List[str]:
        """컬렉션 목록 조회"""
        return list(self.collections.keys())
    
    async def get_collection_info(self, collection_name: str) -> Optional[Dict[str, Any]]:
        """컬렉션 정보 조회"""
        if collection_name not in self.collections:
            return None
        
        collection = self.collections[collection_name]
        return {
            "name": collection_name,
            "vectors_count": collection['index'].ntotal,
            "dimension": collection['dimension'],
            "index_type": "HNSW",
            "status": "ready"
        }
    
    async def store_chunks(self, chunks: List[DocumentChunk], collection_name: str) -> bool:
        """청크들을 FAISS 인덱스에 저장"""
        try:
            if collection_name not in self.collections:
                return False
            
            collection = self.collections[collection_name]
            index = collection['index']
            
            vectors = []
            for chunk in chunks:
                if chunk.embedding:
                    vectors.append(chunk.embedding)
                    
                    # 메타데이터 저장
                    chunk_id = chunk.chunk_id
                    self.metadata_storage[collection_name][chunk_id] = {
                        'document_id': chunk.document_id,
                        'content': chunk.content,
                        'metadata': chunk.metadata
                    }
                    self.id_mappings[collection_name][collection['next_id']] = chunk_id
                    collection['next_id'] += 1
            
            if vectors:
                vectors_array = np.array(vectors, dtype=np.float32)
                index.add(vectors_array)
                return True
            return False
            
        except Exception as e:
            print(f"FAISS 저장 실패: {e}")
            return False
    
    async def search_similar(
        self, 
        query_vector: List[float], 
        collection_name: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """유사한 벡터 검색"""
        try:
            if collection_name not in self.collections:
                return []
            
            collection = self.collections[collection_name]
            index = collection['index']
            
            if index.ntotal == 0:
                return []
            
            query_array = np.array([query_vector], dtype=np.float32)
            
            # FAISS 검색 (거리 기반)
            distances, indices = index.search(query_array, top_k)
            
            results = []
            for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
                if idx == -1:  # 유효하지 않은 인덱스
                    continue
                
                # 거리를 유사도 점수로 변환 (0~1 범위)
                similarity_score = 1.0 / (1.0 + distance)
                
                if score_threshold and similarity_score < score_threshold:
                    continue
                
                chunk_id = self.id_mappings[collection_name].get(idx)
                if chunk_id and chunk_id in self.metadata_storage[collection_name]:
                    metadata = self.metadata_storage[collection_name][chunk_id]
                    
                    # 메타데이터 필터링 (간단한 구현)
                    if filter_metadata:
                        skip = False
                        for key, value in filter_metadata.items():
                            if key not in metadata['metadata'] or metadata['metadata'][key] != value:
                                skip = True
                                break
                        if skip:
                            continue
                    
                    result = RetrievalResult(
                        chunk_id=chunk_id,
                        document_id=metadata['document_id'],
                        content=metadata['content'],
                        score=similarity_score,
                        rank=i + 1,
                        metadata=metadata['metadata']
                    )
                    results.append(result)
            
            return results
            
        except Exception as e:
            print(f"FAISS 검색 실패: {e}")
            return []
    
    async def add_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """단일 임베딩 추가"""
        try:
            if collection_name not in self.collections:
                return False
            
            collection = self.collections[collection_name]
            index = collection['index']
            
            vector_array = np.array([embedding.vector], dtype=np.float32)
            index.add(vector_array)
            
            # 메타데이터 저장
            self.metadata_storage[collection_name][embedding.id] = {
                'document_id': embedding.document_id,
                'chunk_id': embedding.chunk_id,
                'metadata': embedding.metadata
            }
            self.id_mappings[collection_name][collection['next_id']] = embedding.id
            collection['next_id'] += 1
            
            return True
        except Exception as e:
            print(f"FAISS 임베딩 추가 실패: {e}")
            return False
    
    async def add_embeddings(self, embeddings: List[Embedding], collection_name: str) -> bool:
        """다중 임베딩 추가"""
        try:
            if collection_name not in self.collections:
                return False
            
            collection = self.collections[collection_name]
            index = collection['index']
            
            vectors = []
            for embedding in embeddings:
                vectors.append(embedding.vector)
                
                # 메타데이터 저장
                self.metadata_storage[collection_name][embedding.id] = {
                    'document_id': embedding.document_id,
                    'chunk_id': embedding.chunk_id,
                    'metadata': embedding.metadata
                }
                self.id_mappings[collection_name][collection['next_id']] = embedding.id
                collection['next_id'] += 1
            
            if vectors:
                vectors_array = np.array(vectors, dtype=np.float32)
                index.add(vectors_array)
                return True
            return False
            
        except Exception as e:
            print(f"FAISS 다중 임베딩 추가 실패: {e}")
            return False
    
    async def get_embedding(self, embedding_id: str, collection_name: str) -> Optional[Embedding]:
        """임베딩 조회"""
        # FAISS는 ID 기반 조회가 어려움 - 메타데이터만 반환
        if collection_name in self.metadata_storage:
            metadata = self.metadata_storage[collection_name].get(embedding_id)
            if metadata:
                return Embedding(
                    id=embedding_id,
                    document_id=metadata['document_id'],
                    chunk_id=metadata['chunk_id'],
                    vector=[],  # 벡터는 FAISS에서 직접 조회 어려움
                    metadata=metadata['metadata']
                )
        return None
    
    async def delete_embedding(self, embedding_id: str, collection_name: str) -> bool:
        """임베딩 삭제 (FAISS는 개별 삭제 지원 안함)"""
        # FAISS는 개별 벡터 삭제를 지원하지 않음
        # 메타데이터만 삭제
        try:
            if collection_name in self.metadata_storage:
                if embedding_id in self.metadata_storage[collection_name]:
                    del self.metadata_storage[collection_name][embedding_id]
                    return True
            return False
        except Exception as e:
            print(f"FAISS 임베딩 삭제 실패: {e}")
            return False
    
    async def delete_embeddings_by_document(self, document_id: str, collection_name: str) -> bool:
        """문서별 임베딩 삭제"""
        try:
            if collection_name not in self.metadata_storage:
                return False
            
            # 해당 문서의 임베딩 ID들 찾기
            to_delete = []
            for emb_id, metadata in self.metadata_storage[collection_name].items():
                if metadata['document_id'] == document_id:
                    to_delete.append(emb_id)
            
            # 메타데이터에서 삭제
            for emb_id in to_delete:
                del self.metadata_storage[collection_name][emb_id]
            
            return len(to_delete) > 0
        except Exception as e:
            print(f"FAISS 문서별 임베딩 삭제 실패: {e}")
            return False
    
    async def get_embeddings_by_document(self, document_id: str, collection_name: str) -> List[Embedding]:
        """문서별 임베딩 조회"""
        try:
            if collection_name not in self.metadata_storage:
                return []
            
            embeddings = []
            for emb_id, metadata in self.metadata_storage[collection_name].items():
                if metadata['document_id'] == document_id:
                    embedding = Embedding(
                        id=emb_id,
                        document_id=metadata['document_id'],
                        chunk_id=metadata['chunk_id'],
                        vector=[],  # 벡터는 FAISS에서 직접 조회 어려움
                        metadata=metadata['metadata']
                    )
                    embeddings.append(embedding)
            
            return embeddings
        except Exception as e:
            print(f"FAISS 문서별 임베딩 조회 실패: {e}")
            return []
    
    async def count_embeddings(self, collection_name: str) -> int:
        """임베딩 개수 조회"""
        if collection_name in self.collections:
            return self.collections[collection_name]['index'].ntotal
        return 0
    
    async def update_embedding(self, embedding: Embedding, collection_name: str) -> bool:
        """임베딩 업데이트 (FAISS는 업데이트 지원 안함)"""
        # FAISS는 벡터 업데이트를 지원하지 않음
        # 메타데이터만 업데이트
        try:
            if collection_name in self.metadata_storage:
                if embedding.id in self.metadata_storage[collection_name]:
                    self.metadata_storage[collection_name][embedding.id] = {
                        'document_id': embedding.document_id,
                        'chunk_id': embedding.chunk_id,
                        'metadata': embedding.metadata
                    }
                    return True
            return False
        except Exception as e:
            print(f"FAISS 임베딩 업데이트 실패: {e}")
            return False
    
    async def health_check(self) -> bool:
        """헬스 체크"""
        return True  # FAISS는 항상 사용 가능
    
    async def optimize_collection(self, collection_name: str) -> bool:
        """컬렉션 최적화"""
        # FAISS HNSW는 자동 최적화됨
        return True
    
    def get_store_type(self) -> str:
        """저장소 타입 반환"""
        return "faiss"
