"""
Single Agent Example
====================

This example demonstrates how to set up and run a single autonomous agent
in a simulated environment.

Usage:
    python examples/single_agent.py
"""

import sys
sys.path.insert(0, 'src')

from agents import AutonomousAgent
from environment import Simulator
from utils import setup_logger, MetricsTracker, Visualizer
from config import load_config


def main():
    """Run single agent example."""
    
    # Setup logging
    logger = setup_logger('single_agent_example', level='INFO')
    logger.info("Starting Single Agent Example")
    
    # Load configurations
    try:
        agent_config = load_config('agent_config.yaml')
        env_config = load_config('environment_config.yaml')
    except FileNotFoundError:
        # Fallback to default config
        agent_config = {
            'autonomous': {
                'autonomy_level': 0.8,
                'decision_threshold': 0.7,
                'exploration_rate': 0.2
            }
        }
        env_config = {
            'simulation': {
                'max_steps': 1000
            }
        }
    
    # Initialize environment
    env_params = {
        'num_agents': 1,
        'state_dim': 10,
        'action_dim': 4,
        'max_steps': env_config.get('simulation', {}).get('max_steps', 1000),
        'reward_type': 'sparse'
    }
    
    env = Simulator(env_params)
    logger.info(f"Environment created: {env}")
    
    # Initialize agent
    agent_params = agent_config.get('autonomous', {
        'autonomy_level': 0.8,
        'exploration_rate': 0.2
    })
    
    agent = AutonomousAgent(agent_params, name="Agent_1")
    agent.initialize()
    logger.info(f"Agent initialized: {agent}")
    
    # Initialize metrics tracker
    metrics = MetricsTracker(window_size=100)
    
    # Training loop
    num_episodes = 10
    
    for episode in range(num_episodes):
        observation = env.reset()
        done = False
        episode_reward = 0
        steps = 0
        
        logger.info(f"\n=== Episode {episode + 1}/{num_episodes} ===")
        
        while not done:
            # Agent selects action
            action = agent.act(observation)
            
            # Execute action in environment
            next_observation, reward, done, info = env.step(action)
            
            # Agent learns from experience
            experience = {
                'state': observation,
                'action': action,
                'reward': reward,
                'next_state': next_observation,
                'done': done
            }
            agent.learn(experience)
            
            # Update metrics
            episode_reward += reward
            steps += 1
            
            observation = next_observation
        
        # Record episode metrics
        metrics.record('episode_reward', episode_reward, episode=episode)
        metrics.record('episode_length', steps, episode=episode)
        
        logger.info(f"Episode {episode + 1} completed:")
        logger.info(f"  Reward: {episode_reward:.2f}")
        logger.info(f"  Steps: {steps}")
        logger.info(f"  Agent stats: {agent.get_stats()}")
    
    # Print final statistics
    logger.info("\n=== Training Complete ===")
    logger.info(f"Average episode reward: {metrics.get_mean('episode_reward'):.2f}")
    logger.info(f"Average episode length: {metrics.get_mean('episode_length'):.2f}")
    logger.info(f"Best episode reward: {metrics.get_max('episode_reward'):.2f}")
    
    # Generate report
    print("\n" + metrics.generate_report())
    
    # Visualize results (if matplotlib available)
    viz = Visualizer()
    if viz.available:
        rewards = metrics.get_all('episode_reward')
        viz.plot_learning_curve(
            rewards,
            window=5,
            title="Single Agent Learning Curve",
            save_path="data/training/single_agent_learning_curve.png"
        )
        logger.info("Learning curve saved to data/training/")


if __name__ == '__main__':
    main()
