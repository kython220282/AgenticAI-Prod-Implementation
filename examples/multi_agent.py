"""
Multi-Agent Example
====================

This example demonstrates multi-agent collaboration in a shared environment.

Usage:
    python examples/multi_agent.py
"""

import sys
sys.path.insert(0, 'src')

from agents import CollaborativeAgent
from environment import Simulator
from utils import setup_logger, MetricsTracker
from config import load_config


def main():
    """Run multi-agent example."""
    
    # Setup logging
    logger = setup_logger('multi_agent_example', level='INFO')
    logger.info("Starting Multi-Agent Example")
    
    # Configuration
    num_agents = 3
    num_episodes = 5
    
    # Initialize environment
    env_config = {
        'num_agents': num_agents,
        'state_dim': 8,
        'action_dim': 4,
        'max_steps': 500,
        'reward_type': 'sparse'
    }
    
    env = Simulator(env_config)
    logger.info(f"Environment created for {num_agents} agents")
    
    # Initialize agents
    agent_config = {
        'team_size': num_agents,
        'communication_protocol': 'message_passing',
        'coordination_strategy': 'hierarchical'
    }
    
    agents = []
    for i in range(num_agents):
        agent = CollaborativeAgent(agent_config, name=f"Agent_{i}")
        agent.initialize()
        agents.append(agent)
    
    # Set up team structure
    for agent in agents:
        agent.set_team(agents)
    
    # Assign roles
    agents[0].set_role('leader')
    for i in range(1, num_agents):
        agents[i].set_role('follower')
    
    logger.info(f"Initialized {num_agents} collaborative agents")
    
    # Initialize metrics
    metrics = MetricsTracker()
    
    # Training loop
    for episode in range(num_episodes):
        observations = env.reset()
        done = [False] * num_agents
        episode_rewards = [0] * num_agents
        steps = 0
        
        logger.info(f"\n=== Episode {episode + 1}/{num_episodes} ===")
        
        while not all(done):
            # Each agent selects an action
            actions = []
            for i, agent in enumerate(agents):
                action = agent.act(observations[i])
                actions.append(action)
            
            # Execute actions in environment
            next_observations, rewards, done, info = env.step(actions)
            
            # Agents learn from experience
            for i, agent in enumerate(agents):
                experience = {
                    'state': observations[i],
                    'action': actions[i],
                    'reward': rewards[i],
                    'next_state': next_observations[i],
                    'done': done[i]
                }
                agent.learn(experience)
                episode_rewards[i] += rewards[i]
            
            observations = next_observations
            steps += 1
        
        # Record metrics
        total_reward = sum(episode_rewards)
        metrics.record('total_reward', total_reward, episode=episode)
        metrics.record('episode_length', steps, episode=episode)
        
        for i, reward in enumerate(episode_rewards):
            metrics.record(f'agent_{i}_reward', reward, episode=episode)
        
        logger.info(f"Episode {episode + 1} completed:")
        logger.info(f"  Total team reward: {total_reward:.2f}")
        logger.info(f"  Individual rewards: {[f'{r:.2f}' for r in episode_rewards]}")
        logger.info(f"  Steps: {steps}")
    
    # Print final statistics
    logger.info("\n=== Training Complete ===")
    logger.info(f"Average team reward: {metrics.get_mean('total_reward'):.2f}")
    logger.info(f"Average episode length: {metrics.get_mean('episode_length'):.2f}")
    
    for i in range(num_agents):
        avg_reward = metrics.get_mean(f'agent_{i}_reward')
        logger.info(f"Agent {i} average reward: {avg_reward:.2f}")
    
    # Generate report
    print("\n" + metrics.generate_report(['total_reward', 'episode_length']))


if __name__ == '__main__':
    main()
