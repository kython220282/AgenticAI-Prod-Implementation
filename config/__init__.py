"""
Configuration Package
=====================

This package contains all configuration files for the Agentic AI system.

Files:
- agent_config.yaml: Agent-specific configurations (types, parameters, behaviors)
- model_config.yaml: ML model configurations (architecture, hyperparameters)
- environment_config.yaml: Environment settings (simulation parameters, constraints)
- logging_config.yaml: Logging configuration (levels, formats, outputs)

Usage:
    from config import load_config
    config = load_config('agent_config.yaml')
"""

import yaml
import os
from pathlib import Path


def load_config(config_name: str) -> dict:
    """
    Load a YAML configuration file from the config directory.
    
    Args:
        config_name (str): Name of the config file (e.g., 'agent_config.yaml')
        
    Returns:
        dict: Parsed configuration dictionary
        
    Example:
        >>> config = load_config('agent_config.yaml')
        >>> agent_type = config['agent']['type']
    """
    config_dir = Path(__file__).parent
    config_path = config_dir / config_name
    
    if not config_path.exists():
        raise FileNotFoundError(f"Configuration file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)


def get_config_path(config_name: str) -> Path:
    """Get the full path to a configuration file."""
    return Path(__file__).parent / config_name
