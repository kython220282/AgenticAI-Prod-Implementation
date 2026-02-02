"""
Simulator Module
================

This module implements a simulation environment for single and multi-agent scenarios.

Purpose:
--------
- Simulate agent interactions with environment
- Support multi-agent scenarios
- Provide configurable physics and dynamics
- Enable scenario testing and validation

Usage:
------
    from environment import Simulator
    
    config = {
        'num_agents': 3,
        'max_steps': 1000,
        'state_dim': 10,
        'action_dim': 4
    }
    
    sim = Simulator(config)
    obs = sim.reset()
    
    # Single agent
    action = agent.act(obs)
    next_obs, reward, done, info = sim.step(action)
    
    # Multi-agent
    actions = [agent.act(obs[i]) for i, agent in enumerate(agents)]
    observations, rewards, dones, info = sim.step(actions)

Key Features:
------------
- Single and multi-agent support
- Configurable state/action spaces
- Customizable reward functions
- Physics simulation
- Collision detection
"""

from typing import Any, Dict, List, Tuple, Optional, Union
import numpy as np
from .base_env import BaseEnvironment


class Simulator(BaseEnvironment):
    """
    Simulation environment for agent training and testing.
    
    Supports both single-agent and multi-agent scenarios.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the simulator.
        
        Args:
            config (Dict): Simulator configuration including:
                - num_agents: Number of agents (1 for single-agent)
                - state_dim: Dimensionality of state space
                - action_dim: Dimensionality of action space
                - max_steps: Maximum steps per episode
                - reward_type: Reward structure ('sparse', 'dense')
        """
        super().__init__(config)
        
        self.num_agents = config.get('num_agents', 1)
        self.state_dim = config.get('state_dim', 10)
        self.action_dim = config.get('action_dim', 4)
        self.max_steps = config.get('max_steps', 1000)
        self.reward_type = config.get('reward_type', 'sparse')
        
        # Initialize state
        self.current_state = None
        self.agent_positions = None
        self.goals = None
        
        # Simulation parameters
        self.timestep = config.get('timestep', 0.1)
        self.collision_detection = config.get('collision_detection', True)
        
        self.logger.info(
            f"Simulator initialized - Agents: {self.num_agents}, "
            f"State dim: {self.state_dim}, Action dim: {self.action_dim}"
        )
    
    def reset(self) -> Union[np.ndarray, List[np.ndarray]]:
        """
        Reset the simulator to initial state.
        
        Returns:
            observation: Initial observation (array for single agent, 
                        list of arrays for multi-agent)
        """
        self.episode_count += 1
        self.step_count = 0
        self.episode_reward = 0.0
        self.done = False
        
        # Initialize random state
        if self.num_agents == 1:
            self.current_state = self._generate_random_state()
            observation = self.current_state
        else:
            self.current_state = [self._generate_random_state() 
                                 for _ in range(self.num_agents)]
            observation = self.current_state.copy()
        
        # Initialize agent positions (for spatial environments)
        self.agent_positions = np.random.uniform(
            -1.0, 1.0, size=(self.num_agents, 2)
        )
        
        # Initialize goals
        self.goals = np.random.uniform(
            -1.0, 1.0, size=(self.num_agents, 2)
        )
        
        self.logger.debug(f"Simulator reset - Episode {self.episode_count}")
        
        return observation
    
    def step(self, action: Union[Any, List[Any]]) -> Tuple[Any, Any, Any, Dict]:
        """
        Execute one simulation timestep.
        
        Args:
            action: Action to execute (single action or list for multi-agent)
            
        Returns:
            Tuple of (observation, reward, done, info):
                - observation: Next observation
                - reward: Reward(s) from the action(s)
                - done: Whether episode has ended (bool or list)
                - info: Additional information dictionary
        """
        if self.done:
            raise RuntimeError("Episode is done. Call reset() to start new episode.")
        
        self.step_count += 1
        
        # Handle single vs multi-agent
        if self.num_agents == 1:
            observation, reward, done, info = self._single_agent_step(action)
        else:
            observation, reward, done, info = self._multi_agent_step(action)
        
        # Update episode state
        self.done = done if isinstance(done, bool) else all(done)
        if isinstance(reward, (int, float)):
            self.episode_reward += reward
        else:
            self.episode_reward += sum(reward)
        
        # Check max steps
        if self.step_count >= self.max_steps:
            self.done = True
            if isinstance(done, list):
                done = [True] * len(done)
            else:
                done = True
        
        return observation, reward, done, info
    
    def _single_agent_step(self, action: Any) -> Tuple[np.ndarray, float, bool, Dict]:
        """
        Execute step for single agent.
        
        Args:
            action: Agent action
            
        Returns:
            Tuple of (observation, reward, done, info)
        """
        # Apply action to state
        if self.current_state is not None and not isinstance(self.current_state, list):
            self.current_state = self._apply_dynamics(self.current_state, action, 0)
        
        # Update agent position
        if self.agent_positions is not None:
            self.agent_positions[0] = self._update_position(
                self.agent_positions[0], action
            )
        
        # Calculate reward
        reward = self._calculate_reward(0)
        
        # Check if done
        done = self._check_done(0)
        
        # Additional info
        info = {
            'step': self.step_count,
            'distance_to_goal': self._distance_to_goal(0)
        }
        
        observation = self.current_state.copy()
        
        return observation, reward, done, info
    
    def _multi_agent_step(self, actions: List[Any]) -> Tuple[List[np.ndarray], List[float], List[bool], Dict]:
        """
        Execute step for multiple agents.
        
        Args:
            actions (List): List of agent actions
            
        Returns:
            Tuple of (observations, rewards, dones, info)
        """
        if len(actions) != self.num_agents:
            raise ValueError(f"Expected {self.num_agents} actions, got {len(actions)}")
        
        observations = []
        rewards = []
        dones = []
        
        # Update each agent
        for i, action in enumerate(actions):
            # Apply dynamics
            if self.current_state is not None and isinstance(self.current_state, list) and i < len(self.current_state):
                self.current_state[i] = self._apply_dynamics(
                    self.current_state[i], action, i
                )
            
            # Update position
            if self.agent_positions is not None and i < len(self.agent_positions):
                self.agent_positions[i] = self._update_position(
                    self.agent_positions[i], action
                )
            
            # Calculate reward
            reward = self._calculate_reward(i)
            rewards.append(reward)
            
            # Check done
            done = self._check_done(i)
            dones.append(done)
            
            # Observation
            if self.current_state is not None and isinstance(self.current_state, list) and i < len(self.current_state):
                observations.append(self.current_state[i].copy())
        
        # Check collisions
        if self.collision_detection:
            collisions = self._check_collisions()
            if collisions:
                self.logger.debug(f"Collisions detected: {collisions}")
        
        # Info
        info = {
            'step': self.step_count,
            'distances_to_goal': [self._distance_to_goal(i) for i in range(self.num_agents)],
            'collisions': collisions if self.collision_detection else []
        }
        
        return observations, rewards, dones, info
    
    def _generate_random_state(self) -> np.ndarray:
        """Generate random initial state."""
        return np.random.uniform(-1.0, 1.0, size=self.state_dim)
    
    def _apply_dynamics(self, state: np.ndarray, action: Any, agent_id: int) -> np.ndarray:
        """
        Apply environment dynamics to update state.
        
        Args:
            state (np.ndarray): Current state
            action: Action to apply
            agent_id (int): Agent identifier
            
        Returns:
            np.ndarray: Next state
        """
        # Simple dynamics: state += action * timestep
        # In practice, implement physics-based dynamics
        
        if isinstance(action, (int, np.integer)):
            # Discrete action - convert to one-hot
            action_vector = np.zeros(self.action_dim)
            action_vector[action] = 1.0
        else:
            action_vector = np.array(action)
        
        # Update state (simple linear dynamics)
        next_state = state + action_vector[:self.state_dim] * self.timestep
        
        # Clip to bounds
        next_state = np.clip(next_state, -1.0, 1.0)
        
        return next_state
    
    def _update_position(self, position: np.ndarray, action: Any) -> np.ndarray:
        """
        Update agent position based on action.
        
        Args:
            position (np.ndarray): Current position
            action: Action to apply
            
        Returns:
            np.ndarray: New position
        """
        # Simple movement: action affects x, y position
        movement = np.zeros(2)
        
        if isinstance(action, (int, np.integer)):
            # Discrete: 0=up, 1=down, 2=left, 3=right
            if action == 0:
                movement = np.array([0, 0.1])
            elif action == 1:
                movement = np.array([0, -0.1])
            elif action == 2:
                movement = np.array([-0.1, 0])
            elif action == 3:
                movement = np.array([0.1, 0])
        else:
            # Continuous action
            movement = np.array(action[:2]) * 0.1
        
        new_position = position + movement
        new_position = np.clip(new_position, -1.0, 1.0)
        
        return new_position
    
    def _calculate_reward(self, agent_id: int) -> float:
        """
        Calculate reward for agent.
        
        Args:
            agent_id (int): Agent identifier
            
        Returns:
            float: Reward value
        """
        if self.reward_type == 'sparse':
            # Sparse: reward only at goal
            distance = self._distance_to_goal(agent_id)
            if distance < 0.1:
                return 100.0  # Goal reached
            else:
                return -0.1  # Step penalty
        
        elif self.reward_type == 'dense':
            # Dense: reward based on distance to goal
            distance = self._distance_to_goal(agent_id)
            previous_distance = self._distance_to_goal(agent_id)  # Would need to track
            
            # Reward for getting closer
            reward = -distance  # Negative distance as reward
            return reward
        
        return 0.0
    
    def _distance_to_goal(self, agent_id: int) -> float:
        """
        Calculate distance from agent to its goal.
        
        Args:
            agent_id (int): Agent identifier
            
        Returns:
            float: Euclidean distance to goal
        """
        if self.agent_positions is None or self.goals is None:
            return 0.0
        agent_pos = self.agent_positions[agent_id]
        goal_pos = self.goals[agent_id]
        distance = np.linalg.norm(agent_pos - goal_pos)
        return float(distance)
    
    def _check_done(self, agent_id: int) -> bool:
        """
        Check if episode is done for agent.
        
        Args:
            agent_id (int): Agent identifier
            
        Returns:
            bool: True if episode should end
        """
        # Episode ends if goal reached
        distance = self._distance_to_goal(agent_id)
        return distance < 0.1
    
    def _check_collisions(self) -> List[Tuple[int, int]]:
        """
        Check for collisions between agents.
        
        Returns:
            List of (agent1_id, agent2_id) collision pairs
        """
        collisions = []
        collision_threshold = 0.15
        
        if self.agent_positions is None:
            return collisions
        
        for i in range(self.num_agents):
            for j in range(i + 1, self.num_agents):
                distance = np.linalg.norm(
                    self.agent_positions[i] - self.agent_positions[j]
                )
                
                if distance < collision_threshold:
                    collisions.append((i, j))
        
        return collisions
    
    def render(self, mode: str = 'human'):
        """
        Render the simulation.
        
        Args:
            mode (str): Render mode
        """
        if mode == 'human':
            # Simple text rendering
            print(f"\n=== Step {self.step_count} ===")
            if self.agent_positions is not None and self.goals is not None:
                for i in range(self.num_agents):
                    pos = self.agent_positions[i]
                    goal = self.goals[i]
                    dist = self._distance_to_goal(i)
                    print(f"Agent {i}: pos={pos}, goal={goal}, dist={dist:.3f}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get simulator statistics."""
        stats = super().get_stats()
        stats.update({
            'num_agents': self.num_agents,
            'state_dim': self.state_dim,
            'action_dim': self.action_dim,
            'max_steps': self.max_steps
        })
        return stats
