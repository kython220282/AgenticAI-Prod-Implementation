"""
Prompt Template Management System

This module provides a comprehensive system for managing, versioning,
and rendering prompt templates for LLM agents.

Features:
- Template loading and rendering
- Variable substitution
- Template versioning
- Few-shot examples
- Template validation

Usage:
    manager = PromptManager()
    prompt = manager.render_template(
        'reasoning_task',
        variables={'task': 'Solve this problem', 'context': 'Given data...'}
    )
"""

import os
import json
import yaml
from typing import Dict, List, Any, Optional
from pathlib import Path
from jinja2 import Template, Environment, FileSystemLoader
import logging


class PromptManager:
    """
    Manages prompt templates for LLM agents.
    
    Provides loading, rendering, and versioning of prompt templates
    with support for Jinja2 templating and few-shot examples.
    
    Attributes:
        template_dir: Directory containing template files
        templates: Loaded templates cache
        system_prompts: System-level prompts
    """
    
    def __init__(self, template_dir: Optional[str] = None):
        """
        Initialize Prompt Manager.
        
        Args:
            template_dir: Path to template directory (optional)
        """
        self.logger = logging.getLogger(__name__)
        
        # Set template directory
        if template_dir is None:
            template_dir = os.path.join(os.path.dirname(__file__), '../../config/prompts')
        
        self.template_dir = Path(template_dir)
        self.template_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_dir)),
            trim_blocks=True,
            lstrip_blocks=True
        )
        
        # Template cache
        self.templates: Dict[str, Template] = {}
        
        # System prompts
        self.system_prompts = self._load_system_prompts()
        
        # Create default templates if they don't exist
        self._create_default_templates()
        
        self.logger.info(f"Prompt Manager initialized with template dir: {self.template_dir}")
    
    def _load_system_prompts(self) -> Dict[str, str]:
        """Load system prompts from configuration."""
        system_prompts = {
            'default': "You are a helpful AI assistant with reasoning capabilities.",
            'reasoning': "You are an AI agent with advanced reasoning and planning abilities. Think step by step and explain your reasoning.",
            'collaborative': "You are part of a team of AI agents. Coordinate with others to achieve shared goals.",
            'analytical': "You are an analytical AI that breaks down complex problems into manageable steps.",
            'creative': "You are a creative AI that generates innovative solutions and ideas."
        }
        
        # Try to load from config file
        config_path = self.template_dir.parent / 'llm_config.yaml'
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    if 'prompts' in config and 'system_prompts' in config['prompts']:
                        system_prompts.update(config['prompts']['system_prompts'])
            except Exception as e:
                self.logger.warning(f"Could not load system prompts from config: {e}")
        
        return system_prompts
    
    def _create_default_templates(self) -> None:
        """Create default prompt templates if they don't exist."""
        default_templates = {
            'task_planning.txt': '''Given the following task, create a step-by-step plan to accomplish it.

Task: {{ task }}

{% if context %}
Context: {{ context }}
{% endif %}

{% if constraints %}
Constraints:
{% for constraint in constraints %}
- {{ constraint }}
{% endfor %}
{% endif %}

Please provide:
1. A breakdown of the task into subtasks
2. The order in which subtasks should be executed
3. Any dependencies between subtasks
4. Estimated complexity for each subtask

Plan:''',
            
            'reasoning_chain.txt': '''Analyze the following situation and provide step-by-step reasoning.

Situation: {{ situation }}

{% if facts %}
Known Facts:
{% for fact in facts %}
- {{ fact }}
{% endfor %}
{% endif %}

Think through this step by step:
1. What are the key elements of this situation?
2. What are the potential implications?
3. What reasoning approach should be used?
4. What conclusion can be drawn?

Reasoning:''',
            
            'decision_making.txt': '''You need to make a decision based on the following information.

Decision Required: {{ decision }}

{% if options %}
Available Options:
{% for option in options %}
{{ loop.index }}. {{ option }}
{% endfor %}
{% endif %}

{% if criteria %}
Decision Criteria:
{% for criterion in criteria %}
- {{ criterion }}
{% endfor %}
{% endif %}

Analyze each option, weigh the criteria, and make a recommendation with justification.

Analysis:''',
            
            'collaborative_task.txt': '''You are working with other agents on a collaborative task.

Task: {{ task }}

Your Role: {{ role }}

{% if other_agents %}
Other Agents:
{% for agent in other_agents %}
- {{ agent.name }}: {{ agent.role }}
{% endfor %}
{% endif %}

{% if shared_context %}
Shared Context: {{ shared_context }}
{% endif %}

Consider how to best contribute to the team effort and coordinate with other agents.

Your Action:''',
            
            'few_shot_example.txt': '''{{ instruction }}

{% if examples %}
Examples:
{% for example in examples %}

Input: {{ example.input }}
Output: {{ example.output }}
{% if example.explanation %}
Explanation: {{ example.explanation }}
{% endif %}
{% endfor %}
{% endif %}

Now apply the same approach:

Input: {{ input }}
Output:'''
        }
        
        for filename, content in default_templates.items():
            filepath = self.template_dir / filename
            if not filepath.exists():
                with open(filepath, 'w') as f:
                    f.write(content)
                self.logger.info(f"Created default template: {filename}")
    
    def get_system_prompt(self, key: str = 'default') -> str:
        """
        Get a system prompt by key.
        
        Args:
            key: System prompt identifier
            
        Returns:
            System prompt text
        """
        return self.system_prompts.get(key, self.system_prompts['default'])
    
    def load_template(self, template_name: str) -> Template:
        """
        Load a template by name.
        
        Args:
            template_name: Name of template file (with or without .txt extension)
            
        Returns:
            Jinja2 Template object
        """
        if not template_name.endswith('.txt'):
            template_name += '.txt'
        
        if template_name not in self.templates:
            try:
                self.templates[template_name] = self.env.get_template(template_name)
                self.logger.debug(f"Loaded template: {template_name}")
            except Exception as e:
                self.logger.error(f"Error loading template {template_name}: {e}")
                raise
        
        return self.templates[template_name]
    
    def render_template(self, template_name: str, variables: Dict[str, Any]) -> str:
        """
        Render a template with variables.
        
        Args:
            template_name: Name of template
            variables: Dictionary of variables to substitute
            
        Returns:
            Rendered prompt string
        """
        template = self.load_template(template_name)
        rendered = template.render(**variables)
        
        self.logger.debug(f"Rendered template '{template_name}' with {len(variables)} variables")
        return rendered
    
    def create_few_shot_prompt(
        self,
        instruction: str,
        examples: List[Dict[str, str]],
        input_text: str
    ) -> str:
        """
        Create a few-shot learning prompt.
        
        Args:
            instruction: Task instruction
            examples: List of example dicts with 'input', 'output', optional 'explanation'
            input_text: New input to process
            
        Returns:
            Formatted few-shot prompt
        """
        return self.render_template(
            'few_shot_example',
            {
                'instruction': instruction,
                'examples': examples,
                'input': input_text
            }
        )
    
    def validate_template(self, template_name: str, required_vars: List[str]) -> bool:
        """
        Validate that a template contains required variables.
        
        Args:
            template_name: Name of template
            required_vars: List of required variable names
            
        Returns:
            True if all required variables are present
        """
        try:
            template = self.load_template(template_name)
            template_vars = template.module.__dict__.get('variables', set())
            
            missing_vars = set(required_vars) - template_vars
            if missing_vars:
                self.logger.warning(
                    f"Template '{template_name}' missing variables: {missing_vars}"
                )
                return False
            
            return True
        except Exception as e:
            self.logger.error(f"Error validating template: {e}")
            return False
    
    def list_templates(self) -> List[str]:
        """
        List all available templates.
        
        Returns:
            List of template names
        """
        templates = [f.stem for f in self.template_dir.glob('*.txt')]
        return sorted(templates)
    
    def add_template(self, name: str, content: str) -> None:
        """
        Add a new template.
        
        Args:
            name: Template name
            content: Template content
        """
        if not name.endswith('.txt'):
            name += '.txt'
        
        filepath = self.template_dir / name
        with open(filepath, 'w') as f:
            f.write(content)
        
        # Clear cache for this template
        if name in self.templates:
            del self.templates[name]
        
        self.logger.info(f"Added template: {name}")
    
    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """
        Get information about a template.
        
        Args:
            template_name: Name of template
            
        Returns:
            Dictionary with template metadata
        """
        if not template_name.endswith('.txt'):
            template_name += '.txt'
        
        filepath = self.template_dir / template_name
        
        if not filepath.exists():
            return {'error': 'Template not found'}
        
        stat = filepath.stat()
        
        return {
            'name': template_name,
            'path': str(filepath),
            'size': stat.st_size,
            'modified': stat.st_mtime,
            'exists': True
        }
