"""
Test Reasoning Module
=====================

Unit tests for core reasoning components.

Usage:
    python -m pytest tests/test_reasoning.py
"""

import sys
sys.path.insert(0, 'src')

import pytest
from core import ReasoningEngine, Memory, Planner


class TestReasoningEngine:
    """Test cases for ReasoningEngine."""
    
    def test_initialization(self):
        """Test reasoning engine initialization."""
        engine = ReasoningEngine(method='forward_chaining')
        
        assert engine.method == 'forward_chaining'
        assert len(engine.facts) == 0
        assert len(engine.rules) == 0
    
    def test_add_fact(self):
        """Test adding facts."""
        engine = ReasoningEngine()
        
        engine.add_fact("sky", "blue", confidence=1.0)
        
        assert ("sky", "blue") in engine.facts
        assert engine.confidences[("sky", "blue")] == 1.0
    
    def test_add_rule(self):
        """Test adding inference rules."""
        engine = ReasoningEngine()
        
        premises = [("sky", "blue")]
        conclusion = ("weather", "clear")
        
        engine.add_rule(premises, conclusion, confidence=0.9)
        
        assert len(engine.rules) == 1
    
    def test_forward_chaining(self):
        """Test forward chaining inference."""
        engine = ReasoningEngine(method='forward_chaining')
        
        # Add facts
        engine.add_fact("sky", "blue")
        
        # Add rule: sky is blue -> weather is clear
        engine.add_rule(
            premises=[("sky", "blue")],
            conclusion=("weather", "clear")
        )
        
        # Perform inference
        derived = engine.infer()
        
        assert ("weather", "clear") in engine.facts


class TestMemory:
    """Test cases for Memory system."""
    
    def test_initialization(self):
        """Test memory initialization."""
        memory = Memory(capacity=100, memory_type='episodic')
        
        assert memory.capacity == 100
        assert memory.memory_type == 'episodic'
    
    def test_store_and_recall(self):
        """Test storing and recalling memories."""
        memory = Memory(capacity=100)
        
        # Store a memory
        item = {'state': [1, 2, 3], 'action': 0, 'reward': 1.0}
        memory.store(item)
        
        assert len(memory) == 1
        
        # Recall memory
        recalled = memory.recall(item, k=1)
        
        assert len(recalled) > 0


class TestPlanner:
    """Test cases for Planner."""
    
    def test_initialization(self):
        """Test planner initialization."""
        planner = Planner(algorithm='a_star')
        
        assert planner.algorithm == 'a_star'
        assert len(planner.actions) == 0
    
    def test_register_action(self):
        """Test action registration."""
        planner = Planner()
        
        def precondition(state):
            return True
        
        def effect(state):
            new_state = state.copy()
            new_state['done'] = True
            return new_state
        
        planner.register_action('test_action', precondition, effect, cost=1.0)
        
        assert len(planner.actions) == 1
    
    def test_simple_planning(self):
        """Test simple planning scenario."""
        planner = Planner(algorithm='bfs')
        
        # Define actions
        def move_precondition(state):
            return not state.get('at_goal', False)
        
        def move_effect(state):
            new_state = state.copy()
            new_state['at_goal'] = True
            return new_state
        
        planner.register_action('move_to_goal', move_precondition, move_effect)
        
        # Create plan
        initial = {'at_goal': False}
        goal = {'at_goal': True}
        
        plan = planner.create_plan(initial, goal)
        
        assert len(plan) > 0


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
