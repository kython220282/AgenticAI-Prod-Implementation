"""
Environment Package
===================

This package contains environment and simulation implementations for agent training.

Modules:
-------
- base_env.py: Base environment class defining the interface
- simulator.py: Simulation environment for multi-agent scenarios

Usage:
------
    from environment import BaseEnvironment, Simulator
    
    env = Simulator(config)
    env.reset()
    
    obs, reward, done, info = env.step(action)
"""

from .base_env import BaseEnvironment
from .simulator import Simulator

__all__ = ['BaseEnvironment', 'Simulator']
