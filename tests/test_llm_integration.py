"""
Test LLM Agent functionality

This module tests LLM-powered agents including:
- Agent initialization
- LLM interaction
- Vector memory integration
- Token tracking
- Prompt management
"""

import pytest
import sys
import os
sys.path.insert(0, 'src')

from agents.llm_agent import LLMAgent
from utils.prompt_manager import PromptManager
from utils.token_tracker import TokenTracker
from utils.vector_store import VectorStoreManager


@pytest.fixture
def llm_config():
    """LLM agent configuration."""
    return {
        'llm_provider': 'openai',
        'model': 'gpt-4-turbo-preview',
        'temperature': 0.7,
        'max_tokens': 500,
        'use_vector_memory': False,  # Disable for testing
        'system_prompt': 'default'
    }


@pytest.fixture
def prompt_manager():
    """Create prompt manager."""
    return PromptManager()


@pytest.fixture
def token_tracker():
    """Create token tracker."""
    return TokenTracker(agent_name="test_agent")


def test_llm_agent_creation(llm_config):
    """Test LLM agent can be created."""
    agent = LLMAgent(llm_config, name="TestAgent")
    assert agent.name == "TestAgent"
    assert agent.model == "gpt-4-turbo-preview"
    assert agent.temperature == 0.7


def test_llm_agent_initialization():
    """Test agent initialization (without actual API call)."""
    config = {
        'llm_provider': 'openai',
        'model': 'gpt-4-turbo-preview',
        'use_vector_memory': False
    }
    
    agent = LLMAgent(config)
    # Note: Full initialization requires API key
    assert agent is not None


def test_prompt_manager_initialization(prompt_manager):
    """Test prompt manager initializes correctly."""
    assert prompt_manager is not None
    assert prompt_manager.template_dir.exists()


def test_system_prompts(prompt_manager):
    """Test system prompt retrieval."""
    default = prompt_manager.get_system_prompt('default')
    reasoning = prompt_manager.get_system_prompt('reasoning')
    
    assert len(default) > 0
    assert len(reasoning) > 0
    assert default != reasoning


def test_prompt_template_listing(prompt_manager):
    """Test listing available templates."""
    templates = prompt_manager.list_templates()
    assert isinstance(templates, list)
    # Should have default templates
    assert len(templates) > 0


def test_few_shot_prompt(prompt_manager):
    """Test few-shot prompt creation."""
    examples = [
        {
            'input': 'Test input 1',
            'output': 'Test output 1'
        },
        {
            'input': 'Test input 2',
            'output': 'Test output 2',
            'explanation': 'Test explanation'
        }
    ]
    
    prompt = prompt_manager.create_few_shot_prompt(
        instruction="Process the input",
        examples=examples,
        input_text="New input"
    )
    
    assert 'Process the input' in prompt
    assert 'Test input 1' in prompt
    assert 'New input' in prompt


def test_token_tracker_initialization(token_tracker):
    """Test token tracker initializes correctly."""
    assert token_tracker.agent_name == "test_agent"
    assert len(token_tracker.usage_data) == 0


def test_token_tracking(token_tracker):
    """Test token usage tracking."""
    record = token_tracker.track(
        prompt_tokens=100,
        completion_tokens=50,
        model='gpt-4-turbo-preview',
        task='test_task'
    )
    
    assert record['total_tokens'] == 150
    assert record['agent'] == 'test_agent'
    assert record['task'] == 'test_task'
    assert 'cost' in record
    assert record['cost'] > 0


def test_token_summary(token_tracker):
    """Test token usage summary generation."""
    # Add some usage data
    token_tracker.track(100, 50, 'gpt-4-turbo-preview')
    token_tracker.track(200, 100, 'gpt-4-turbo-preview')
    
    summary = token_tracker.get_summary()
    
    assert summary['total_tokens'] == 450
    assert summary['total_records'] == 2
    assert summary['prompt_tokens'] == 300
    assert summary['completion_tokens'] == 150
    assert 'total_cost' in summary


def test_token_report(token_tracker):
    """Test report generation."""
    token_tracker.track(100, 50, 'gpt-4-turbo-preview', task='task1')
    
    report = token_tracker.generate_report(period='all')
    
    assert 'Token Usage Report' in report
    assert 'test_agent' in report
    assert 'Total Tokens' in report


def test_vector_store_initialization():
    """Test vector store can be initialized."""
    # This test requires sentence-transformers
    try:
        store = VectorStoreManager(
            provider='faiss',
            collection_name='test_collection'
        )
        assert store.provider == 'faiss'
        assert store.collection_name == 'test_collection'
    except ImportError:
        pytest.skip("sentence-transformers not available")


def test_vector_memory_operations():
    """Test vector memory add and retrieve."""
    try:
        store = VectorStoreManager(provider='faiss')
        
        # Add memory
        doc_id = store.add_memory(
            "Test information",
            metadata={'type': 'test'}
        )
        
        assert doc_id is not None
        
        # Retrieve similar
        results = store.retrieve_similar("Test query", k=1)
        
        assert len(results) <= 1
        if len(results) > 0:
            assert 'text' in results[0]
            assert 'score' in results[0]
    
    except ImportError:
        pytest.skip("Required packages not available")


def test_cost_calculation():
    """Test token cost calculation for different models."""
    tracker = TokenTracker()
    
    # Test GPT-4
    record1 = tracker.track(1000, 500, 'gpt-4-turbo-preview')
    assert record1['cost'] > 0
    
    # Test GPT-3.5 (should be cheaper)
    record2 = tracker.track(1000, 500, 'gpt-3.5-turbo')
    assert record2['cost'] < record1['cost']


def test_template_rendering(prompt_manager):
    """Test template rendering with variables."""
    # Add a simple template
    prompt_manager.add_template(
        'test_template',
        'Hello {{ name }}, your task is: {{ task }}'
    )
    
    rendered = prompt_manager.render_template(
        'test_template',
        {'name': 'Agent', 'task': 'Test'}
    )
    
    assert 'Hello Agent' in rendered
    assert 'Test' in rendered


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
