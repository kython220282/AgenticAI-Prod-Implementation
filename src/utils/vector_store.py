"""
Vector Database Integration

This module provides a unified interface for multiple vector databases
including Chroma, Pinecone, Weaviate, and FAISS.

Features:
- Multi-provider support
- Embedding generation
- Semantic search
- Memory persistence
- Metadata filtering

Usage:
    manager = VectorStoreManager(provider='chroma')
    manager.add_memory("Important information", metadata={'type': 'fact'})
    results = manager.retrieve_similar("What was important?", k=5)
"""

import os
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path
import numpy as np

try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
except ImportError:
    CHROMA_AVAILABLE = False

try:
    import pinecone
    PINECONE_AVAILABLE = True
except ImportError:
    PINECONE_AVAILABLE = False

try:
    import weaviate
    WEAVIATE_AVAILABLE = True
except ImportError:
    WEAVIATE_AVAILABLE = False

try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    FAISS_AVAILABLE = False

try:
    from sentence_transformers import SentenceTransformer
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False


class VectorStoreManager:
    """
    Unified interface for vector database operations.
    
    Supports multiple vector database providers with a consistent API
    for storing and retrieving semantic memories.
    
    Attributes:
        provider: Vector database provider name
        client: Database client instance
        embedding_model: Model for generating embeddings
        collection_name: Name of the collection/index
    """
    
    def __init__(
        self,
        provider: str = 'chroma',
        embedding_model: str = 'all-MiniLM-L6-v2',
        collection_name: str = 'agent_memory',
        **kwargs
    ):
        """
        Initialize Vector Store Manager.
        
        Args:
            provider: Database provider ('chroma', 'pinecone', 'weaviate', 'faiss')
            embedding_model: Sentence transformer model name
            collection_name: Collection/index name
            **kwargs: Provider-specific configuration
        """
        self.logger = logging.getLogger(__name__)
        self.provider = provider.lower()
        self.collection_name = collection_name
        self.client = None
        self.collection = None
        
        # Initialize embedding model
        if SENTENCE_TRANSFORMERS_AVAILABLE:
            self.embedding_model = SentenceTransformer(embedding_model)
            self.logger.info(f"Loaded embedding model: {embedding_model}")
        else:
            raise ImportError("sentence-transformers not available. Install with: pip install sentence-transformers")
        
        # Initialize provider
        if self.provider == 'chroma':
            self._init_chroma(**kwargs)
        elif self.provider == 'pinecone':
            self._init_pinecone(**kwargs)
        elif self.provider == 'weaviate':
            self._init_weaviate(**kwargs)
        elif self.provider == 'faiss':
            self._init_faiss(**kwargs)
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        
        self.logger.info(f"Vector store initialized with provider: {provider}")
    
    def _init_chroma(self, persist_directory: str = './data/vector_db/chroma', **kwargs):
        """Initialize ChromaDB."""
        if not CHROMA_AVAILABLE:
            raise ImportError("chromadb not available. Install with: pip install chromadb")
        
        persist_dir = Path(persist_directory)
        persist_dir.mkdir(parents=True, exist_ok=True)
        
        self.client = chromadb.PersistentClient(
            path=str(persist_dir),
            settings=Settings(anonymized_telemetry=False)
        )
        
        # Get or create collection
        self.collection = self.client.get_or_create_collection(
            name=self.collection_name,
            metadata={"description": "Agent semantic memory"}
        )
        
        self.logger.info(f"ChromaDB initialized at {persist_dir}")
    
    def _init_pinecone(self, **kwargs):
        """Initialize Pinecone."""
        if not PINECONE_AVAILABLE:
            raise ImportError("pinecone not available. Install with: pip install pinecone-client")
        
        api_key = os.getenv('PINECONE_API_KEY')
        if not api_key:
            raise ValueError("PINECONE_API_KEY environment variable not set")
        
        environment = kwargs.get('environment', 'gcp-starter')
        
        pinecone.init(api_key=api_key, environment=environment)
        
        # Create index if it doesn't exist
        dimension = self.embedding_model.get_sentence_embedding_dimension()
        if self.collection_name not in pinecone.list_indexes():
            pinecone.create_index(
                name=self.collection_name,
                dimension=dimension,
                metric='cosine'
            )
        
        self.client = pinecone.Index(self.collection_name)
        self.logger.info("Pinecone initialized")
    
    def _init_weaviate(self, url: str = 'http://localhost:8080', **kwargs):
        """Initialize Weaviate."""
        if not WEAVIATE_AVAILABLE:
            raise ImportError("weaviate not available. Install with: pip install weaviate-client")
        
        self.client = weaviate.Client(url=url)
        
        # Create schema if it doesn't exist
        class_name = self.collection_name.capitalize()
        if not self.client.schema.exists(class_name):
            schema = {
                "class": class_name,
                "properties": [
                    {"name": "text", "dataType": ["text"]},
                    {"name": "metadata", "dataType": ["text"]}
                ]
            }
            self.client.schema.create_class(schema)
        
        self.collection_name = class_name
        self.logger.info("Weaviate initialized")
    
    def _init_faiss(self, index_path: str = './data/vector_db/faiss_index', **kwargs):
        """Initialize FAISS."""
        if not FAISS_AVAILABLE:
            raise ImportError("faiss not available. Install with: pip install faiss-cpu")
        
        self.index_path = Path(index_path)
        self.index_path.mkdir(parents=True, exist_ok=True)
        
        dimension = self.embedding_model.get_sentence_embedding_dimension()
        
        # Load existing index or create new one
        index_file = self.index_path / f"{self.collection_name}.index"
        if index_file.exists():
            self.client = faiss.read_index(str(index_file))
        else:
            self.client = faiss.IndexFlatL2(dimension)
        
        # Store metadata separately
        self.metadata_store = []
        self.logger.info("FAISS initialized")
    
    def add_memory(
        self,
        text: str,
        metadata: Optional[Dict[str, Any]] = None,
        doc_id: Optional[str] = None
    ) -> str:
        """
        Add a memory to the vector store.
        
        Args:
            text: Text content to store
            metadata: Optional metadata dictionary
            doc_id: Optional document ID
            
        Returns:
            Document ID
        """
        # Generate embedding
        embedding = self.embedding_model.encode(text).tolist()
        
        if doc_id is None:
            from uuid import uuid4
            doc_id = str(uuid4())
        
        metadata = metadata or {}
        
        if self.provider == 'chroma':
            self.collection.add(
                ids=[doc_id],
                embeddings=[embedding],
                documents=[text],
                metadatas=[metadata]
            )
        
        elif self.provider == 'pinecone':
            self.client.upsert([(doc_id, embedding, {'text': text, **metadata})])
        
        elif self.provider == 'weaviate':
            self.client.data_object.create(
                {
                    'text': text,
                    'metadata': str(metadata)
                },
                self.collection_name,
                uuid=doc_id
            )
        
        elif self.provider == 'faiss':
            self.client.add(np.array([embedding], dtype=np.float32))
            self.metadata_store.append({'id': doc_id, 'text': text, 'metadata': metadata})
            self._save_faiss()
        
        self.logger.debug(f"Added memory with ID: {doc_id}")
        return doc_id
    
    def retrieve_similar(
        self,
        query: str,
        k: int = 5,
        filter_metadata: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve similar memories based on query.
        
        Args:
            query: Query text
            k: Number of results to return
            filter_metadata: Optional metadata filter
            
        Returns:
            List of similar memories with scores
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode(query).tolist()
        
        results = []
        
        if self.provider == 'chroma':
            response = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                where=filter_metadata
            )
            
            for i in range(len(response['ids'][0])):
                results.append({
                    'id': response['ids'][0][i],
                    'text': response['documents'][0][i],
                    'metadata': response['metadatas'][0][i],
                    'score': response['distances'][0][i]
                })
        
        elif self.provider == 'pinecone':
            response = self.client.query(
                vector=query_embedding,
                top_k=k,
                include_metadata=True,
                filter=filter_metadata
            )
            
            for match in response['matches']:
                results.append({
                    'id': match['id'],
                    'text': match['metadata'].get('text', ''),
                    'metadata': {k: v for k, v in match['metadata'].items() if k != 'text'},
                    'score': match['score']
                })
        
        elif self.provider == 'weaviate':
            response = self.client.query.get(
                self.collection_name,
                ['text', 'metadata']
            ).with_near_vector({
                'vector': query_embedding
            }).with_limit(k).do()
            
            for item in response['data']['Get'][self.collection_name]:
                results.append({
                    'id': item.get('_additional', {}).get('id', ''),
                    'text': item['text'],
                    'metadata': eval(item.get('metadata', '{}')),
                    'score': item.get('_additional', {}).get('distance', 0)
                })
        
        elif self.provider == 'faiss':
            query_vec = np.array([query_embedding], dtype=np.float32)
            distances, indices = self.client.search(query_vec, k)
            
            for i, idx in enumerate(indices[0]):
                if idx < len(self.metadata_store):
                    item = self.metadata_store[idx]
                    results.append({
                        'id': item['id'],
                        'text': item['text'],
                        'metadata': item['metadata'],
                        'score': float(distances[0][i])
                    })
        
        self.logger.debug(f"Retrieved {len(results)} similar memories")
        return results
    
    def delete_memory(self, doc_id: str) -> bool:
        """
        Delete a memory by ID.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if successful
        """
        try:
            if self.provider == 'chroma':
                self.collection.delete(ids=[doc_id])
            elif self.provider == 'pinecone':
                self.client.delete(ids=[doc_id])
            elif self.provider == 'weaviate':
                self.client.data_object.delete(doc_id)
            elif self.provider == 'faiss':
                # FAISS doesn't support deletion directly
                self.logger.warning("FAISS does not support direct deletion")
                return False
            
            self.logger.debug(f"Deleted memory: {doc_id}")
            return True
        except Exception as e:
            self.logger.error(f"Error deleting memory: {e}")
            return False
    
    def get_size(self) -> int:
        """
        Get the number of memories stored.
        
        Returns:
            Number of memories
        """
        if self.provider == 'chroma':
            return self.collection.count()
        elif self.provider == 'faiss':
            return self.client.ntotal
        else:
            return 0  # Not easily available for Pinecone/Weaviate
    
    def clear(self) -> None:
        """Clear all memories from the vector store."""
        if self.provider == 'chroma':
            self.client.delete_collection(self.collection_name)
            self.collection = self.client.create_collection(self.collection_name)
        elif self.provider == 'faiss':
            dimension = self.embedding_model.get_sentence_embedding_dimension()
            self.client = faiss.IndexFlatL2(dimension)
            self.metadata_store = []
            self._save_faiss()
        
        self.logger.info("Vector store cleared")
    
    def _save_faiss(self) -> None:
        """Save FAISS index to disk."""
        if self.provider == 'faiss':
            index_file = self.index_path / f"{self.collection_name}.index"
            faiss.write_index(self.client, str(index_file))
            
            # Save metadata
            import json
            metadata_file = self.index_path / f"{self.collection_name}_metadata.json"
            with open(metadata_file, 'w') as f:
                json.dump(self.metadata_store, f)
