"""
Test Agents Module
==================

Unit tests for agent implementations.

Usage:
    python -m pytest tests/test_agents.py
"""

import sys
sys.path.insert(0, 'src')

import pytest
import numpy as np
from agents import BaseAgent, AutonomousAgent, LearningAgent, ReasoningAgent, CollaborativeAgent


class TestBaseAgent:
    """Test cases for BaseAgent."""
    
    def test_initialization(self):
        """Test agent initialization."""
        config = {'test_param': 'value'}
        
        # BaseAgent is abstract, create a simple implementation
        class SimpleAgent(BaseAgent):
            def act(self, observation):
                return 0
            
            def learn(self, experience):
                pass
        
        agent = SimpleAgent(config, name="test_agent")
        
        assert agent.name == "test_agent"
        assert agent.config == config
        assert not agent.initialized
        assert agent.step_count == 0
    
    def test_initialize(self):
        """Test agent initialization method."""
        class SimpleAgent(BaseAgent):
            def act(self, observation):
                return 0
            
            def learn(self, experience):
                pass
        
        agent = SimpleAgent({})
        agent.initialize()
        
        assert agent.initialized
        assert agent.step_count == 0
    
    def test_reset(self):
        """Test agent reset functionality."""
        class SimpleAgent(BaseAgent):
            def act(self, observation):
                return 0
            
            def learn(self, experience):
                pass
        
        agent = SimpleAgent({})
        agent.initialize()
        agent.step_count = 100
        
        agent.reset()
        
        assert agent.step_count == 0


class TestAutonomousAgent:
    """Test cases for AutonomousAgent."""
    
    def test_initialization(self):
        """Test autonomous agent initialization."""
        config = {
            'autonomy_level': 0.8,
            'decision_threshold': 0.7,
            'exploration_rate': 0.2
        }
        
        agent = AutonomousAgent(config)
        agent.initialize()
        
        assert agent.autonomy_level == 0.8
        assert agent.decision_threshold == 0.7
        assert agent.exploration_rate == 0.2
        assert agent.initialized
    
    def test_act(self):
        """Test autonomous agent action selection."""
        config = {'exploration_rate': 0.0}  # No exploration for predictable test
        agent = AutonomousAgent(config)
        agent.initialize()
        
        observation = np.array([1.0, 2.0, 3.0])
        action = agent.act(observation)
        
        assert action is not None
        assert agent.step_count == 1


class TestLearningAgent:
    """Test cases for LearningAgent."""
    
    def test_initialization(self):
        """Test learning agent initialization."""
        config = {
            'learning_rate': 0.001,
            'discount_factor': 0.95,
            'batch_size': 32
        }
        
        agent = LearningAgent(config)
        agent.initialize()
        
        assert agent.learning_rate == 0.001
        assert agent.discount_factor == 0.95
        assert agent.batch_size == 32
        assert len(agent.memory) == 0
    
    def test_memory_storage(self):
        """Test experience storage in memory."""
        config = {'memory_size': 100}
        agent = LearningAgent(config)
        agent.initialize()
        
        experience = {
            'state': [1, 2, 3],
            'action': 0,
            'reward': 1.0,
            'next_state': [2, 3, 4],
            'done': False
        }
        
        agent.learn(experience)
        
        assert len(agent.memory) == 1


class TestReasoningAgent:
    """Test cases for ReasoningAgent."""
    
    def test_initialization(self):
        """Test reasoning agent initialization."""
        config = {
            'reasoning_depth': 5,
            'inference_engine': 'forward_chaining'
        }
        
        agent = ReasoningAgent(config)
        agent.initialize()
        
        assert agent.reasoning_depth == 5
        assert agent.inference_engine == 'forward_chaining'
        assert len(agent.facts) == 0
        assert len(agent.rules) == 0
    
    def test_add_fact(self):
        """Test adding facts to knowledge base."""
        agent = ReasoningAgent({})
        agent.initialize()
        
        agent.add_fact("test_fact", 1.0)
        
        assert "test_fact" in agent.facts


class TestCollaborativeAgent:
    """Test cases for CollaborativeAgent."""
    
    def test_initialization(self):
        """Test collaborative agent initialization."""
        config = {
            'team_size': 5,
            'communication_protocol': 'message_passing'
        }
        
        agent = CollaborativeAgent(config)
        agent.initialize()
        
        assert agent.team_size == 5
        assert agent.communication_protocol == 'message_passing'
        assert len(agent.inbox) == 0
    
    def test_communication(self):
        """Test agent communication."""
        config = {'team_size': 2}
        
        agent1 = CollaborativeAgent(config, name="agent1")
        agent2 = CollaborativeAgent(config, name="agent2")
        
        agent1.initialize()
        agent2.initialize()
        
        agent1.set_team([agent2])
        
        # Send message
        agent1.communicate('test_message', 'Hello!', [agent2])
        agent1._send_pending_messages()
        
        assert len(agent2.inbox) == 1


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
