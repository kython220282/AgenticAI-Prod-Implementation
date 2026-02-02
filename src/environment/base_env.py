"""
Base Environment Module
=======================

This module defines the base environment interface for agent interaction,
following the OpenAI Gym API standard.

Purpose:
--------
- Provide standardized environment interface
- Define state/action spaces
- Handle environment dynamics
- Support episode management

Usage:
------
    from environment import BaseEnvironment
    
    class MyEnvironment(BaseEnvironment):
        def step(self, action):
            # Implement environment dynamics
            return observation, reward, done, info
        
        def reset(self):
            # Reset environment to initial state
            return initial_observation
    
    env = MyEnvironment(config)
    obs = env.reset()
    
    for _ in range(100):
        action = agent.act(obs)
        obs, reward, done, info = env.step(action)
        if done:
            break

Key Features:
------------
- Gym-compatible interface
- Configurable state and action spaces
- Episode management
- Rendering support
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Tuple, Optional
import logging
import numpy as np


class BaseEnvironment(ABC):
    """
    Base environment class for agent interaction.
    
    Follows the OpenAI Gym API for compatibility with standard RL libraries.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the base environment.
        
        Args:
            config (Dict): Environment configuration
        """
        self.config = config
        self.logger = logging.getLogger('environment.BaseEnvironment')
        
        # Episode tracking
        self.episode_count = 0
        self.step_count = 0
        self.episode_reward = 0.0
        self.done = False
        
        # State and action spaces (to be defined by subclasses)
        self.observation_space = None
        self.action_space = None
        
        # Rendering
        self.render_mode = config.get('render_mode', None)
        
        self.logger.info("Base environment initialized")
    
    @abstractmethod
    def step(self, action: Any) -> Tuple[Any, float, bool, Dict]:
        """
        Execute one timestep of the environment's dynamics.
        
        Args:
            action: Action to execute
            
        Returns:
            Tuple of (observation, reward, done, info):
                - observation: Agent's observation of the current environment
                - reward (float): Reward from the action
                - done (bool): Whether the episode has ended
                - info (Dict): Additional information
        """
        pass
    
    @abstractmethod
    def reset(self) -> Any:
        """
        Reset the environment to an initial state.
        
        Returns:
            observation: Initial observation
        """
        pass
    
    def render(self, mode: str = 'human'):
        """
        Render the environment.
        
        Args:
            mode (str): Rendering mode ('human', 'rgb_array', etc.)
        """
        # Override in subclasses to implement rendering
        pass
    
    def close(self):
        """Clean up environment resources."""
        self.logger.info("Environment closed")
    
    def seed(self, seed: Optional[int] = None):
        """
        Set the random seed for reproducibility.
        
        Args:
            seed (int, optional): Random seed
        """
        if seed is not None:
            np.random.seed(seed)
            self.logger.info(f"Random seed set to {seed}")
    
    def get_state(self) -> Dict[str, Any]:
        """
        Get the current environment state.
        
        Returns:
            Dict: Current state dictionary
        """
        return {
            'episode_count': self.episode_count,
            'step_count': self.step_count,
            'episode_reward': self.episode_reward,
            'done': self.done
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Get environment statistics.
        
        Returns:
            Dict: Statistics dictionary
        """
        return {
            'episode_count': self.episode_count,
            'total_steps': self.step_count,
            'average_episode_length': self.step_count / max(1, self.episode_count),
            'current_episode_reward': self.episode_reward
        }
    
    def __repr__(self) -> str:
        """String representation of environment."""
        return (f"{self.__class__.__name__}("
                f"episodes={self.episode_count}, "
                f"steps={self.step_count})")
