"""
어댑터 팩토리 - 설정에 따라 적절한 어댑터를 생성
"""

from typing import Protocol
from config.settings import ConfigPort
from core.ports.vector_store import VectorStorePort
from core.ports.embedding_model import EmbeddingModelPort
from core.ports.document_loader import DocumentLoaderPort
from core.ports.text_chunker import TextChunkerPort
from core.ports.retriever import RetrieverPort

# Vector Store Adapters
from adapters.vector_store.qdrant_vector_store import QdrantVectorStoreAdapter
from adapters.vector_store.mock_vector_store import MockVectorStoreAdapter
from adapters.vector_store.faiss_vector_store import FaissVectorStoreAdapter

# Embedding Adapters  
from adapters.embedding.openai_embedding import OpenAIEmbeddingAdapter

# Document Loader Adapters
from adapters.pdf.pdf_loader import PdfLoaderAdapter
from adapters.pdf.json_loader import JsonLoaderAdapter
from adapters.pdf.web_scraper_loader import WebScraperLoaderAdapter
from adapters.pdf.unstructured_loader import UnstructuredLoaderAdapter

# Text Chunker Adapters
from adapters.embedding.text_chunker import RecursiveTextChunkerAdapter
from adapters.embedding.semantic_text_chunker import SemanticTextChunkerAdapter

# Retriever Adapters
from adapters.vector_store.simple_retriever import SimpleRetrieverAdapter
from adapters.vector_store.ensemble_retriever import EnsembleRetrieverAdapter, FusionStrategy


class AdapterFactory:
    """어댑터 팩토리 클래스"""
    
    @staticmethod
    def create_vector_store_adapter(adapter_type: str = "qdrant") -> VectorStorePort:
        """벡터 저장소 어댑터 생성"""
        if adapter_type.lower() == "qdrant":
            return QdrantVectorStoreAdapter()
        elif adapter_type.lower() == "mock":
            return MockVectorStoreAdapter()
        elif adapter_type.lower() == "faiss":
            return FaissVectorStoreAdapter()
        # elif adapter_type.lower() == "chroma":
        #     return ChromaVectorStoreAdapter()
        else:
            raise ValueError(f"지원하지 않는 벡터 저장소 타입: {adapter_type}")
    
    @staticmethod
    def create_embedding_adapter(adapter_type: str = "openai", config: ConfigPort = None) -> EmbeddingModelPort:
        """임베딩 모델 어댑터 생성"""
        if adapter_type.lower() == "openai":
            return OpenAIEmbeddingAdapter(config)
        # elif adapter_type.lower() == "huggingface":
        #     return HuggingFaceEmbeddingAdapter(config)
        # elif adapter_type.lower() == "cohere":
        #     return CohereEmbeddingAdapter(config)
        else:
            raise ValueError(f"지원하지 않는 임베딩 모델 타입: {adapter_type}")
    
    @staticmethod
    def create_document_loader_adapter(adapter_type: str = "pdf", **kwargs) -> DocumentLoaderPort:
        """문서 로더 어댑터 생성"""
        if adapter_type.lower() == "pdf":
            return PdfLoaderAdapter()
        elif adapter_type.lower() == "json":
            return JsonLoaderAdapter()
        elif adapter_type.lower() == "web_scraper" or adapter_type.lower() == "web":
            return WebScraperLoaderAdapter(**kwargs)
        elif adapter_type.lower() == "unstructured":
            return UnstructuredLoaderAdapter()
        # elif adapter_type.lower() == "pymupdf":
        #     return PyMuPDFLoaderAdapter()
        else:
            raise ValueError(f"지원하지 않는 문서 로더 타입: {adapter_type}")
    
    @staticmethod
    def create_text_chunker_adapter(
        adapter_type: str = "recursive", 
        chunk_size: int = 1000, 
        chunk_overlap: int = 200
    ) -> TextChunkerPort:
        """텍스트 청킹 어댑터 생성"""
        if adapter_type.lower() == "recursive":
            return RecursiveTextChunkerAdapter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        elif adapter_type.lower() == "semantic":
            return SemanticTextChunkerAdapter(
                chunk_size=chunk_size,
                chunk_overlap=chunk_overlap
            )
        # elif adapter_type.lower() == "token":
        #     return TokenTextChunkerAdapter(
        #         chunk_size=chunk_size,
        #         chunk_overlap=chunk_overlap
        #     )
        else:
            raise ValueError(f"지원하지 않는 텍스트 청킹 타입: {adapter_type}")
    
    @staticmethod
    def create_retriever_adapter(
        adapter_type: str = "simple",
        vector_store: VectorStorePort = None,
        embedding_model: EmbeddingModelPort = None,
        **kwargs
    ) -> RetrieverPort:
        """리트리버 어댑터 생성"""
        if adapter_type.lower() == "simple":
            if not vector_store or not embedding_model:
                raise ValueError("Simple retriever requires vector_store and embedding_model")
            return SimpleRetrieverAdapter(vector_store, embedding_model)
        elif adapter_type.lower() == "ensemble":
            retrievers = kwargs.get('retrievers', [])
            if not retrievers:
                raise ValueError("Ensemble retriever requires a list of retrievers")
            
            fusion_strategy = kwargs.get('fusion_strategy', FusionStrategy.RANK_FUSION)
            weights = kwargs.get('weights', None)
            rrf_k = kwargs.get('rrf_k', 60)
            
            return EnsembleRetrieverAdapter(
                retrievers=retrievers,
                fusion_strategy=fusion_strategy,
                weights=weights,
                rrf_k=rrf_k
            )
        else:
            raise ValueError(f"지원하지 않는 리트리버 타입: {adapter_type}")
    
    @staticmethod
    def create_ensemble_retriever(
        retrievers: list[RetrieverPort],
        fusion_strategy: str = "rank_fusion",
        weights: list[float] = None,
        rrf_k: int = 60
    ) -> EnsembleRetrieverAdapter:
        """앙상블 리트리버 생성 (편의 메서드)"""
        # 문자열을 FusionStrategy enum으로 변환
        strategy_map = {
            "score_fusion": FusionStrategy.SCORE_FUSION,
            "rank_fusion": FusionStrategy.RANK_FUSION,
            "weighted_score": FusionStrategy.WEIGHTED_SCORE,
            "voting": FusionStrategy.VOTING
        }
        
        strategy = strategy_map.get(fusion_strategy.lower(), FusionStrategy.RANK_FUSION)
        
        return EnsembleRetrieverAdapter(
            retrievers=retrievers,
            fusion_strategy=strategy,
            weights=weights,
            rrf_k=rrf_k
        )


