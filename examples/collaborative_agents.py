"""
Collaborative Agents Example
============================

This example demonstrates advanced collaboration between reasoning agents.

Usage:
    python examples/collaborative_agents.py
"""

import sys
sys.path.insert(0, 'src')

from agents import ReasoningAgent, CollaborativeAgent
from core import Memory, Planner
from environment import Simulator
from utils import setup_logger


def main():
    """Run collaborative agents example with reasoning."""
    
    # Setup logging
    logger = setup_logger('collaborative_example', level='INFO')
    logger.info("Starting Collaborative Agents with Reasoning Example")
    
    # Initialize environment
    env_config = {
        'num_agents': 2,
        'state_dim': 6,
        'action_dim': 4,
        'max_steps': 100
    }
    
    env = Simulator(env_config)
    
    # Initialize reasoning agent
    reasoning_config = {
        'reasoning_depth': 5,
        'inference_engine': 'forward_chaining',
        'confidence_threshold': 0.75
    }
    
    reasoning_agent = ReasoningAgent(reasoning_config, name="Reasoner")
    reasoning_agent.initialize()
    
    # Add some knowledge
    reasoning_agent.add_fact("goal_location", "north")
    reasoning_agent.add_fact("current_location", "south")
    
    # Add rule: if at goal, task is complete
    reasoning_agent.add_rule(
        premises=[("current_location", "north")],
        conclusion=("task", "complete")
    )
    
    logger.info("Reasoning agent configured with knowledge base")
    
    # Initialize collaborative agents
    collab_config = {
        'team_size': 2,
        'communication_protocol': 'message_passing',
        'coordination_strategy': 'distributed'
    }
    
    agents = []
    for i in range(2):
        agent = CollaborativeAgent(collab_config, name=f"Collaborator_{i}")
        agent.initialize()
        agents.append(agent)
    
    # Set up team
    for agent in agents:
        agent.set_team(agents)
    
    logger.info("Collaborative team initialized")
    
    # Demonstration scenario
    num_steps = 10
    observations = env.reset()
    
    logger.info("\n=== Running Collaborative Scenario ===")
    
    for step in range(num_steps):
        logger.info(f"\nStep {step + 1}/{num_steps}")
        
        # Reasoning agent analyzes situation
        if step % 3 == 0:
            # Perform reasoning
            reasoning_agent.add_fact("step", str(step))
            derived_facts = reasoning_agent._forward_chaining()
            
            if derived_facts:
                logger.info(f"Reasoning agent derived: {derived_facts}")
                
                # Share knowledge with team
                knowledge = {
                    'derived_facts': derived_facts,
                    'step': step
                }
                agents[0].share_knowledge(knowledge)
        
        # Collaborative agents act
        actions = []
        for i, agent in enumerate(agents):
            # Process any messages
            agent._process_messages()
            
            # Select action
            action = agent.act(observations[i])
            actions.append(action)
            
            logger.info(f"  {agent.name}: action={action}")
        
        # Execute actions
        observations, rewards, dones, info = env.step(actions)
        
        # Agents communicate
        if step % 2 == 0:
            agents[0].communicate(
                'coordination',
                {'action': actions[0], 'reward': rewards[0]},
                [agents[1]]
            )
            agents[0]._send_pending_messages()
            logger.info("  Agents exchanged coordination messages")
        
        if all(dones):
            logger.info("All agents completed their tasks!")
            break
    
    # Final statistics
    logger.info("\n=== Scenario Complete ===")
    logger.info(f"Reasoning agent facts: {len(reasoning_agent.facts)}")
    logger.info(f"Reasoning agent derived facts: {len(reasoning_agent.derived_facts)}")
    
    for agent in agents:
        stats = agent.get_stats()
        logger.info(f"{agent.name} - Shared knowledge: {stats['shared_knowledge_items']} items")


if __name__ == '__main__':
    main()
