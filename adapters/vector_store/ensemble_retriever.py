"""
Ensemble retriever adapter that combines multiple retrievers for better results.
"""

from typing import List, Optional, Dict, Any, Union
from enum import Enum
import asyncio
from collections import defaultdict
from core.entities.document import Query, RetrievalResult
from core.ports.retriever import RetrieverPort


class FusionStrategy(Enum):
    """Fusion strategies for combining retrieval results."""
    SCORE_FUSION = "score_fusion"
    RANK_FUSION = "rank_fusion"  # Reciprocal Rank Fusion (RRF)
    WEIGHTED_SCORE = "weighted_score"
    VOTING = "voting"


class EnsembleRetrieverAdapter(RetrieverPort):
    """Ensemble retriever that combines results from multiple retrievers."""
    
    def __init__(
        self,
        retrievers: List[RetrieverPort],
        fusion_strategy: FusionStrategy = FusionStrategy.RANK_FUSION,
        weights: Optional[List[float]] = None,
        rrf_k: int = 60  # RRF parameter
    ):
        """
        Initialize ensemble retriever.
        
        Args:
            retrievers: List of retriever instances to combine
            fusion_strategy: Strategy for combining results
            weights: Weights for each retriever (if using weighted strategies)
            rrf_k: Parameter for Reciprocal Rank Fusion
        """
        if not retrievers:
            raise ValueError("At least one retriever must be provided")
        
        self._retrievers = retrievers
        self._fusion_strategy = fusion_strategy
        self._rrf_k = rrf_k
        self._collection_name = "documents"
        
        # Set weights
        if weights is None:
            self._weights = [1.0 / len(retrievers)] * len(retrievers)
        else:
            if len(weights) != len(retrievers):
                raise ValueError("Number of weights must match number of retrievers")
            # Normalize weights
            total_weight = sum(weights)
            self._weights = [w / total_weight for w in weights]
    
    def set_collection_name(self, collection_name: str) -> None:
        """Set the collection name for all retrievers."""
        self._collection_name = collection_name
        for retriever in self._retrievers:
            retriever.set_collection_name(collection_name)
    
    def get_collection_name(self) -> str:
        """Get the current collection name."""
        return self._collection_name
    
    def get_retriever_type(self) -> str:
        """Get the type of this retriever."""
        return f"ensemble_retriever_{self._fusion_strategy.value}"
    
    async def retrieve(
        self,
        query: Query,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Retrieve documents using ensemble of retrievers."""
        try:
            # Get results from all retrievers concurrently
            tasks = []
            for retriever in self._retrievers:
                task = retriever.retrieve(
                    query=query,
                    top_k=top_k * 2,  # Get more results for better fusion
                    score_threshold=score_threshold,
                    filter_metadata=filter_metadata
                )
                tasks.append(task)
            
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and get valid results
            valid_results = []
            for i, result in enumerate(all_results):
                if isinstance(result, Exception):
                    print(f"Warning: Retriever {i} failed: {result}")
                    valid_results.append([])
                else:
                    valid_results.append(result)
            
            if not any(valid_results):
                return []
            
            # Combine results using selected fusion strategy
            combined_results = self._fuse_results(valid_results, top_k)
            
            return combined_results
            
        except Exception as e:
            raise Exception(f"Ensemble retrieval failed: {str(e)}")
    
    async def retrieve_by_text(
        self,
        query_text: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[RetrievalResult]:
        """Retrieve relevant documents for a text query."""
        try:
            # Create Query entity from text
            query = Query.create(query_text)
            
            # Use the regular retrieve method
            return await self.retrieve(
                query=query,
                top_k=top_k,
                score_threshold=score_threshold,
                filter_metadata=filter_metadata
            )
            
        except Exception as e:
            raise Exception(f"Text retrieval failed: {str(e)}")
    
    async def retrieve_similar_documents(
        self,
        document_id: str,
        top_k: int = 10,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """Find documents similar to a given document using ensemble."""
        try:
            # Get results from all retrievers concurrently
            tasks = []
            for retriever in self._retrievers:
                task = retriever.retrieve_similar_documents(
                    document_id=document_id,
                    top_k=top_k * 2,
                    score_threshold=score_threshold
                )
                tasks.append(task)
            
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and get valid results
            valid_results = []
            for i, result in enumerate(all_results):
                if isinstance(result, Exception):
                    print(f"Warning: Retriever {i} failed: {result}")
                    valid_results.append([])
                else:
                    valid_results.append(result)
            
            if not any(valid_results):
                return []
            
            # Combine results using selected fusion strategy
            combined_results = self._fuse_results(valid_results, top_k)
            
            return combined_results
            
        except Exception as e:
            raise Exception(f"Similar document retrieval failed: {str(e)}")
    
    async def retrieve_with_reranking(
        self,
        query: Query,
        top_k: int = 10,
        rerank_top_k: int = 100,
        score_threshold: Optional[float] = None
    ) -> List[RetrievalResult]:
        """Retrieve with reranking using ensemble."""
        try:
            # Get results from all retrievers with reranking
            tasks = []
            for retriever in self._retrievers:
                task = retriever.retrieve_with_reranking(
                    query=query,
                    top_k=top_k,
                    rerank_top_k=rerank_top_k,
                    score_threshold=score_threshold
                )
                tasks.append(task)
            
            all_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Filter out exceptions and get valid results
            valid_results = []
            for i, result in enumerate(all_results):
                if isinstance(result, Exception):
                    print(f"Warning: Retriever {i} failed: {result}")
                    valid_results.append([])
                else:
                    valid_results.append(result)
            
            if not any(valid_results):
                return []
            
            # Combine results using selected fusion strategy
            combined_results = self._fuse_results(valid_results, top_k)
            
            return combined_results
            
        except Exception as e:
            raise Exception(f"Reranking retrieval failed: {str(e)}")
    
    def _fuse_results(self, all_results: List[List[RetrievalResult]], top_k: int) -> List[RetrievalResult]:
        """Fuse results from multiple retrievers."""
        if self._fusion_strategy == FusionStrategy.SCORE_FUSION:
            return self._score_fusion(all_results, top_k)
        elif self._fusion_strategy == FusionStrategy.RANK_FUSION:
            return self._rank_fusion(all_results, top_k)
        elif self._fusion_strategy == FusionStrategy.WEIGHTED_SCORE:
            return self._weighted_score_fusion(all_results, top_k)
        elif self._fusion_strategy == FusionStrategy.VOTING:
            return self._voting_fusion(all_results, top_k)
        else:
            raise ValueError(f"Unknown fusion strategy: {self._fusion_strategy}")
    
    def _score_fusion(self, all_results: List[List[RetrievalResult]], top_k: int) -> List[RetrievalResult]:
        """Combine results using average score fusion."""
        document_scores = defaultdict(list)
        document_results = {}
        
        # Collect scores for each document
        for results in all_results:
            for result in results:
                key = f"{result.document_id}_{result.chunk_id}"
                document_scores[key].append(result.score)
                document_results[key] = result
        
        # Calculate average scores
        fused_results = []
        for doc_key, scores in document_scores.items():
            avg_score = sum(scores) / len(scores)
            result = document_results[doc_key]
            
            # Create new result with fused score
            fused_result = RetrievalResult(
                document_id=result.document_id,
                chunk_id=result.chunk_id,
                content=result.content,
                score=avg_score,
                rank=0,  # Will be set later
                metadata=result.metadata
            )
            fused_results.append(fused_result)
        
        # Sort by score and assign ranks
        fused_results.sort(key=lambda x: x.score, reverse=True)
        for i, result in enumerate(fused_results[:top_k]):
            result.rank = i + 1
        
        return fused_results[:top_k]
    
    def _rank_fusion(self, all_results: List[List[RetrievalResult]], top_k: int) -> List[RetrievalResult]:
        """Combine results using Reciprocal Rank Fusion (RRF)."""
        document_scores = defaultdict(float)
        document_results = {}
        
        # Calculate RRF scores
        for results in all_results:
            for result in results:
                key = f"{result.document_id}_{result.chunk_id}"
                # RRF formula: 1 / (k + rank)
                rrf_score = 1.0 / (self._rrf_k + result.rank)
                document_scores[key] += rrf_score
                document_results[key] = result
        
        # Create fused results
        fused_results = []
        for doc_key, rrf_score in document_scores.items():
            result = document_results[doc_key]
            
            fused_result = RetrievalResult(
                document_id=result.document_id,
                chunk_id=result.chunk_id,
                content=result.content,
                score=rrf_score,
                rank=0,  # Will be set later
                metadata=result.metadata
            )
            fused_results.append(fused_result)
        
        # Sort by RRF score and assign ranks
        fused_results.sort(key=lambda x: x.score, reverse=True)
        for i, result in enumerate(fused_results[:top_k]):
            result.rank = i + 1
        
        return fused_results[:top_k]
    
    def _weighted_score_fusion(self, all_results: List[List[RetrievalResult]], top_k: int) -> List[RetrievalResult]:
        """Combine results using weighted score fusion."""
        document_scores = defaultdict(float)
        document_counts = defaultdict(int)
        document_results = {}
        
        # Calculate weighted scores
        for i, results in enumerate(all_results):
            weight = self._weights[i]
            for result in results:
                key = f"{result.document_id}_{result.chunk_id}"
                document_scores[key] += result.score * weight
                document_counts[key] += 1
                document_results[key] = result
        
        # Create fused results
        fused_results = []
        for doc_key, weighted_score in document_scores.items():
            result = document_results[doc_key]
            
            fused_result = RetrievalResult(
                document_id=result.document_id,
                chunk_id=result.chunk_id,
                content=result.content,
                score=weighted_score,
                rank=0,  # Will be set later
                metadata=result.metadata
            )
            fused_results.append(fused_result)
        
        # Sort by weighted score and assign ranks
        fused_results.sort(key=lambda x: x.score, reverse=True)
        for i, result in enumerate(fused_results[:top_k]):
            result.rank = i + 1
        
        return fused_results[:top_k]
    
    def _voting_fusion(self, all_results: List[List[RetrievalResult]], top_k: int) -> List[RetrievalResult]:
        """Combine results using voting (frequency-based) fusion."""
        document_votes = defaultdict(int)
        document_scores = defaultdict(list)
        document_results = {}
        
        # Count votes and collect scores
        for results in all_results:
            for result in results:
                key = f"{result.document_id}_{result.chunk_id}"
                document_votes[key] += 1
                document_scores[key].append(result.score)
                document_results[key] = result
        
        # Create fused results
        fused_results = []
        for doc_key, votes in document_votes.items():
            result = document_results[doc_key]
            avg_score = sum(document_scores[doc_key]) / len(document_scores[doc_key])
            
            # Combine votes and average score
            combined_score = votes + avg_score * 0.1  # Vote weight is higher
            
            fused_result = RetrievalResult(
                document_id=result.document_id,
                chunk_id=result.chunk_id,
                content=result.content,
                score=combined_score,
                rank=0,  # Will be set later
                metadata=result.metadata
            )
            fused_results.append(fused_result)
        
        # Sort by combined score and assign ranks
        fused_results.sort(key=lambda x: x.score, reverse=True)
        for i, result in enumerate(fused_results[:top_k]):
            result.rank = i + 1
        
        return fused_results[:top_k]
    
    async def get_retriever_info(self) -> Dict[str, Any]:
        """Get information about this ensemble retriever."""
        retriever_infos = []
        for i, retriever in enumerate(self._retrievers):
            try:
                info = await retriever.get_retriever_info()
                info["weight"] = self._weights[i]
                retriever_infos.append(info)
            except Exception as e:
                retriever_infos.append({
                    "type": retriever.get_retriever_type(),
                    "weight": self._weights[i],
                    "error": str(e)
                })
        
        return {
            "type": self.get_retriever_type(),
            "collection_name": self._collection_name,
            "fusion_strategy": self._fusion_strategy.value,
            "rrf_k": self._rrf_k,
            "num_retrievers": len(self._retrievers),
            "retrievers": retriever_infos,
            "capabilities": [
                "ensemble_retrieval",
                "score_fusion",
                "rank_fusion",
                "weighted_fusion",
                "voting_fusion"
            ]
        }
    
    async def health_check(self) -> bool:
        """Check if the ensemble retriever is healthy."""
        try:
            # Check if at least one retriever is healthy
            health_checks = []
            for retriever in self._retrievers:
                try:
                    health = await retriever.health_check()
                    health_checks.append(health)
                except Exception:
                    health_checks.append(False)
            
            # Return True if at least one retriever is healthy
            return any(health_checks)
            
        except Exception:
            return False
    
    def add_retriever(self, retriever: RetrieverPort, weight: float = 1.0) -> None:
        """Add a new retriever to the ensemble."""
        self._retrievers.append(retriever)
        
        # Recalculate weights
        current_total = sum(self._weights)
        new_total = current_total + weight
        
        # Normalize all weights
        self._weights = [w * current_total / new_total for w in self._weights]
        self._weights.append(weight / new_total)
        
        # Set collection name for new retriever
        retriever.set_collection_name(self._collection_name)
    
    def remove_retriever(self, index: int) -> None:
        """Remove a retriever from the ensemble."""
        if 0 <= index < len(self._retrievers):
            self._retrievers.pop(index)
            removed_weight = self._weights.pop(index)
            
            # Renormalize remaining weights
            if self._weights:
                remaining_total = sum(self._weights)
                self._weights = [w / remaining_total for w in self._weights]
    
    def set_fusion_strategy(self, strategy: FusionStrategy) -> None:
        """Change the fusion strategy."""
        self._fusion_strategy = strategy
    
    def set_weights(self, weights: List[float]) -> None:
        """Set new weights for retrievers."""
        if len(weights) != len(self._retrievers):
            raise ValueError("Number of weights must match number of retrievers")
        
        # Normalize weights
        total_weight = sum(weights)
        self._weights = [w / total_weight for w in weights]