# 편의 함수들
def get_vector_store_adapter(config: ConfigPort) -> VectorStorePort:
    """설정에서 벡터 저장소 어댑터 타입을 읽어서 생성"""
    adapter_type = config.get_vector_store_type()
    return AdapterFactory.create_vector_store_adapter(adapter_type)


def get_embedding_adapter(config: ConfigPort) -> EmbeddingModelPort:
    """설정에서 임베딩 어댑터 타입을 읽어서 생성"""
    adapter_type = config.get_embedding_type()
    return AdapterFactory.create_embedding_adapter(adapter_type, config)


def get_document_loader_adapter(config: ConfigPort) -> DocumentLoaderPort:
    """설정에서 문서 로더 어댑터 타입을 읽어서 생성"""
    adapter_type = config.get_document_loader_type()
    return AdapterFactory.create_document_loader_adapter(adapter_type)


def get_text_chunker_adapter(config: ConfigPort) -> TextChunkerPort:
    """설정에서 텍스트 청킹 어댑터 타입을 읽어서 생성"""
    adapter_type = config.get_text_chunker_type()
    return AdapterFactory.create_text_chunker_adapter(
        adapter_type=adapter_type,
        chunk_size=config.get_chunk_size(),
        chunk_overlap=config.get_chunk_overlap()
    )


def get_retriever_adapter(config: ConfigPort) -> RetrieverPort:
    """설정에서 리트리버 어댑터 타입을 읽어서 생성"""
    adapter_type = config.get_retriever_type()
    
    if adapter_type.lower() == "simple":
        vector_store = get_vector_store_adapter(config)
        embedding_model = get_embedding_adapter(config)
        return AdapterFactory.create_retriever_adapter(
            adapter_type="simple",
            vector_store=vector_store,
            embedding_model=embedding_model
        )
    elif adapter_type.lower() == "ensemble":
        # 기본적으로 3개의 simple retriever로 앙상블 구성
        vector_store = get_vector_store_adapter(config)
        embedding_model = get_embedding_adapter(config)
        
        retrievers = [
            AdapterFactory.create_retriever_adapter(
                adapter_type="simple",
                vector_store=vector_store,
                embedding_model=embedding_model
            ) for _ in range(3)
        ]
        
        return AdapterFactory.create_ensemble_retriever(
            retrievers=retrievers,
            fusion_strategy="rank_fusion"
        )
    else:
        raise ValueError(f"지원하지 않는 리트리버 타입: {adapter_type}")


class DependencyContainer:
    """의존성 주입 컨테이너"""
    
    def __init__(self, config: ConfigPort):
        self.config = config
        self._vector_store = None
        self._embedding_model = None
        self._document_loader = None
        self._text_chunker = None
        self._retriever = None
    
    @property
    def vector_store(self) -> VectorStorePort:
        """벡터 저장소 싱글톤 인스턴스"""
        if self._vector_store is None:
            self._vector_store = get_vector_store_adapter(self.config)
        return self._vector_store
    
    @property
    def embedding_model(self) -> EmbeddingModelPort:
        """임베딩 모델 싱글톤 인스턴스"""
        if self._embedding_model is None:
            self._embedding_model = get_embedding_adapter(self.config)
        return self._embedding_model
    
    @property
    def document_loader(self) -> DocumentLoaderPort:
        """문서 로더 싱글톤 인스턴스"""
        if self._document_loader is None:
            self._document_loader = get_document_loader_adapter(self.config)
        return self._document_loader
    
    @property
    def text_chunker(self) -> TextChunkerPort:
        """텍스트 청킹 싱글톤 인스턴스"""
        if self._text_chunker is None:
            self._text_chunker = get_text_chunker_adapter(self.config)
        return self._text_chunker
    
    @property
    def retriever(self) -> RetrieverPort:
        """리트리버 싱글톤 인스턴스"""
        if self._retriever is None:
            self._retriever = get_retriever_adapter(self.config)
        return self._retriever
    
    def reset(self):
        """모든 인스턴스 초기화 (테스트용)"""
        self._vector_store = None
        self._embedding_model = None
        self._document_loader = None
        self._text_chunker = None
        self._retriever = None


# 전역 의존성 컨테이너 (설정 기반 자동 초기화)
from config.settings import config as global_config
container = DependencyContainer(global_config)
