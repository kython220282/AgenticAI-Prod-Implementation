"""
Logger Module
=============

This module provides logging utilities and configuration for the Agentic AI system.

Purpose:
--------
- Set up structured logging
- Configure log levels and formats
- Provide context-aware logging
- Support log rotation and archival

Usage:
------
    from utils import setup_logger, get_logger
    
    # Setup logger for a module
    logger = setup_logger('my_module', level='DEBUG')
    
    # Use logger
    logger.info("Agent initialized")
    logger.debug("Detailed debug information")
    logger.error("An error occurred", exc_info=True)
    
    # Get existing logger
    logger = get_logger('my_module')

Key Features:
------------
- Hierarchical logging
- Multiple output handlers (file, console, etc.)
- Structured log formatting
- Performance logging
"""

import logging
import logging.config
from pathlib import Path
from typing import Optional
import yaml


def setup_logger(name: str, 
                level: str = 'INFO',
                log_file: Optional[str] = None,
                use_config: bool = True) -> logging.Logger:
    """
    Set up a logger with specified configuration.
    
    Args:
        name (str): Logger name
        level (str): Logging level ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file (str, optional): Path to log file
        use_config (bool): Whether to use logging config file
        
    Returns:
        logging.Logger: Configured logger instance
    """
    # Load logging configuration if available
    if use_config:
        config_path = Path(__file__).parent.parent.parent / 'config' / 'logging_config.yaml'
        
        if config_path.exists():
            try:
                with open(config_path, 'r') as f:
                    config = yaml.safe_load(f)
                    logging.config.dictConfig(config)
            except Exception as e:
                print(f"Warning: Could not load logging config: {e}")
    
    # Get or create logger
    logger = logging.getLogger(name)
    
    # Set level
    logger.setLevel(getattr(logging, level.upper()))
    
    # Add console handler if not already configured
    if not logger.handlers and not use_config:
        console_handler = logging.StreamHandler()
        console_handler.setLevel(getattr(logging, level.upper()))
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Add file handler if specified
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get an existing logger by name.
    
    Args:
        name (str): Logger name
        
    Returns:
        logging.Logger: Logger instance
    """
    return logging.getLogger(name)


class ContextLogger:
    """
    Context-aware logger that adds contextual information to log messages.
    
    Usage:
        logger = ContextLogger('my_module', context={'agent_id': 'agent_1'})
        logger.info("Processing request")  # Will include agent_id in log
    """
    
    def __init__(self, name: str, context: Optional[dict] = None):
        """
        Initialize context logger.
        
        Args:
            name (str): Logger name
            context (dict, optional): Context dictionary to include in logs
        """
        self.logger = logging.getLogger(name)
        self.context = context or {}
    
    def _format_message(self, msg: str) -> str:
        """Add context to message."""
        if self.context:
            context_str = ' '.join([f"{k}={v}" for k, v in self.context.items()])
            return f"[{context_str}] {msg}"
        return msg
    
    def debug(self, msg: str, *args, **kwargs):
        """Log debug message with context."""
        self.logger.debug(self._format_message(msg), *args, **kwargs)
    
    def info(self, msg: str, *args, **kwargs):
        """Log info message with context."""
        self.logger.info(self._format_message(msg), *args, **kwargs)
    
    def warning(self, msg: str, *args, **kwargs):
        """Log warning message with context."""
        self.logger.warning(self._format_message(msg), *args, **kwargs)
    
    def error(self, msg: str, *args, **kwargs):
        """Log error message with context."""
        self.logger.error(self._format_message(msg), *args, **kwargs)
    
    def critical(self, msg: str, *args, **kwargs):
        """Log critical message with context."""
        self.logger.critical(self._format_message(msg), *args, **kwargs)
    
    def set_context(self, **kwargs):
        """Update context dictionary."""
        self.context.update(kwargs)


class PerformanceLogger:
    """
    Logger specialized for performance metrics.
    
    Usage:
        perf_logger = PerformanceLogger()
        
        with perf_logger.measure('operation_name'):
            # Perform operation
            pass
    """
    
    def __init__(self, name: str = 'performance'):
        """Initialize performance logger."""
        self.logger = logging.getLogger(name)
    
    def measure(self, operation: str):
        """
        Context manager for measuring operation time.
        
        Args:
            operation (str): Operation name
        """
        from contextlib import contextmanager
        import time
        
        @contextmanager
        def _measure():
            start_time = time.time()
            try:
                yield
            finally:
                elapsed = time.time() - start_time
                self.logger.info(f"{operation} completed in {elapsed:.4f}s")
        
        return _measure()
    
    def log_metric(self, name: str, value: float, unit: str = ''):
        """
        Log a performance metric.
        
        Args:
            name (str): Metric name
            value (float): Metric value
            unit (str): Unit of measurement
        """
        unit_str = f" {unit}" if unit else ""
        self.logger.info(f"{name}: {value:.4f}{unit_str}")
