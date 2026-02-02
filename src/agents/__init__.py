"""
Agents Package
==============

This package contains all agent implementations for the Agentic AI system.

Agent Types:
-----------
1. BaseAgent: Abstract base class defining the core agent interface
2. AutonomousAgent: Self-directed agent with autonomous decision-making
3. LearningAgent: Agent with reinforcement learning capabilities
4. ReasoningAgent: Agent with advanced reasoning and planning abilities
5. CollaborativeAgent: Agent designed for multi-agent collaboration

Usage:
------
    from agents import AutonomousAgent
    
    agent = AutonomousAgent(config)
    agent.initialize()
    action = agent.act(observation)
    agent.learn(experience)

Best Practices:
--------------
- Always initialize agents before use
- Handle agent lifecycle properly (initialize -> act -> learn -> cleanup)
- Use appropriate agent type for your task
- Configure agents using YAML configuration files
"""

from .base_agent import BaseAgent
from .autonomous_agent import AutonomousAgent
from .learning_agent import LearningAgent
from .reasoning_agent import ReasoningAgent
from .collaborative_agent import CollaborativeAgent

try:
    from .llm_agent import LLMAgent
    __all__ = [
        'BaseAgent',
        'AutonomousAgent',
        'LearningAgent',
        'ReasoningAgent',
        'CollaborativeAgent',
        'LLMAgent'
    ]
except ImportError:
    __all__ = [
        'BaseAgent',
        'AutonomousAgent',
        'LearningAgent',
        'ReasoningAgent',
        'CollaborativeAgent'
    ]
