"""
Reinforcement Learning Example
==============================

This example demonstrates reinforcement learning with a LearningAgent.

Usage:
    python examples/reinforcement_learning.py
"""

import sys
sys.path.insert(0, 'src')

from agents import LearningAgent
from environment import Simulator
from utils import setup_logger, MetricsTracker, Visualizer


def main():
    """Run reinforcement learning example."""
    
    # Setup logging
    logger = setup_logger('rl_example', level='INFO')
    logger.info("Starting Reinforcement Learning Example")
    
    # Initialize environment
    env_config = {
        'num_agents': 1,
        'state_dim': 8,
        'action_dim': 4,
        'max_steps': 200,
        'reward_type': 'dense'
    }
    
    env = Simulator(env_config)
    logger.info("Environment initialized")
    
    # Initialize learning agent
    agent_config = {
        'learning_rate': 0.001,
        'discount_factor': 0.95,
        'epsilon_start': 1.0,
        'epsilon_end': 0.01,
        'epsilon_decay': 0.995,
        'batch_size': 32,
        'memory_size': 10000
    }
    
    agent = LearningAgent(agent_config, name="RL_Agent")
    agent.initialize()
    logger.info(f"Learning agent initialized with ε={agent.epsilon:.3f}")
    
    # Initialize metrics
    metrics = MetricsTracker(window_size=100)
    
    # Training parameters
    num_episodes = 100
    
    logger.info(f"\nTraining for {num_episodes} episodes...")
    
    # Training loop
    for episode in range(num_episodes):
        observation = env.reset()
        done = False
        episode_reward = 0
        steps = 0
        
        while not done:
            # Agent selects action (epsilon-greedy)
            action = agent.act(observation)
            
            # Execute action
            next_observation, reward, done, info = env.step(action)
            
            # Store experience and learn
            experience = {
                'state': observation,
                'action': action,
                'reward': reward,
                'next_state': next_observation,
                'done': done
            }
            agent.learn(experience)
            
            episode_reward += reward
            steps += 1
            observation = next_observation
        
        # Record metrics
        metrics.record('episode_reward', episode_reward, episode=episode)
        metrics.record('episode_length', steps, episode=episode)
        metrics.record('epsilon', agent.epsilon, episode=episode)
        
        # Log progress every 10 episodes
        if (episode + 1) % 10 == 0:
            avg_reward = metrics.get_moving_average('episode_reward', window=10)
            logger.info(
                f"Episode {episode + 1}/{num_episodes} | "
                f"Avg Reward: {avg_reward:.2f} | "
                f"ε: {agent.epsilon:.3f} | "
                f"Memory: {len(agent.memory)}"
            )
    
    # Print final statistics
    logger.info("\n=== Training Complete ===")
    stats = agent.get_stats()
    logger.info(f"Episodes completed: {stats['episodes_completed']}")
    logger.info(f"Final epsilon: {stats['epsilon']:.3f}")
    logger.info(f"Memory size: {stats['memory_size']}")
    logger.info(f"Average reward (last 100): {metrics.get_moving_average('episode_reward', 100):.2f}")
    logger.info(f"Best episode reward: {metrics.get_max('episode_reward'):.2f}")
    
    # Visualize learning progress
    viz = Visualizer()
    if viz.available:
        rewards = metrics.get_all('episode_reward')
        epsilons = metrics.get_all('epsilon')
        
        # Plot learning curve
        viz.plot_learning_curve(
            rewards,
            window=20,
            title="Reinforcement Learning Progress",
            save_path="data/training/rl_learning_curve.png"
        )
        
        # Plot epsilon decay
        viz.plot_metrics(
            {'Exploration Rate (ε)': epsilons},
            title="Epsilon Decay",
            ylabel="Epsilon",
            save_path="data/training/rl_epsilon_decay.png"
        )
        
        logger.info("Visualizations saved to data/training/")


if __name__ == '__main__':
    main()
