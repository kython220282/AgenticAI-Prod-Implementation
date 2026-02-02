"""
LLM Agent Example

Demonstrates how to use LLM-powered agents with:
- LangChain integration
- Prompt templates
- Vector memory
- Token tracking

Usage:
    python examples/llm_agent_example.py
"""

import sys
sys.path.insert(0, 'src')

import os
from agents.llm_agent import LLMAgent
from utils.prompt_manager import PromptManager
from utils.token_tracker import TokenTracker
from utils.vector_store import VectorStoreManager

def main():
    """Run LLM agent example."""
    print("=" * 60)
    print("LLM Agent Example")
    print("=" * 60)
    
    # Set OpenAI API key (required)
    # Make sure to set OPENAI_API_KEY environment variable
    if not os.getenv('OPENAI_API_KEY'):
        print("\n⚠️  Warning: OPENAI_API_KEY not set")
        print("This example requires an OpenAI API key.")
        print("Set it with: export OPENAI_API_KEY='your-key-here'")
        print("\nUsing mock mode for demonstration...")
        return
    
    # Configure LLM agent
    config = {
        'llm_provider': 'openai',
        'model': 'gpt-4-turbo-preview',
        'temperature': 0.7,
        'max_tokens': 500,
        'use_vector_memory': True,
        'system_prompt': 'reasoning'
    }
    
    # Create agent
    print("\n1. Initializing LLM Agent...")
    agent = LLMAgent(config, name="AssistantAgent")
    agent.initialize()
    print("✓ Agent initialized")
    
    # Example 1: Simple interaction
    print("\n2. Simple Interaction:")
    print("-" * 60)
    query1 = "What are the key principles of building an agentic AI system?"
    print(f"User: {query1}")
    response1 = agent.act(query1)
    print(f"Agent: {response1}")
    
    # Example 2: Follow-up with memory
    print("\n3. Follow-up Question (with memory):")
    print("-" * 60)
    query2 = "Can you elaborate on the first principle you mentioned?"
    print(f"User: {query2}")
    response2 = agent.act(query2)
    print(f"Agent: {response2}")
    
    # Example 3: Using prompt templates
    print("\n4. Using Prompt Templates:")
    print("-" * 60)
    pm = PromptManager()
    
    # Create a planning task
    planning_prompt = pm.render_template(
        'task_planning',
        {
            'task': 'Build a multi-agent system for customer support',
            'constraints': [
                'Must handle 1000+ concurrent users',
                'Response time < 2 seconds',
                'Support multiple languages'
            ]
        }
    )
    
    print(f"Planning Task:\n{planning_prompt[:200]}...")
    response3 = agent.act(planning_prompt)
    print(f"\nAgent Plan:\n{response3}")
    
    # Example 4: Token tracking
    print("\n5. Token Usage Statistics:")
    print("-" * 60)
    stats = agent.get_stats()
    token_usage = stats['token_usage']
    print(f"Total Tokens: {token_usage['total_tokens']:,}")
    print(f"Total Cost: ${token_usage['total_cost']:.6f}")
    print(f"Requests: {token_usage['total_records']}")
    print(f"Avg Tokens/Request: {token_usage['average_tokens_per_request']:.2f}")
    
    # Example 5: Vector memory retrieval
    print("\n6. Testing Vector Memory:")
    print("-" * 60)
    
    # Add some information to memory
    agent.vector_memory.add_memory(
        "The agent uses a modular architecture with separate components for perception, reasoning, and action.",
        metadata={'type': 'architecture', 'importance': 'high'}
    )
    agent.vector_memory.add_memory(
        "Performance metrics should be tracked for each agent interaction.",
        metadata={'type': 'best_practice'}
    )
    
    # Retrieve related memories
    query3 = "How should I structure my agent?"
    similar_memories = agent.vector_memory.retrieve_similar(query3, k=2)
    
    print(f"Query: {query3}")
    print("\nRelevant Memories:")
    for i, mem in enumerate(similar_memories, 1):
        print(f"\n{i}. {mem['text']}")
        print(f"   Similarity Score: {mem['score']:.4f}")
        print(f"   Metadata: {mem['metadata']}")
    
    # Example 6: Generate detailed report
    print("\n7. Token Usage Report:")
    print("-" * 60)
    tracker = agent.token_tracker
    report = tracker.generate_report(period='day')
    print(report)
    
    # Example 7: Few-shot prompting
    print("\n8. Few-Shot Learning Example:")
    print("-" * 60)
    
    few_shot_prompt = pm.create_few_shot_prompt(
        instruction="Extract key information from the text",
        examples=[
            {
                'input': "The agent processed 100 requests in 5 seconds.",
                'output': "{'metric': 'throughput', 'value': 20, 'unit': 'requests/second'}",
                'explanation': "Calculated requests per second"
            },
            {
                'input': "Memory usage increased to 2.5 GB during peak load.",
                'output': "{'metric': 'memory', 'value': 2.5, 'unit': 'GB', 'condition': 'peak'}",
                'explanation': "Extracted memory metric with context"
            }
        ],
        input_text="The system handled 500 concurrent users with 95% success rate."
    )
    
    print("Few-shot prompt created")
    response4 = agent.act(few_shot_prompt)
    print(f"Agent: {response4}")
    
    # Final statistics
    print("\n" + "=" * 60)
    print("Final Agent Statistics:")
    print("=" * 60)
    final_stats = agent.get_stats()
    print(f"Agent: {final_stats['name']}")
    print(f"Status: {final_stats['status']}")
    print(f"Model: {final_stats['model']}")
    print(f"Conversations: {final_stats['conversations']}")
    print(f"Vector Memory Size: {final_stats.get('vector_memory_size', 0)}")
    print(f"Total Cost: ${final_stats['token_usage']['total_cost']:.6f}")
    
    print("\n✓ Example completed successfully!")

if __name__ == "__main__":
    main()
