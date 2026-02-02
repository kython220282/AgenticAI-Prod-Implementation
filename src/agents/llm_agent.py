"""
LLM-Powered Agent Implementation

This module provides an agent that leverages Large Language Models
for decision-making, reasoning, and natural language interaction.

Features:
- LangChain integration
- Prompt template management
- Vector memory retrieval
- Token usage tracking
- Multi-turn conversations

Usage:
    config = {
        'llm_provider': 'openai',
        'model': 'gpt-4-turbo-preview',
        'temperature': 0.7,
        'use_vector_memory': True
    }
    agent = LLMAgent(config, name="ChatAgent")
    agent.initialize()
    response = agent.act("What should I do next?")
"""

from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

try:
    from langchain.chat_models import ChatOpenAI
    from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
    from langchain.schema import HumanMessage, AIMessage, SystemMessage
    from langchain.memory import ConversationBufferMemory
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False

from .base_agent import BaseAgent
from ..utils.prompt_manager import PromptManager
from ..utils.token_tracker import TokenTracker
from ..utils.vector_store import VectorStoreManager


class LLMAgent(BaseAgent):
    """
    Agent powered by Large Language Models.
    
    This agent uses LLMs for natural language understanding,
    reasoning, and decision-making. It integrates with vector
    databases for long-term memory and tracks token usage.
    
    Attributes:
        llm: The language model instance
        prompt_manager: Manages prompt templates
        token_tracker: Tracks token usage
        vector_memory: Vector database for semantic memory
        conversation_history: Chat history
    """
    
    def __init__(self, config: Dict[str, Any], name: str = "LLMAgent"):
        """
        Initialize LLM Agent.
        
        Args:
            config: Agent configuration including:
                - llm_provider: LLM provider (openai, anthropic)
                - model: Model name
                - temperature: Sampling temperature
                - max_tokens: Maximum response tokens
                - use_vector_memory: Enable vector memory
                - system_prompt: System prompt template
            name: Agent identifier
        """
        super().__init__(config, name)
        
        if not LANGCHAIN_AVAILABLE:
            raise ImportError("LangChain not installed. Install with: pip install langchain langchain-openai")
        
        self.logger = logging.getLogger(f"{__name__}.{name}")
        
        # Configuration
        self.llm_provider = config.get('llm_provider', 'openai')
        self.model = config.get('model', 'gpt-4-turbo-preview')
        self.temperature = config.get('temperature', 0.7)
        self.max_tokens = config.get('max_tokens', 2000)
        self.use_vector_memory = config.get('use_vector_memory', True)
        self.system_prompt_key = config.get('system_prompt', 'default')
        
        # Components
        self.llm = None
        self.prompt_manager = PromptManager()
        self.token_tracker = TokenTracker(agent_name=name)
        self.vector_memory = None
        self.conversation_history = []
        self.memory = None
        
        self.logger.info(f"LLM Agent '{name}' created with model {self.model}")
    
    def initialize(self) -> None:
        """Initialize the LLM and supporting components."""
        self.logger.info("Initializing LLM Agent...")
        
        # Initialize LLM
        if self.llm_provider == 'openai':
            self.llm = ChatOpenAI(
                model=self.model,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
        else:
            raise ValueError(f"Unsupported LLM provider: {self.llm_provider}")
        
        # Initialize conversation memory
        self.memory = ConversationBufferMemory(
            return_messages=True,
            memory_key="chat_history"
        )
        
        # Initialize vector memory if enabled
        if self.use_vector_memory:
            self.vector_memory = VectorStoreManager()
            self.logger.info("Vector memory enabled")
        
        self.state['status'] = 'initialized'
        self.logger.info("LLM Agent initialized successfully")
    
    def perceive(self, observation: Any) -> Dict[str, Any]:
        """
        Process observations using LLM understanding.
        
        Args:
            observation: Input observation (text or structured data)
            
        Returns:
            Processed perception with semantic understanding
        """
        if isinstance(observation, str):
            perception = {
                'type': 'text',
                'content': observation,
                'timestamp': datetime.now().isoformat()
            }
        else:
            perception = {
                'type': 'structured',
                'data': observation,
                'timestamp': datetime.now().isoformat()
            }
        
        # Store in conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': observation,
            'timestamp': perception['timestamp']
        })
        
        # Store in vector memory for long-term retrieval
        if self.vector_memory:
            self.vector_memory.add_memory(
                text=str(observation),
                metadata={'type': 'perception', 'timestamp': perception['timestamp']}
            )
        
        return perception
    
    def decide(self, perception: Dict[str, Any]) -> Dict[str, Any]:
        """
        Make decisions using LLM reasoning.
        
        Args:
            perception: Processed observation
            
        Returns:
            Decision with reasoning trace
        """
        # Get relevant context from vector memory
        context = ""
        if self.vector_memory:
            relevant_memories = self.vector_memory.retrieve_similar(
                query=str(perception.get('content', '')),
                k=5
            )
            if relevant_memories:
                context = "\n".join([mem['text'] for mem in relevant_memories])
        
        # Build prompt with template
        system_prompt = self.prompt_manager.get_system_prompt(self.system_prompt_key)
        
        messages = [
            SystemMessage(content=system_prompt)
        ]
        
        # Add context if available
        if context:
            messages.append(SystemMessage(content=f"Relevant context:\n{context}"))
        
        # Add conversation history (last 10 messages)
        for msg in self.conversation_history[-10:]:
            if msg['role'] == 'user':
                messages.append(HumanMessage(content=msg['content']))
            elif msg['role'] == 'assistant':
                messages.append(AIMessage(content=msg['content']))
        
        # Get LLM response
        try:
            response = self.llm.invoke(messages)
            response_text = response.content
            
            # Track tokens
            self.token_tracker.track(
                prompt_tokens=response.response_metadata.get('token_usage', {}).get('prompt_tokens', 0),
                completion_tokens=response.response_metadata.get('token_usage', {}).get('completion_tokens', 0),
                model=self.model
            )
            
            decision = {
                'action': 'respond',
                'response': response_text,
                'reasoning': 'LLM-generated response',
                'confidence': 0.9,
                'timestamp': datetime.now().isoformat()
            }
            
            # Store in conversation history
            self.conversation_history.append({
                'role': 'assistant',
                'content': response_text,
                'timestamp': decision['timestamp']
            })
            
            self.logger.info(f"LLM decision made: {response_text[:100]}...")
            return decision
            
        except Exception as e:
            self.logger.error(f"Error in LLM decision: {e}")
            return {
                'action': 'error',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def act(self, observation: Any) -> Any:
        """
        Process observation and generate response.
        
        Args:
            observation: Input observation
            
        Returns:
            Agent's response
        """
        perception = self.perceive(observation)
        decision = self.decide(perception)
        return decision.get('response', decision.get('error', 'No response'))
    
    def learn(self, experience: Dict[str, Any]) -> None:
        """
        Learn from experience by updating vector memory.
        
        Args:
            experience: Experience data including feedback
        """
        if self.vector_memory and 'feedback' in experience:
            self.vector_memory.add_memory(
                text=f"Feedback: {experience['feedback']}",
                metadata={
                    'type': 'learning',
                    'timestamp': datetime.now().isoformat()
                }
            )
            self.logger.info("Learned from experience")
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get agent statistics including token usage.
        
        Returns:
            Dictionary with agent statistics
        """
        stats = {
            'name': self.name,
            'status': self.state.get('status'),
            'model': self.model,
            'conversations': len(self.conversation_history),
            'token_usage': self.token_tracker.get_summary()
        }
        
        if self.vector_memory:
            stats['vector_memory_size'] = self.vector_memory.get_size()
        
        return stats
    
    def reset(self) -> None:
        """Reset agent state and clear conversation history."""
        self.state = {'status': 'initialized'}
        self.conversation_history = []
        if self.memory:
            self.memory.clear()
        self.logger.info("Agent reset")
    
    def save(self, filepath: str) -> None:
        """
        Save agent state and conversation history.
        
        Args:
            filepath: Path to save file
        """
        import pickle
        
        save_data = {
            'config': self.config,
            'state': self.state,
            'conversation_history': self.conversation_history,
            'token_usage': self.token_tracker.get_summary()
        }
        
        with open(filepath, 'wb') as f:
            pickle.dump(save_data, f)
        
        self.logger.info(f"Agent saved to {filepath}")
    
    def load(self, filepath: str) -> None:
        """
        Load agent state from file.
        
        Args:
            filepath: Path to load from
        """
        import pickle
        
        with open(filepath, 'rb') as f:
            save_data = pickle.load(f)
        
        self.config = save_data['config']
        self.state = save_data['state']
        self.conversation_history = save_data['conversation_history']
        
        self.logger.info(f"Agent loaded from {filepath}")
