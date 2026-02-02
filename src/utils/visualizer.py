"""
Visualizer Module
=================

This module provides visualization tools for agents, environments, and performance metrics.

Purpose:
--------
- Visualize agent behavior and trajectories
- Plot performance metrics over time
- Create environment visualizations
- Generate training progress graphs

Usage:
------
    from utils import Visualizer
    
    viz = Visualizer()
    
    # Plot metrics
    viz.plot_metrics(metrics_dict, title="Training Progress")
    
    # Plot agent trajectory
    viz.plot_trajectory(positions, goals)
    
    # Plot learning curve
    viz.plot_learning_curve(rewards, window=100)

Key Features:
------------
- Matplotlib-based plotting
- Interactive visualizations
- Multi-plot dashboards
- Export to image files
"""

from typing import List, Dict, Optional, Tuple, Any
import logging
import numpy as np


class Visualizer:
    """
    Visualization tools for agents and performance metrics.
    
    Provides plotting and visualization capabilities for analysis.
    """
    
    def __init__(self, style: str = 'default', save_dir: Optional[str] = None):
        """
        Initialize the visualizer.
        
        Args:
            style (str): Matplotlib style to use
            save_dir (str, optional): Directory to save plots
        """
        self.style = style
        self.save_dir = save_dir
        self.logger = logging.getLogger('utils.Visualizer')
        
        # Try to import matplotlib
        try:
            import matplotlib.pyplot as plt
            import matplotlib
            self.plt = plt
            self.matplotlib = matplotlib
            
            if style != 'default':
                plt.style.use(style)
            
            self.available = True
            self.logger.info("Visualizer initialized with matplotlib")
        except ImportError:
            self.plt = None
            self.matplotlib = None
            self.available = False
            self.logger.warning("Matplotlib not available - visualization disabled")
    
    def plot_metrics(self, metrics: Dict[str, List[float]], 
                    title: str = "Metrics",
                    xlabel: str = "Step",
                    ylabel: str = "Value",
                    save_path: Optional[str] = None):
        """
        Plot multiple metrics on the same graph.
        
        Args:
            metrics (Dict): Dictionary of metric_name -> values
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            save_path (str, optional): Path to save plot
        """
        if not self.available or self.plt is None:
            self.logger.warning("Visualization not available")
            return
        
        fig, ax = self.plt.subplots(figsize=(10, 6))
        
        for name, values in metrics.items():
            ax.plot(values, label=name, linewidth=2)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.plt.tight_layout()
        
        if save_path:
            self.plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Plot saved to {save_path}")
        else:
            self.plt.show()
        
        self.plt.close()
    
    def plot_learning_curve(self, rewards: List[float],
                           window: int = 100,
                           title: str = "Learning Curve",
                           save_path: Optional[str] = None):
        """
        Plot learning curve with moving average.
        
        Args:
            rewards (List): Episode rewards
            window (int): Moving average window size
            title (str): Plot title
            save_path (str, optional): Path to save plot
        """
        if not self.available or self.plt is None:
            self.logger.warning("Visualization not available")
            return
        
        fig, ax = self.plt.subplots(figsize=(10, 6))
        
        # Raw rewards
        ax.plot(rewards, alpha=0.3, color='blue', label='Episode Reward')
        
        # Moving average
        if len(rewards) >= window:
            moving_avg = np.convolve(rewards, np.ones(window)/window, mode='valid')
            ax.plot(range(window-1, len(rewards)), moving_avg, 
                   color='red', linewidth=2, label=f'{window}-Episode Moving Average')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('Episode', fontsize=12)
        ax.set_ylabel('Reward', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        
        self.plt.tight_layout()
        
        if save_path:
            self.plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Learning curve saved to {save_path}")
        else:
            self.plt.show()
        
        self.plt.close()
    
    def plot_trajectory(self, positions: np.ndarray,
                       goals: Optional[np.ndarray] = None,
                       title: str = "Agent Trajectory",
                       save_path: Optional[str] = None):
        """
        Plot agent trajectory in 2D space.
        
        Args:
            positions (np.ndarray): Array of (x, y) positions
            goals (np.ndarray, optional): Goal positions
            title (str): Plot title
            save_path (str, optional): Path to save plot
        """
        if not self.available or self.plt is None:
            self.logger.warning("Visualization not available")
            return
        
        fig, ax = self.plt.subplots(figsize=(8, 8))
        
        # Plot trajectory
        ax.plot(positions[:, 0], positions[:, 1], 
               'b-', linewidth=2, label='Trajectory')
        
        # Mark start and end
        ax.plot(positions[0, 0], positions[0, 1], 
               'go', markersize=10, label='Start')
        ax.plot(positions[-1, 0], positions[-1, 1], 
               'ro', markersize=10, label='End')
        
        # Plot goals if provided
        if goals is not None:
            ax.plot(goals[:, 0], goals[:, 1], 
                   'r*', markersize=15, label='Goals')
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position', fontsize=12)
        ax.set_ylabel('Y Position', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        self.plt.tight_layout()
        
        if save_path:
            self.plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Trajectory plot saved to {save_path}")
        else:
            self.plt.show()
        
        self.plt.close()
    
    def plot_heatmap(self, data: np.ndarray,
                    title: str = "Heatmap",
                    xlabel: str = "X",
                    ylabel: str = "Y",
                    save_path: Optional[str] = None):
        """
        Plot 2D heatmap.
        
        Args:
            data (np.ndarray): 2D array of values
            title (str): Plot title
            xlabel (str): X-axis label
            ylabel (str): Y-axis label
            save_path (str, optional): Path to save plot
        """
        if not self.available or self.plt is None:
            self.logger.warning("Visualization not available")
            return
        
        fig, ax = self.plt.subplots(figsize=(10, 8))
        
        im = ax.imshow(data, cmap='viridis', aspect='auto')
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel(xlabel, fontsize=12)
        ax.set_ylabel(ylabel, fontsize=12)
        
        # Add colorbar
        self.plt.colorbar(im, ax=ax)
        
        self.plt.tight_layout()
        
        if save_path:
            self.plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Heatmap saved to {save_path}")
        else:
            self.plt.show()
        
        self.plt.close()
    
    def plot_multi_agent_trajectories(self, agent_positions: List[np.ndarray],
                                     colors: Optional[List[str]] = None,
                                     title: str = "Multi-Agent Trajectories",
                                     save_path: Optional[str] = None):
        """
        Plot trajectories for multiple agents.
        
        Args:
            agent_positions (List[np.ndarray]): List of position arrays for each agent
            colors (List[str], optional): Colors for each agent
            title (str): Plot title
            save_path (str, optional): Path to save plot
        """
        if not self.available or self.plt is None:
            self.logger.warning("Visualization not available")
            return
        
        fig, ax = self.plt.subplots(figsize=(10, 10))
        
        if colors is None:
            colors = ['b', 'r', 'g', 'orange', 'purple', 'brown', 'pink']
        
        for i, positions in enumerate(agent_positions):
            color = colors[i % len(colors)]
            ax.plot(positions[:, 0], positions[:, 1], 
                   color=color, linewidth=2, label=f'Agent {i}')
            ax.plot(positions[0, 0], positions[0, 1], 
                   'o', color=color, markersize=8)
            ax.plot(positions[-1, 0], positions[-1, 1], 
                   's', color=color, markersize=8)
        
        ax.set_title(title, fontsize=14, fontweight='bold')
        ax.set_xlabel('X Position', fontsize=12)
        ax.set_ylabel('Y Position', fontsize=12)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.axis('equal')
        
        self.plt.tight_layout()
        
        if save_path:
            self.plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Multi-agent trajectories saved to {save_path}")
        else:
            self.plt.show()
        
        self.plt.close()
    
    def create_dashboard(self, metrics_dict: Dict[str, Any],
                        layout: Tuple[int, int] = (2, 2),
                        title: str = "Dashboard",
                        save_path: Optional[str] = None):
        """
        Create a multi-plot dashboard.
        
        Args:
            metrics_dict (Dict): Dictionary of plot_name -> data
            layout (Tuple): Grid layout (rows, cols)
            title (str): Dashboard title
            save_path (str, optional): Path to save dashboard
        """
        if not self.available or self.plt is None or self.plt is None:
            self.logger.warning("Visualization not available")
            return
        
        rows, cols = layout
        fig, axes = self.plt.subplots(rows, cols, figsize=(15, 10))
        fig.suptitle(title, fontsize=16, fontweight='bold')
        
        if rows == 1 and cols == 1:
            axes = np.array([[axes]])
        elif rows == 1 or cols == 1:
            axes = axes.reshape(rows, cols)
        
        plot_items = list(metrics_dict.items())
        
        for idx in range(rows * cols):
            row = idx // cols
            col = idx % cols
            ax = axes[row, col]
            
            if idx < len(plot_items):
                name, data = plot_items[idx]
                
                if isinstance(data, (list, np.ndarray)):
                    ax.plot(data, linewidth=2)
                    ax.set_title(name)
                    ax.grid(True, alpha=0.3)
                else:
                    ax.text(0.5, 0.5, f"{name}\n{data}", 
                           ha='center', va='center', fontsize=12)
                    ax.axis('off')
            else:
                ax.axis('off')
        
        self.plt.tight_layout()
        
        if save_path:
            self.plt.savefig(save_path, dpi=300, bbox_inches='tight')
            self.logger.info(f"Dashboard saved to {save_path}")
        else:
            self.plt.show()
        
        self.plt.close()
    
    def __repr__(self) -> str:
        """String representation of visualizer."""
        status = "available" if self.available else "unavailable"
        return f"Visualizer(status='{status}', style='{self.style}')"
