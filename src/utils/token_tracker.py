"""
Token Usage Tracking System

This module provides comprehensive tracking of LLM token usage
for cost monitoring, optimization, and analysis.

Features:
- Token usage tracking per agent/task
- Cost calculation
- Usage statistics and reports
- Persistent storage
- Alert thresholds

Usage:
    tracker = TokenTracker(agent_name="MyAgent")
    tracker.track(prompt_tokens=100, completion_tokens=50, model="gpt-4")
    summary = tracker.get_summary()
"""

import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict


class TokenTracker:
    """
    Tracks token usage and costs for LLM operations.
    
    Provides detailed tracking of token consumption with cost
    calculations, usage statistics, and reporting capabilities.
    
    Attributes:
        agent_name: Name of the agent being tracked
        usage_data: Token usage records
        model_costs: Cost per token by model
    """
    
    # Token costs (per 1K tokens) - February 2026 pricing
    MODEL_COSTS = {
        'gpt-4-turbo-preview': {'prompt': 0.01, 'completion': 0.03},
        'gpt-4': {'prompt': 0.03, 'completion': 0.06},
        'gpt-3.5-turbo': {'prompt': 0.0005, 'completion': 0.0015},
        'claude-3-opus-20240229': {'prompt': 0.015, 'completion': 0.075},
        'claude-3-sonnet-20240229': {'prompt': 0.003, 'completion': 0.015},
        'claude-3-haiku-20240307': {'prompt': 0.00025, 'completion': 0.00125},
        'text-embedding-3-large': {'prompt': 0.00013, 'completion': 0.0},
        'text-embedding-3-small': {'prompt': 0.00002, 'completion': 0.0},
    }
    
    def __init__(
        self,
        agent_name: str = "default",
        log_file: Optional[str] = None,
        alert_threshold: int = 100000
    ):
        """
        Initialize Token Tracker.
        
        Args:
            agent_name: Name of the agent to track
            log_file: Path to JSON log file for persistence
            alert_threshold: Daily token threshold for alerts
        """
        self.logger = logging.getLogger(__name__)
        self.agent_name = agent_name
        self.alert_threshold = alert_threshold
        
        # Set log file path
        if log_file is None:
            log_file = f"./data/logs/token_usage_{agent_name}.json"
        
        self.log_file = Path(log_file)
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # Usage data structure
        self.usage_data: List[Dict[str, Any]] = []
        
        # Load existing data if available
        self._load_data()
        
        self.logger.info(f"Token Tracker initialized for agent: {agent_name}")
    
    def track(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str,
        task: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Track a token usage event.
        
        Args:
            prompt_tokens: Number of tokens in prompt
            completion_tokens: Number of tokens in completion
            model: Model name used
            task: Optional task identifier
            metadata: Optional additional metadata
            
        Returns:
            Record of the usage event with cost calculation
        """
        total_tokens = prompt_tokens + completion_tokens
        
        # Calculate cost
        cost = self._calculate_cost(prompt_tokens, completion_tokens, model)
        
        # Create record
        record = {
            'timestamp': datetime.now().isoformat(),
            'agent': self.agent_name,
            'model': model,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_tokens': total_tokens,
            'cost': cost,
            'task': task,
            'metadata': metadata or {}
        }
        
        self.usage_data.append(record)
        
        # Save to file
        self._save_data()
        
        # Check alert threshold
        self._check_threshold()
        
        self.logger.debug(
            f"Tracked: {total_tokens} tokens, ${cost:.6f} "
            f"(model: {model}, task: {task})"
        )
        
        return record
    
    def _calculate_cost(
        self,
        prompt_tokens: int,
        completion_tokens: int,
        model: str
    ) -> float:
        """
        Calculate cost based on token usage and model.
        
        Args:
            prompt_tokens: Number of prompt tokens
            completion_tokens: Number of completion tokens
            model: Model name
            
        Returns:
            Cost in USD
        """
        if model not in self.MODEL_COSTS:
            self.logger.warning(f"Unknown model '{model}', using default costs")
            costs = {'prompt': 0.01, 'completion': 0.03}
        else:
            costs = self.MODEL_COSTS[model]
        
        prompt_cost = (prompt_tokens / 1000) * costs['prompt']
        completion_cost = (completion_tokens / 1000) * costs['completion']
        
        return prompt_cost + completion_cost
    
    def get_summary(self, time_period: Optional[str] = None) -> Dict[str, Any]:
        """
        Get usage summary statistics.
        
        Args:
            time_period: Optional time filter ('hour', 'day', 'week', 'month', 'all')
            
        Returns:
            Summary statistics dictionary
        """
        filtered_data = self._filter_by_time(time_period or 'all')
        
        if not filtered_data:
            return {
                'agent': self.agent_name,
                'period': time_period or 'all',
                'total_records': 0,
                'total_tokens': 0,
                'total_cost': 0.0
            }
        
        total_tokens = sum(r['total_tokens'] for r in filtered_data)
        total_cost = sum(r['cost'] for r in filtered_data)
        prompt_tokens = sum(r['prompt_tokens'] for r in filtered_data)
        completion_tokens = sum(r['completion_tokens'] for r in filtered_data)
        
        # Model breakdown
        model_stats = defaultdict(lambda: {'count': 0, 'tokens': 0, 'cost': 0.0})
        for record in filtered_data:
            model = record['model']
            model_stats[model]['count'] += 1
            model_stats[model]['tokens'] += record['total_tokens']
            model_stats[model]['cost'] += record['cost']
        
        # Task breakdown
        task_stats = defaultdict(lambda: {'count': 0, 'tokens': 0, 'cost': 0.0})
        for record in filtered_data:
            task = record.get('task', 'unknown')
            task_stats[task]['count'] += 1
            task_stats[task]['tokens'] += record['total_tokens']
            task_stats[task]['cost'] += record['cost']
        
        return {
            'agent': self.agent_name,
            'period': time_period or 'all',
            'total_records': len(filtered_data),
            'total_tokens': total_tokens,
            'prompt_tokens': prompt_tokens,
            'completion_tokens': completion_tokens,
            'total_cost': round(total_cost, 6),
            'average_tokens_per_request': round(total_tokens / len(filtered_data), 2),
            'average_cost_per_request': round(total_cost / len(filtered_data), 6),
            'by_model': dict(model_stats),
            'by_task': dict(task_stats),
            'first_request': filtered_data[0]['timestamp'],
            'last_request': filtered_data[-1]['timestamp']
        }
    
    def _filter_by_time(self, period: str) -> List[Dict[str, Any]]:
        """Filter usage data by time period."""
        if period == 'all' or not self.usage_data:
            return self.usage_data
        
        now = datetime.now()
        time_deltas = {
            'hour': timedelta(hours=1),
            'day': timedelta(days=1),
            'week': timedelta(weeks=1),
            'month': timedelta(days=30)
        }
        
        if period not in time_deltas:
            return self.usage_data
        
        cutoff = now - time_deltas[period]
        
        return [
            r for r in self.usage_data
            if datetime.fromisoformat(r['timestamp']) >= cutoff
        ]
    
    def _check_threshold(self) -> None:
        """Check if daily token usage exceeds threshold."""
        daily_data = self._filter_by_time('day')
        daily_tokens = sum(r['total_tokens'] for r in daily_data)
        
        if daily_tokens > self.alert_threshold:
            self.logger.warning(
                f"Daily token usage ({daily_tokens}) exceeded threshold "
                f"({self.alert_threshold}) for agent '{self.agent_name}'"
            )
    
    def generate_report(self, period: str = 'day') -> str:
        """
        Generate a formatted usage report.
        
        Args:
            period: Time period for report
            
        Returns:
            Formatted report string
        """
        summary = self.get_summary(period)
        
        report = f"""
Token Usage Report - {self.agent_name}
{'=' * 60}
Period: {period}
Total Requests: {summary['total_records']}
Total Tokens: {summary['total_tokens']:,}
  - Prompt: {summary['prompt_tokens']:,}
  - Completion: {summary['completion_tokens']:,}
Total Cost: ${summary['total_cost']:.6f}

Average per Request:
  - Tokens: {summary['average_tokens_per_request']:.2f}
  - Cost: ${summary['average_cost_per_request']:.6f}

By Model:
"""
        
        for model, stats in summary['by_model'].items():
            report += f"  {model}:\n"
            report += f"    Requests: {stats['count']}\n"
            report += f"    Tokens: {stats['tokens']:,}\n"
            report += f"    Cost: ${stats['cost']:.6f}\n"
        
        if summary['by_task']:
            report += "\nBy Task:\n"
            for task, stats in summary['by_task'].items():
                report += f"  {task}:\n"
                report += f"    Requests: {stats['count']}\n"
                report += f"    Tokens: {stats['tokens']:,}\n"
                report += f"    Cost: ${stats['cost']:.6f}\n"
        
        return report
    
    def _save_data(self) -> None:
        """Save usage data to JSON file."""
        try:
            with open(self.log_file, 'w') as f:
                json.dump(self.usage_data, f, indent=2)
        except Exception as e:
            self.logger.error(f"Error saving token data: {e}")
    
    def _load_data(self) -> None:
        """Load usage data from JSON file."""
        if self.log_file.exists():
            try:
                with open(self.log_file, 'r') as f:
                    self.usage_data = json.load(f)
                self.logger.info(f"Loaded {len(self.usage_data)} existing records")
            except Exception as e:
                self.logger.error(f"Error loading token data: {e}")
                self.usage_data = []
        else:
            self.usage_data = []
    
    def reset(self) -> None:
        """Reset all usage data."""
        self.usage_data = []
        self._save_data()
        self.logger.info("Token tracker reset")
    
    def export_csv(self, filepath: str) -> None:
        """
        Export usage data to CSV file.
        
        Args:
            filepath: Path to CSV file
        """
        import csv
        
        if not self.usage_data:
            self.logger.warning("No data to export")
            return
        
        with open(filepath, 'w', newline='') as f:
            fieldnames = [
                'timestamp', 'agent', 'model', 'task',
                'prompt_tokens', 'completion_tokens', 'total_tokens', 'cost'
            ]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for record in self.usage_data:
                row = {k: record.get(k, '') for k in fieldnames}
                writer.writerow(row)
        
        self.logger.info(f"Exported {len(self.usage_data)} records to {filepath}")
