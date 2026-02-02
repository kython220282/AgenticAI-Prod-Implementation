"""
Memory Module
=============

This module implements memory management systems for agents, including
short-term working memory, long-term episodic memory, and semantic knowledge.

Purpose:
--------
- Store and retrieve agent experiences
- Implement different memory types (working, episodic, semantic)
- Provide memory consolidation and forgetting mechanisms
- Enable efficient memory search and recall

Usage:
------
    from core import Memory
    
    memory = Memory(capacity=10000, memory_type='episodic')
    
    # Store experience
    memory.store({
        'timestamp': time.time(),
        'state': state,
        'action': action,
        'reward': reward
    })
    
    # Retrieve similar experiences
    similar = memory.recall(query_state, k=5)
    
    # Consolidate memories
    memory.consolidate()

Key Features:
------------
- Multiple memory types (working, episodic, semantic)
- Similarity-based retrieval
- Memory consolidation and compression
- Forgetting mechanisms (temporal decay, interference)
- Priority-based storage
"""

from typing import Any, Dict, List, Optional
from collections import deque
import numpy as np
import logging
from datetime import datetime


class Memory:
    """
    Memory management system for agents.
    
    Supports different types of memory including working memory,
    episodic memory, and semantic knowledge storage.
    """
    
    def __init__(self, capacity: int = 10000, memory_type: str = 'episodic'):
        """
        Initialize the memory system.
        
        Args:
            capacity (int): Maximum number of memories to store
            memory_type (str): Type of memory ('working', 'episodic', 'semantic')
        """
        self.capacity = capacity
        self.memory_type = memory_type
        self.logger = logging.getLogger('core.Memory')
        
        # Storage structures
        self.working_memory = deque(maxlen=100)  # Short-term, limited capacity
        self.episodic_memory = deque(maxlen=capacity)  # Experience buffer
        self.semantic_memory = {}  # Fact and knowledge storage
        
        # Memory metadata
        self.access_counts = {}
        self.last_access = {}
        self.priorities = {}
        
        self.logger.info(f"Memory initialized - Type: {memory_type}, Capacity: {capacity}")
    
    def store(self, item: Dict[str, Any], priority: float = 1.0):
        """
        Store an item in memory.
        
        Args:
            item (Dict): Item to store (experience, fact, etc.)
            priority (float): Storage priority (higher = more important)
        """
        timestamp = datetime.now()
        
        # Add metadata
        item['_timestamp'] = timestamp
        item['_priority'] = priority
        item['_access_count'] = 0
        
        # Generate unique ID
        item_id = self._generate_id(item)
        item['_id'] = item_id
        
        # Store in appropriate memory system
        if self.memory_type == 'working':
            self.working_memory.append(item)
            self.logger.debug(f"Stored in working memory: {item_id}")
            
        elif self.memory_type == 'episodic':
            # Check if we need to forget something
            if len(self.episodic_memory) >= self.capacity:
                self._forget_least_important()
            
            self.episodic_memory.append(item)
            self.priorities[item_id] = priority
            self.logger.debug(f"Stored in episodic memory: {item_id}")
            
        elif self.memory_type == 'semantic':
            # Semantic memory uses structured storage
            key = item.get('key') or item_id
            self.semantic_memory[key] = item
            self.logger.debug(f"Stored in semantic memory: {key}")
    
    def recall(self, query: Any, k: int = 5, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """
        Recall memories similar to the query.
        
        Args:
            query: Query item or pattern to match
            k (int): Number of memories to retrieve
            similarity_threshold (float): Minimum similarity score (0-1)
            
        Returns:
            List of recalled memories, sorted by relevance
        """
        self.logger.debug(f"Recalling {k} memories for query")
        
        if self.memory_type == 'episodic':
            memories = list(self.episodic_memory)
        elif self.memory_type == 'working':
            memories = list(self.working_memory)
        else:
            memories = list(self.semantic_memory.values())
        
        if not memories:
            return []
        
        # Calculate similarity scores
        scored_memories = []
        for memory in memories:
            similarity = self._calculate_similarity(query, memory)
            
            if similarity >= similarity_threshold:
                scored_memories.append((similarity, memory))
                
                # Update access metadata
                item_id = memory.get('_id')
                if item_id:
                    self.access_counts[item_id] = self.access_counts.get(item_id, 0) + 1
                    self.last_access[item_id] = datetime.now()
        
        # Sort by similarity and return top k
        scored_memories.sort(key=lambda x: x[0], reverse=True)
        recalled = [mem for score, mem in scored_memories[:k]]
        
        self.logger.debug(f"Recalled {len(recalled)} memories")
        return recalled
    
    def _calculate_similarity(self, query: Any, memory: Dict[str, Any]) -> float:
        """
        Calculate similarity between query and memory.
        
        Args:
            query: Query item
            memory: Memory item
            
        Returns:
            float: Similarity score (0-1)
        """
        # Placeholder implementation - use embedding similarity in practice
        # This could use cosine similarity of state embeddings, etc.
        
        # Simple example: compare state if both are dicts
        if isinstance(query, dict) and 'state' in memory:
            # Implement actual similarity metric
            return 0.7  # Placeholder
        
        return 0.5  # Default similarity
    
    def consolidate(self):
        """
        Consolidate memories by merging similar experiences.
        
        This helps compress memory and strengthen important patterns.
        """
        self.logger.info("Consolidating memories")
        
        # Group similar memories
        # Merge or compress redundant information
        # Update priorities based on importance
        
        # Placeholder implementation
        pass
    
    def _forget_least_important(self):
        """
        Remove the least important memory to make space.
        
        Uses combination of recency, frequency, and priority.
        """
        if not self.episodic_memory:
            return
        
        # Calculate importance scores
        importance_scores = []
        current_time = datetime.now()
        
        for memory in self.episodic_memory:
            item_id = memory.get('_id')
            
            # Factors: priority, access frequency, recency
            priority = self.priorities.get(item_id, 1.0)
            access_count = self.access_counts.get(item_id, 0)
            
            timestamp = memory.get('_timestamp', current_time)
            age = (current_time - timestamp).total_seconds()
            recency = 1.0 / (1.0 + age / 3600)  # Decay over hours
            
            # Combined importance score
            importance = priority * (1 + access_count) * recency
            importance_scores.append((importance, memory))
        
        # Remove least important
        if importance_scores:
            importance_scores.sort(key=lambda x: x[0])
            least_important = importance_scores[0][1]
            self.episodic_memory.remove(least_important)
            
            item_id = least_important.get('_id')
            self.logger.debug(f"Forgot memory: {item_id}")
    
    def _generate_id(self, item: Dict[str, Any]) -> str:
        """Generate unique ID for memory item."""
        timestamp = item.get('_timestamp', datetime.now())
        return f"mem_{timestamp.timestamp()}_{hash(str(item)) % 10000}"
    
    def clear(self, memory_type: Optional[str] = None):
        """
        Clear memories.
        
        Args:
            memory_type (str, optional): Specific memory type to clear
        """
        if memory_type == 'working' or memory_type is None:
            self.working_memory.clear()
            
        if memory_type == 'episodic' or memory_type is None:
            self.episodic_memory.clear()
            self.priorities.clear()
            
        if memory_type == 'semantic' or memory_type is None:
            self.semantic_memory.clear()
        
        self.access_counts.clear()
        self.last_access.clear()
        
        self.logger.info(f"Cleared {memory_type or 'all'} memories")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            'memory_type': self.memory_type,
            'capacity': self.capacity,
            'working_memory_size': len(self.working_memory),
            'episodic_memory_size': len(self.episodic_memory),
            'semantic_memory_size': len(self.semantic_memory),
            'total_accesses': sum(self.access_counts.values())
        }
    
    def __len__(self) -> int:
        """Return total number of memories stored."""
        if self.memory_type == 'working':
            return len(self.working_memory)
        elif self.memory_type == 'episodic':
            return len(self.episodic_memory)
        else:
            return len(self.semantic_memory)
    
    def __repr__(self) -> str:
        """String representation of memory system."""
        return f"Memory(type='{self.memory_type}', size={len(self)}, capacity={self.capacity})"
