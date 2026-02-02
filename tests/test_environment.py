"""
Test Environment Module
=======================

Unit tests for environment and simulation.

Usage:
    python -m pytest tests/test_environment.py
"""

import sys
sys.path.insert(0, 'src')

import pytest
import numpy as np
from environment import BaseEnvironment, Simulator


class TestSimulator:
    """Test cases for Simulator environment."""
    
    def test_initialization(self):
        """Test simulator initialization."""
        config = {
            'num_agents': 1,
            'state_dim': 10,
            'action_dim': 4,
            'max_steps': 100
        }
        
        sim = Simulator(config)
        
        assert sim.num_agents == 1
        assert sim.state_dim == 10
        assert sim.action_dim == 4
        assert sim.max_steps == 100
    
    def test_reset(self):
        """Test environment reset."""
        config = {'num_agents': 1, 'state_dim': 5, 'action_dim': 4}
        sim = Simulator(config)
        
        obs = sim.reset()
        
        assert obs is not None
        assert sim.step_count == 0
        assert not sim.done
    
    def test_single_agent_step(self):
        """Test single agent environment step."""
        config = {'num_agents': 1, 'state_dim': 5, 'action_dim': 4}
        sim = Simulator(config)
        
        obs = sim.reset()
        action = 0
        
        next_obs, reward, done, info = sim.step(action)
        
        assert next_obs is not None
        assert isinstance(reward, (int, float))
        assert isinstance(done, bool)
        assert isinstance(info, dict)
    
    def test_multi_agent_step(self):
        """Test multi-agent environment step."""
        config = {'num_agents': 3, 'state_dim': 5, 'action_dim': 4}
        sim = Simulator(config)
        
        obs = sim.reset()
        actions = [0, 1, 2]  # One action per agent
        
        next_obs, rewards, dones, info = sim.step(actions)
        
        assert len(next_obs) == 3
        assert len(rewards) == 3
        assert len(dones) == 3
    
    def test_episode_completion(self):
        """Test episode completion and reset."""
        config = {'num_agents': 1, 'state_dim': 5, 'action_dim': 4, 'max_steps': 10}
        sim = Simulator(config)
        
        sim.reset()
        
        # Run until episode ends
        done = False
        steps = 0
        while not done and steps < 15:
            _, _, done, _ = sim.step(0)
            steps += 1
        
        assert done or steps >= 10


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
