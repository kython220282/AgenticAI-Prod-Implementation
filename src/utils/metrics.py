"""
Metrics Module
==============

This module provides performance metrics tracking and analysis for agents and systems.

Purpose:
--------
- Track agent performance metrics
- Calculate statistics and aggregates
- Support real-time monitoring
- Generate performance reports

Usage:
------
    from utils import MetricsTracker
    
    metrics = MetricsTracker()
    
    # Record metrics
    metrics.record('episode_reward', 150.5)
    metrics.record('steps', 100)
    
    # Get statistics
    avg_reward = metrics.get_mean('episode_reward')
    max_reward = metrics.get_max('episode_reward')
    
    # Get report
    report = metrics.generate_report()

Key Features:
------------
- Multi-metric tracking
- Statistical analysis
- Moving averages
- Performance reporting
"""

from typing import Dict, List, Optional, Any
from collections import defaultdict, deque
import numpy as np
import logging


class MetricsTracker:
    """
    Performance metrics tracking and analysis system.
    
    Tracks multiple metrics over time and provides statistical analysis.
    """
    
    def __init__(self, window_size: int = 100):
        """
        Initialize metrics tracker.
        
        Args:
            window_size (int): Size of sliding window for moving averages
        """
        self.window_size = window_size
        self.logger = logging.getLogger('utils.MetricsTracker')
        
        # Metric storage
        self.metrics = defaultdict(list)
        self.windowed_metrics = defaultdict(lambda: deque(maxlen=window_size))
        
        # Aggregates
        self.episode_metrics = defaultdict(list)
        
        self.logger.info(f"MetricsTracker initialized with window size: {window_size}")
    
    def record(self, name: str, value: float, episode: Optional[int] = None):
        """
        Record a metric value.
        
        Args:
            name (str): Metric name
            value (float): Metric value
            episode (int, optional): Episode number
        """
        self.metrics[name].append(value)
        self.windowed_metrics[name].append(value)
        
        if episode is not None:
            self.episode_metrics[name].append((episode, value))
        
        self.logger.debug(f"Recorded {name}: {value}")
    
    def record_batch(self, metrics_dict: Dict[str, float], episode: Optional[int] = None):
        """
        Record multiple metrics at once.
        
        Args:
            metrics_dict (Dict): Dictionary of metric_name -> value
            episode (int, optional): Episode number
        """
        for name, value in metrics_dict.items():
            self.record(name, value, episode)
    
    def get_latest(self, name: str) -> Optional[float]:
        """
        Get the most recent value for a metric.
        
        Args:
            name (str): Metric name
            
        Returns:
            float: Latest value, or None if no values recorded
        """
        values = self.metrics.get(name, [])
        return values[-1] if values else None
    
    def get_all(self, name: str) -> List[float]:
        """
        Get all recorded values for a metric.
        
        Args:
            name (str): Metric name
            
        Returns:
            List of all recorded values
        """
        return self.metrics.get(name, [])
    
    def get_mean(self, name: str, windowed: bool = False) -> float:
        """
        Get mean value of a metric.
        
        Args:
            name (str): Metric name
            windowed (bool): Use windowed mean vs all-time mean
            
        Returns:
            float: Mean value
        """
        if windowed:
            values = list(self.windowed_metrics.get(name, []))
        else:
            values = self.metrics.get(name, [])
        
        return float(np.mean(values)) if values else 0.0
    
    def get_std(self, name: str, windowed: bool = False) -> float:
        """
        Get standard deviation of a metric.
        
        Args:
            name (str): Metric name
            windowed (bool): Use windowed std vs all-time std
            
        Returns:
            float: Standard deviation
        """
        if windowed:
            values = list(self.windowed_metrics.get(name, []))
        else:
            values = self.metrics.get(name, [])
        
        return float(np.std(values)) if values else 0.0
    
    def get_min(self, name: str) -> float:
        """Get minimum value of a metric."""
        values = self.metrics.get(name, [])
        return np.min(values) if values else 0.0
    
    def get_max(self, name: str) -> float:
        """Get maximum value of a metric."""
        values = self.metrics.get(name, [])
        return np.max(values) if values else 0.0
    
    def get_sum(self, name: str) -> float:
        """Get sum of all values for a metric."""
        values = self.metrics.get(name, [])
        return np.sum(values) if values else 0.0
    
    def get_moving_average(self, name: str, window: Optional[int] = None) -> float:
        """
        Get moving average of a metric.
        
        Args:
            name (str): Metric name
            window (int, optional): Window size (uses default if None)
            
        Returns:
            float: Moving average
        """
        if window is None:
            values = list(self.windowed_metrics.get(name, []))
        else:
            all_values = self.metrics.get(name, [])
            values = all_values[-window:] if all_values else []
        
        return float(np.mean(values)) if values else 0.0
    
    def get_percentile(self, name: str, percentile: float) -> float:
        """
        Get percentile value of a metric.
        
        Args:
            name (str): Metric name
            percentile (float): Percentile (0-100)
            
        Returns:
            float: Percentile value
        """
        values = self.metrics.get(name, [])
        return np.percentile(values, percentile) if values else 0.0
    
    def get_statistics(self, name: str) -> Dict[str, float]:
        """
        Get comprehensive statistics for a metric.
        
        Args:
            name (str): Metric name
            
        Returns:
            Dict with mean, std, min, max, median, etc.
        """
        values = self.metrics.get(name, [])
        
        if not values:
            return {
                'count': 0,
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0,
                'median': 0.0
            }
        
        return {
            'count': len(values),
            'mean': float(np.mean(values)),
            'std': float(np.std(values)),
            'min': float(np.min(values)),
            'max': float(np.max(values)),
            'median': float(np.median(values)),
            'q25': float(np.percentile(values, 25)),
            'q75': float(np.percentile(values, 75))
        }
    
    def get_trend(self, name: str, window: int = 10) -> str:
        """
        Determine trend direction for a metric.
        
        Args:
            name (str): Metric name
            window (int): Window size for trend calculation
            
        Returns:
            str: 'increasing', 'decreasing', or 'stable'
        """
        values = self.metrics.get(name, [])
        
        if len(values) < window:
            return 'stable'
        
        recent = values[-window:]
        first_half = np.mean(recent[:window//2])
        second_half = np.mean(recent[window//2:])
        
        change = (second_half - first_half) / (abs(first_half) + 1e-8)
        
        if change > 0.05:
            return 'increasing'
        elif change < -0.05:
            return 'decreasing'
        else:
            return 'stable'
    
    def compare_episodes(self, name: str, episode1: int, episode2: int) -> Dict[str, float]:
        """
        Compare metric values between two episodes.
        
        Args:
            name (str): Metric name
            episode1 (int): First episode number
            episode2 (int): Second episode number
            
        Returns:
            Dict with comparison statistics
        """
        episode_values = self.episode_metrics.get(name, [])
        
        value1 = None
        value2 = None
        
        for ep, val in episode_values:
            if ep == episode1:
                value1 = val
            if ep == episode2:
                value2 = val
        
        if value1 is None or value2 is None:
            # Return empty dict or default values instead of error string
            return {}
        
        return {
            'episode1_value': value1,
            'episode2_value': value2,
            'difference': value2 - value1,
            'percent_change': ((value2 - value1) / (abs(value1) + 1e-8)) * 100
        }
    
    def generate_report(self, metrics: Optional[List[str]] = None) -> str:
        """
        Generate a text report of metrics.
        
        Args:
            metrics (List[str], optional): Specific metrics to report (all if None)
            
        Returns:
            str: Formatted report
        """
        if metrics is None:
            metrics = list(self.metrics.keys())
        
        report_lines = ["=" * 60, "Performance Metrics Report", "=" * 60, ""]
        
        for metric_name in metrics:
            stats = self.get_statistics(metric_name)
            trend = self.get_trend(metric_name)
            
            report_lines.append(f"{metric_name}:")
            report_lines.append(f"  Count: {stats['count']}")
            report_lines.append(f"  Mean:  {stats['mean']:.4f}")
            report_lines.append(f"  Std:   {stats['std']:.4f}")
            report_lines.append(f"  Min:   {stats['min']:.4f}")
            report_lines.append(f"  Max:   {stats['max']:.4f}")
            report_lines.append(f"  Trend: {trend}")
            report_lines.append("")
        
        report_lines.append("=" * 60)
        
        return "\n".join(report_lines)
    
    def reset(self, metric_name: Optional[str] = None):
        """
        Reset metrics.
        
        Args:
            metric_name (str, optional): Specific metric to reset (all if None)
        """
        if metric_name:
            self.metrics[metric_name].clear()
            self.windowed_metrics[metric_name].clear()
            self.episode_metrics[metric_name].clear()
            self.logger.info(f"Reset metric: {metric_name}")
        else:
            self.metrics.clear()
            self.windowed_metrics.clear()
            self.episode_metrics.clear()
            self.logger.info("Reset all metrics")
    
    def export_to_dict(self) -> Dict[str, Any]:
        """
        Export all metrics to dictionary.
        
        Returns:
            Dict containing all metrics data
        """
        return {
            'metrics': {name: list(values) for name, values in self.metrics.items()},
            'statistics': {name: self.get_statistics(name) for name in self.metrics.keys()}
        }
    
    def get_metric_names(self) -> List[str]:
        """Get list of all tracked metric names."""
        return list(self.metrics.keys())
    
    def __repr__(self) -> str:
        """String representation of metrics tracker."""
        num_metrics = len(self.metrics)
        return f"MetricsTracker(metrics={num_metrics}, window_size={self.window_size})"
