"""
Base Agent Module
=================

This module defines the BaseAgent abstract class that serves as the foundation
for all agent types in the system.

Purpose:
--------
- Provides a common interface for all agents
- Defines core agent lifecycle methods
- Implements shared functionality across agent types

Usage:
------
    from agents.base_agent import BaseAgent
    
    class MyAgent(BaseAgent):
        def act(self, observation):
            # Implement custom behavior
            return action
            
        def learn(self, experience):
            # Implement learning logic
            pass

Key Methods:
-----------
- initialize(): Setup agent state and resources
- act(observation): Decide on action given observation
- learn(experience): Update agent based on experience
- reset(): Reset agent to initial state
- save(path): Save agent state to disk
- load(path): Load agent state from disk
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
import logging


class BaseAgent(ABC):
    """
    Abstract base class for all agents in the Agentic AI system.
    
    All agent implementations should inherit from this class and implement
    the required abstract methods.
    """
    
    def __init__(self, config: Dict[str, Any], name: Optional[str] = None):
        """
        Initialize the base agent.
        
        Args:
            config (Dict): Configuration dictionary for the agent
            name (str, optional): Name identifier for the agent
        """
        self.config = config
        self.name = name or self.__class__.__name__
        self.logger = logging.getLogger(f"agents.{self.name}")
        self.initialized = False
        self.step_count = 0
        
    def initialize(self):
        """
        Initialize the agent's state and resources.
        
        This method should be called before the agent starts operating.
        Override this method to add custom initialization logic.
        """
        self.logger.info(f"Initializing agent: {self.name}")
        self.initialized = True
        self.step_count = 0
        
    @abstractmethod
    def act(self, observation: Any) -> Any:
        """
        Decide on an action given the current observation.
        
        Args:
            observation: Current state observation from the environment
            
        Returns:
            action: Action to take in the environment
            
        Note:
            This is an abstract method that must be implemented by subclasses.
        """
        pass
    
    @abstractmethod
    def learn(self, experience: Dict[str, Any]):
        """
        Update the agent based on experience.
        
        Args:
            experience (Dict): Dictionary containing:
                - state: Previous state
                - action: Action taken
                - reward: Reward received
                - next_state: Resulting state
                - done: Whether episode ended
                
        Note:
            This is an abstract method that must be implemented by subclasses.
        """
        pass
    
    def reset(self):
        """
        Reset the agent to its initial state.
        
        Useful for starting new episodes or experiments.
        """
        self.logger.info(f"Resetting agent: {self.name}")
        self.step_count = 0
        
    def save(self, path: str):
        """
        Save the agent's state to disk.
        
        Args:
            path (str): File path where agent state will be saved
        """
        self.logger.info(f"Saving agent state to: {path}")
        # Implement serialization logic in subclasses
        
    def load(self, path: str):
        """
        Load the agent's state from disk.
        
        Args:
            path (str): File path from which to load agent state
        """
        self.logger.info(f"Loading agent state from: {path}")
        # Implement deserialization logic in subclasses
        
    def get_stats(self) -> Dict[str, Any]:
        """
        Get current agent statistics.
        
        Returns:
            Dict containing agent performance metrics and state information
        """
        return {
            'name': self.name,
            'initialized': self.initialized,
            'step_count': self.step_count
        }
    
    def __repr__(self) -> str:
        """String representation of the agent."""
        return f"{self.__class__.__name__}(name='{self.name}', steps={self.step_count})"
