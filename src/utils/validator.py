"""
Validator Module
================

This module provides data validation and integrity checking utilities.

Purpose:
--------
- Validate configuration files
- Check data integrity
- Verify system requirements
- Validate agent states and actions

Usage:
------
    from utils import Validator
    
    validator = Validator()
    
    # Validate configuration
    is_valid = validator.validate_config(config_dict, schema)
    
    # Validate data range
    validator.check_range(value, min_val, max_val, "parameter_name")
    
    # Validate required fields
    validator.check_required_fields(data, ['field1', 'field2'])

Key Features:
------------
- Schema-based validation
- Type checking
- Range validation
- Required field checking
"""

from typing import Any, Dict, List, Optional, Callable
import logging
import numpy as np


class Validator:
    """
    Data validation and integrity checking system.
    
    Provides utilities for validating configurations, data, and system states.
    """
    
    def __init__(self, strict_mode: bool = False):
        """
        Initialize the validator.
        
        Args:
            strict_mode (bool): If True, raise exceptions on validation failure
        """
        self.strict_mode = strict_mode
        self.logger = logging.getLogger('utils.Validator')
        self.validation_errors = []
        
        self.logger.info(f"Validator initialized - Strict mode: {strict_mode}")
    
    def validate_config(self, config: Dict[str, Any], 
                       schema: Dict[str, Any]) -> bool:
        """
        Validate configuration against a schema.
        
        Args:
            config (Dict): Configuration dictionary to validate
            schema (Dict): Schema specifying expected structure and types
            
        Returns:
            bool: True if valid, False otherwise
        """
        self.validation_errors.clear()
        
        for key, spec in schema.items():
            if spec.get('required', False) and key not in config:
                error = f"Missing required field: {key}"
                self._handle_error(error)
                continue
            
            if key in config:
                value = config[key]
                expected_type = spec.get('type')
                
                # Type checking
                if expected_type and not isinstance(value, expected_type):
                    error = f"Invalid type for {key}: expected {expected_type}, got {type(value)}"
                    self._handle_error(error)
                
                # Range checking for numeric values
                if isinstance(value, (int, float)):
                    if 'min' in spec and value < spec['min']:
                        error = f"{key} value {value} below minimum {spec['min']}"
                        self._handle_error(error)
                    
                    if 'max' in spec and value > spec['max']:
                        error = f"{key} value {value} above maximum {spec['max']}"
                        self._handle_error(error)
                
                # Allowed values
                if 'allowed' in spec and value not in spec['allowed']:
                    error = f"{key} value {value} not in allowed values: {spec['allowed']}"
                    self._handle_error(error)
        
        is_valid = len(self.validation_errors) == 0
        
        if is_valid:
            self.logger.info("Configuration validation passed")
        else:
            self.logger.warning(f"Configuration validation failed with {len(self.validation_errors)} errors")
        
        return is_valid
    
    def check_required_fields(self, data: Dict[str, Any], 
                             required_fields: List[str]) -> bool:
        """
        Check if all required fields are present in data.
        
        Args:
            data (Dict): Data dictionary
            required_fields (List): List of required field names
            
        Returns:
            bool: True if all required fields present
        """
        self.validation_errors.clear()
        
        for field in required_fields:
            if field not in data:
                error = f"Missing required field: {field}"
                self._handle_error(error)
        
        return len(self.validation_errors) == 0
    
    def check_type(self, value: Any, expected_type: type, 
                   name: str = "value") -> bool:
        """
        Check if value is of expected type.
        
        Args:
            value: Value to check
            expected_type (type): Expected type
            name (str): Name of value for error messages
            
        Returns:
            bool: True if type matches
        """
        if not isinstance(value, expected_type):
            error = f"{name} has invalid type: expected {expected_type}, got {type(value)}"
            self._handle_error(error)
            return False
        return True
    
    def check_range(self, value: float, min_val: float, max_val: float,
                   name: str = "value") -> bool:
        """
        Check if value is within specified range.
        
        Args:
            value (float): Value to check
            min_val (float): Minimum allowed value
            max_val (float): Maximum allowed value
            name (str): Name of value for error messages
            
        Returns:
            bool: True if within range
        """
        if value < min_val:
            error = f"{name} value {value} below minimum {min_val}"
            self._handle_error(error)
            return False
        
        if value > max_val:
            error = f"{name} value {value} above maximum {max_val}"
            self._handle_error(error)
            return False
        
        return True
    
    def check_shape(self, array: np.ndarray, expected_shape: tuple,
                   name: str = "array") -> bool:
        """
        Check if array has expected shape.
        
        Args:
            array (np.ndarray): Array to check
            expected_shape (tuple): Expected shape
            name (str): Name of array for error messages
            
        Returns:
            bool: True if shape matches
        """
        if array.shape != expected_shape:
            error = f"{name} has invalid shape: expected {expected_shape}, got {array.shape}"
            self._handle_error(error)
            return False
        return True
    
    def check_positive(self, value: float, name: str = "value") -> bool:
        """
        Check if value is positive.
        
        Args:
            value (float): Value to check
            name (str): Name of value for error messages
            
        Returns:
            bool: True if positive
        """
        if value <= 0:
            error = f"{name} must be positive, got {value}"
            self._handle_error(error)
            return False
        return True
    
    def check_non_negative(self, value: float, name: str = "value") -> bool:
        """
        Check if value is non-negative.
        
        Args:
            value (float): Value to check
            name (str): Name of value for error messages
            
        Returns:
            bool: True if non-negative
        """
        if value < 0:
            error = f"{name} must be non-negative, got {value}"
            self._handle_error(error)
            return False
        return True
    
    def check_probability(self, value: float, name: str = "probability") -> bool:
        """
        Check if value is a valid probability (0 to 1).
        
        Args:
            value (float): Value to check
            name (str): Name of value for error messages
            
        Returns:
            bool: True if valid probability
        """
        return self.check_range(value, 0.0, 1.0, name)
    
    def check_not_empty(self, collection: Any, name: str = "collection") -> bool:
        """
        Check if collection is not empty.
        
        Args:
            collection: Collection to check (list, dict, etc.)
            name (str): Name of collection for error messages
            
        Returns:
            bool: True if not empty
        """
        if not collection:
            error = f"{name} is empty"
            self._handle_error(error)
            return False
        return True
    
    def check_custom(self, value: Any, validator_func: Callable,
                    name: str = "value") -> bool:
        """
        Check value using custom validator function.
        
        Args:
            value: Value to check
            validator_func (Callable): Function that returns True if valid
            name (str): Name of value for error messages
            
        Returns:
            bool: True if validation passes
        """
        try:
            if not validator_func(value):
                error = f"{name} failed custom validation"
                self._handle_error(error)
                return False
        except Exception as e:
            error = f"{name} validation error: {str(e)}"
            self._handle_error(error)
            return False
        
        return True
    
    def validate_agent_state(self, state: Dict[str, Any]) -> bool:
        """
        Validate agent state dictionary.
        
        Args:
            state (Dict): Agent state to validate
            
        Returns:
            bool: True if valid
        """
        required_fields = ['initialized', 'step_count']
        return self.check_required_fields(state, required_fields)
    
    def validate_environment_config(self, config: Dict[str, Any]) -> bool:
        """
        Validate environment configuration.
        
        Args:
            config (Dict): Environment configuration
            
        Returns:
            bool: True if valid
        """
        schema = {
            'max_steps': {'type': int, 'min': 1, 'required': True},
            'state_dim': {'type': int, 'min': 1, 'required': True},
            'action_dim': {'type': int, 'min': 1, 'required': True},
        }
        
        return self.validate_config(config, schema)
    
    def _handle_error(self, error: str):
        """
        Handle validation error based on strict mode.
        
        Args:
            error (str): Error message
        """
        self.validation_errors.append(error)
        self.logger.error(f"Validation error: {error}")
        
        if self.strict_mode:
            raise ValueError(error)
    
    def get_errors(self) -> List[str]:
        """
        Get list of validation errors.
        
        Returns:
            List of error messages
        """
        return self.validation_errors.copy()
    
    def clear_errors(self):
        """Clear validation errors."""
        self.validation_errors.clear()
    
    def has_errors(self) -> bool:
        """Check if there are validation errors."""
        return len(self.validation_errors) > 0
    
    def __repr__(self) -> str:
        """String representation of validator."""
        return f"Validator(strict_mode={self.strict_mode}, errors={len(self.validation_errors)})"
