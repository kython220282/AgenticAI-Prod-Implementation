"""
Executor Module
===============

This module implements action execution and monitoring systems for agents,
handling action execution, error recovery, and performance tracking.

Purpose:
--------
- Execute actions in the environment
- Monitor execution status and outcomes
- Handle execution errors and failures
- Track execution metrics

Usage:
------
    from core import Executor
    
    executor = Executor(max_retries=3, timeout=10.0)
    
    # Execute single action
    result = executor.execute(action, environment)
    
    # Execute action sequence
    results = executor.execute_sequence(actions, environment)
    
    # Execute with error handling
    result = executor.execute_safe(action, env, fallback_action)

Key Features:
------------
- Action execution with error handling
- Retry mechanisms for failed actions
- Execution monitoring and logging
- Performance metrics tracking
- Timeout handling
"""

from typing import Any, Dict, List, Optional, Callable
import logging
import time
from enum import Enum


class ExecutionStatus(Enum):
    """Status codes for action execution."""
    SUCCESS = "success"
    FAILURE = "failure"
    TIMEOUT = "timeout"
    ERROR = "error"
    RETRYING = "retrying"


class Executor:
    """
    Action execution system for agents.
    
    Handles action execution, monitoring, error recovery, and performance tracking.
    """
    
    def __init__(self, max_retries: int = 3, timeout: float = 10.0, 
                 retry_delay: float = 0.5):
        """
        Initialize the executor.
        
        Args:
            max_retries (int): Maximum number of retry attempts
            timeout (float): Execution timeout in seconds
            retry_delay (float): Delay between retries in seconds
        """
        self.max_retries = max_retries
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.logger = logging.getLogger('core.Executor')
        
        # Execution tracking
        self.execution_history = []
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time = 0.0
        
        # Error handlers
        self.error_handlers = {}
        
        self.logger.info(
            f"Executor initialized - Max retries: {max_retries}, "
            f"Timeout: {timeout}s"
        )
    
    def execute(self, action: Any, environment: Any, 
                context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute a single action in the environment.
        
        Args:
            action: Action to execute
            environment: Environment to execute action in
            context (Dict, optional): Additional execution context
            
        Returns:
            Dict containing execution results:
                - status: ExecutionStatus
                - result: Action result (if successful)
                - error: Error message (if failed)
                - duration: Execution time
        """
        start_time = time.time()
        
        self.logger.debug(f"Executing action: {action}")
        
        try:
            # Execute action with timeout
            result = self._execute_with_timeout(action, environment, self.timeout)
            
            duration = time.time() - start_time
            self.total_execution_time += duration
            self.success_count += 1
            
            execution_result = {
                'status': ExecutionStatus.SUCCESS,
                'result': result,
                'duration': duration,
                'action': action
            }
            
            self.logger.info(f"Action executed successfully in {duration:.3f}s")
            
        except TimeoutError as e:
            duration = time.time() - start_time
            self.failure_count += 1
            
            execution_result = {
                'status': ExecutionStatus.TIMEOUT,
                'error': str(e),
                'duration': duration,
                'action': action
            }
            
            self.logger.error(f"Action execution timeout after {duration:.3f}s")
            
        except Exception as e:
            duration = time.time() - start_time
            self.failure_count += 1
            
            execution_result = {
                'status': ExecutionStatus.ERROR,
                'error': str(e),
                'duration': duration,
                'action': action
            }
            
            self.logger.error(f"Action execution error: {e}")
        
        # Record execution
        self.execution_history.append(execution_result)
        
        return execution_result
    
    def execute_with_retry(self, action: Any, environment: Any,
                          context: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Execute action with automatic retry on failure.
        
        Args:
            action: Action to execute
            environment: Environment to execute action in
            context (Dict, optional): Execution context
            
        Returns:
            Dict containing execution results
        """
        retries = 0
        last_result = None
        
        while retries <= self.max_retries:
            if retries > 0:
                self.logger.info(f"Retry attempt {retries}/{self.max_retries}")
                time.sleep(self.retry_delay)
            
            result = self.execute(action, environment, context)
            
            if result['status'] == ExecutionStatus.SUCCESS:
                return result
            
            last_result = result
            retries += 1
        
        # All retries exhausted
        self.logger.error(f"Action failed after {self.max_retries} retries")
        return last_result if last_result is not None else {'status': ExecutionStatus.FAILURE, 'error': 'No result after retries'}
    
    def execute_sequence(self, actions: List[Any], environment: Any,
                        stop_on_failure: bool = True) -> List[Dict[str, Any]]:
        """
        Execute a sequence of actions.
        
        Args:
            actions (List): List of actions to execute
            environment: Environment to execute in
            stop_on_failure (bool): Whether to stop if an action fails
            
        Returns:
            List of execution results for each action
        """
        self.logger.info(f"Executing sequence of {len(actions)} actions")
        
        results = []
        
        for i, action in enumerate(actions):
            self.logger.debug(f"Executing action {i+1}/{len(actions)}: {action}")
            
            result = self.execute(action, environment)
            results.append(result)
            
            # Check if we should stop
            if stop_on_failure and result['status'] != ExecutionStatus.SUCCESS:
                self.logger.warning(
                    f"Stopping sequence execution at action {i+1} due to failure"
                )
                break
        
        successful = sum(1 for r in results if r['status'] == ExecutionStatus.SUCCESS)
        self.logger.info(
            f"Sequence execution complete - "
            f"Success: {successful}/{len(results)}"
        )
        
        return results
    
    def execute_safe(self, action: Any, environment: Any,
                    fallback_action: Optional[Any] = None) -> Dict[str, Any]:
        """
        Execute action safely with fallback option.
        
        Args:
            action: Primary action to execute
            environment: Environment to execute in
            fallback_action: Action to try if primary fails
            
        Returns:
            Dict containing execution results
        """
        result = self.execute_with_retry(action, environment)
        
        # If primary action failed and fallback available
        if result['status'] != ExecutionStatus.SUCCESS and fallback_action:
            self.logger.info("Primary action failed, attempting fallback")
            
            fallback_result = self.execute(fallback_action, environment)
            fallback_result['used_fallback'] = True
            fallback_result['primary_action'] = action
            
            return fallback_result
        
        return result
    
    def _execute_with_timeout(self, action: Any, environment: Any,
                             timeout: float) -> Any:
        """
        Execute action with timeout.
        
        Args:
            action: Action to execute
            environment: Environment
            timeout (float): Timeout in seconds
            
        Returns:
            Action result
            
        Raises:
            TimeoutError: If execution exceeds timeout
        """
        # Simple timeout implementation
        # In practice, might use threading.Timer or asyncio
        
        start_time = time.time()
        
        # Execute action (assuming environment has a step method)
        if hasattr(environment, 'step'):
            result = environment.step(action)
        else:
            # Fallback: just return action result
            result = action
        
        elapsed = time.time() - start_time
        
        if elapsed > timeout:
            raise TimeoutError(f"Execution exceeded timeout of {timeout}s")
        
        return result
    
    def register_error_handler(self, error_type: type, 
                               handler: Callable):
        """
        Register a custom error handler for specific error types.
        
        Args:
            error_type (type): Exception type to handle
            handler (Callable): Function(error, action, environment) -> recovery_action
        """
        self.error_handlers[error_type] = handler
        self.logger.debug(f"Registered error handler for {error_type.__name__}")
    
    def handle_error(self, error: Exception, action: Any, 
                    environment: Any) -> Optional[Any]:
        """
        Handle execution error using registered handlers.
        
        Args:
            error (Exception): Error that occurred
            action: Action that failed
            environment: Environment
            
        Returns:
            Recovery action, or None if no handler available
        """
        error_type = type(error)
        
        if error_type in self.error_handlers:
            handler = self.error_handlers[error_type]
            recovery_action = handler(error, action, environment)
            
            self.logger.info(f"Error handled by custom handler: {error_type.__name__}")
            return recovery_action
        
        return None
    
    def monitor_execution(self, action: Any, environment: Any) -> Dict[str, Any]:
        """
        Execute action with detailed monitoring.
        
        Args:
            action: Action to execute
            environment: Environment
            
        Returns:
            Dict with detailed execution metrics
        """
        start_time = time.time()
        
        # Pre-execution state
        pre_state = self._capture_state(environment) if hasattr(environment, 'get_state') else None
        
        # Execute
        result = self.execute(action, environment)
        
        # Post-execution state
        post_state = self._capture_state(environment) if hasattr(environment, 'get_state') else None
        
        # Calculate metrics
        duration = time.time() - start_time
        
        monitoring_result = {
            **result,
            'pre_state': pre_state,
            'post_state': post_state,
            'state_change': self._calculate_state_change(pre_state, post_state),
            'timestamp': start_time
        }
        
        return monitoring_result
    
    def _capture_state(self, environment: Any) -> Any:
        """Capture current environment state."""
        if hasattr(environment, 'get_state'):
            return environment.get_state()
        return None
    
    def _calculate_state_change(self, pre_state: Any, post_state: Any) -> Dict:
        """Calculate changes between states."""
        if pre_state is None or post_state is None:
            return {}
        
        # Placeholder implementation
        return {'changed': pre_state != post_state}
    
    def get_success_rate(self) -> float:
        """
        Calculate success rate of executions.
        
        Returns:
            float: Success rate (0-1)
        """
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        
        return self.success_count / total
    
    def get_average_execution_time(self) -> float:
        """
        Get average execution time.
        
        Returns:
            float: Average time in seconds
        """
        total = self.success_count + self.failure_count
        if total == 0:
            return 0.0
        
        return self.total_execution_time / total
    
    def clear_history(self):
        """Clear execution history."""
        self.execution_history.clear()
        self.logger.debug("Execution history cleared")
    
    def reset_stats(self):
        """Reset execution statistics."""
        self.success_count = 0
        self.failure_count = 0
        self.total_execution_time = 0.0
        self.execution_history.clear()
        self.logger.info("Execution statistics reset")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get executor statistics."""
        return {
            'max_retries': self.max_retries,
            'timeout': self.timeout,
            'success_count': self.success_count,
            'failure_count': self.failure_count,
            'success_rate': self.get_success_rate(),
            'average_execution_time': self.get_average_execution_time(),
            'total_executions': len(self.execution_history)
        }
    
    def __repr__(self) -> str:
        """String representation of executor."""
        return (f"Executor(max_retries={self.max_retries}, "
                f"timeout={self.timeout}, "
                f"success_rate={self.get_success_rate():.2%})")
