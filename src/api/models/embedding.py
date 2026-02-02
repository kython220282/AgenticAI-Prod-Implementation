"""
Embedding model for vector storage and semantic search.
"""

from typing import Optional, List, Dict, Any

from sqlalchemy import Column, String, Text, JSON
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY
from sqlalchemy.orm import relationship
from sqlalchemy import ForeignKey
try:
    from pgvector.sqlalchemy import Vector
    HAS_PGVECTOR = True
except ImportError:
    HAS_PGVECTOR = False
    # Fallback to regular ARRAY
    Vector = None

from src.api.models.base import Base


class Embedding(Base):
    """Vector embedding storage for semantic search."""
    
    __tablename__ = "embeddings"
    
    # Content
    content = Column(Text, nullable=False)
    
    # Vector embedding (1536 dimensions for OpenAI)
    if HAS_PGVECTOR and Vector is not None:
        embedding = Column(Vector(1536), nullable=True)
    else:
        # Fallback to ARRAY if pgvector not available
        embedding = Column(ARRAY(float, dimensions=1536), nullable=True)
    
    # Metadata
    metadata = Column(JSONB, default={}, nullable=False)
    source = Column(String(255), nullable=True, index=True)
    
    # Owner relationship
    owner_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    owner = relationship("User", back_populates="embeddings")
    
    # Document grouping (for multi-chunk documents)
    document_id = Column(String(255), nullable=True, index=True)
    chunk_index = Column(String, nullable=True)
    
    def __repr__(self) -> str:
        return f"<Embedding(id={self.id}, source={self.source})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        data = super().to_dict()
        data['metadata'] = self.metadata or {}
        # Don't include embedding vector in dict by default (too large)
        if 'embedding' in data:
            del data['embedding']
        return data
    
    @property
    def embedding_list(self) -> Optional[List[float]]:
        """Get embedding as list."""
        if self.embedding is not None:
            if isinstance(self.embedding, list):
                return self.embedding
            # Handle pgvector format if needed
            return list(self.embedding)
        return None
