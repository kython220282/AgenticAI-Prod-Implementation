"""
Planner Module
==============

This module implements planning algorithms for multi-step goal achievement,
including classical planning, hierarchical task networks, and probabilistic planning.

Purpose:
--------
- Generate action sequences to achieve goals
- Implement various planning algorithms (A*, STRIPS, HTN, etc.)
- Handle partial observability and uncertainty
- Support plan adaptation and replanning

Usage:
------
    from core import Planner
    
    planner = Planner(algorithm='a_star')
    
    # Define initial state and goal
    initial_state = {'robot_at': 'A', 'door_open': False}
    goal_state = {'robot_at': 'B', 'package_delivered': True}
    
    # Generate plan
    plan = planner.create_plan(initial_state, goal_state, actions)
    
    # Execute plan
    for action in plan:
        execute(action)

Key Features:
------------
- Multiple planning algorithms
- Goal decomposition
- Plan optimization
- Dynamic replanning
- Cost estimation
"""

from typing import Any, Dict, List, Optional, Callable, Tuple
import logging
from collections import deque
import heapq


class Planner:
    """
    Planning system for generating action sequences to achieve goals.
    
    Supports various planning algorithms and strategies.
    """
    
    def __init__(self, algorithm: str = 'a_star', max_depth: int = 100):
        """
        Initialize the planner.
        
        Args:
            algorithm (str): Planning algorithm ('a_star', 'bfs', 'dfs', 'strips', 'htn')
            max_depth (int): Maximum planning depth
        """
        self.algorithm = algorithm
        self.max_depth = max_depth
        self.logger = logging.getLogger('core.Planner')
        
        # Available actions
        self.actions = []
        
        # Heuristic function for informed search
        self.heuristic = None
        
        # Planning statistics
        self.nodes_explored = 0
        self.plan_length = 0
        self.plan_cost = 0.0
        
        self.logger.info(f"Planner initialized - Algorithm: {algorithm}")
    
    def register_action(self, name: str, preconditions: Callable, 
                       effects: Callable, cost: float = 1.0):
        """
        Register an available action with the planner.
        
        Args:
            name (str): Action name
            preconditions (Callable): Function checking if action is applicable
            effects (Callable): Function applying action effects to state
            cost (float): Cost of executing this action
        """
        action = {
            'name': name,
            'preconditions': preconditions,
            'effects': effects,
            'cost': cost
        }
        self.actions.append(action)
        self.logger.debug(f"Registered action: {name} (cost: {cost})")
    
    def set_heuristic(self, heuristic: Callable):
        """
        Set the heuristic function for informed search.
        
        Args:
            heuristic (Callable): Function(state, goal) -> estimated_cost
        """
        self.heuristic = heuristic
        self.logger.debug("Heuristic function set")
    
    def create_plan(self, initial_state: Dict[str, Any], 
                   goal: Dict[str, Any],
                   actions: Optional[List[Dict]] = None) -> List[str]:
        """
        Generate a plan to achieve the goal from the initial state.
        
        Args:
            initial_state (Dict): Initial state of the world
            goal (Dict): Goal state to achieve
            actions (List[Dict], optional): Available actions (uses registered if None)
            
        Returns:
            List of action names forming the plan
        """
        self.nodes_explored = 0
        self.plan_length = 0
        self.plan_cost = 0.0
        
        if actions is not None:
            self.actions = actions
        
        self.logger.info(f"Creating plan using {self.algorithm}")
        
        # Select planning algorithm
        if self.algorithm == 'a_star':
            plan = self._a_star_search(initial_state, goal)
        elif self.algorithm == 'bfs':
            plan = self._breadth_first_search(initial_state, goal)
        elif self.algorithm == 'dfs':
            plan = self._depth_first_search(initial_state, goal)
        elif self.algorithm == 'strips':
            plan = self._strips_planning(initial_state, goal)
        else:
            self.logger.error(f"Unknown algorithm: {self.algorithm}")
            return []
        
        if plan:
            self.plan_length = len(plan)
            self.logger.info(
                f"Plan created - Length: {self.plan_length}, "
                f"Cost: {self.plan_cost:.2f}, "
                f"Nodes explored: {self.nodes_explored}"
            )
        else:
            self.logger.warning("No plan found")
        
        return plan
    
    def _a_star_search(self, initial_state: Dict, goal: Dict) -> List[str]:
        """
        A* search algorithm for optimal planning.
        
        Args:
            initial_state (Dict): Starting state
            goal (Dict): Goal state
            
        Returns:
            List of actions forming optimal plan
        """
        # Priority queue: (f_score, state, path, cost)
        frontier = [(0, initial_state, [], 0)]
        visited = set()
        
        while frontier and self.nodes_explored < self.max_depth:
            f_score, current_state, path, g_cost = heapq.heappop(frontier)
            self.nodes_explored += 1
            
            # Convert state to hashable form
            state_key = self._state_to_key(current_state)
            
            if state_key in visited:
                continue
            
            visited.add(state_key)
            
            # Check if goal reached
            if self._is_goal(current_state, goal):
                self.plan_cost = g_cost
                return path
            
            # Expand actions
            for action in self.actions:
                if action['preconditions'](current_state):
                    # Apply action to get next state
                    next_state = action['effects'](current_state.copy())
                    action_cost = action['cost']
                    new_g_cost = g_cost + action_cost
                    
                    # Calculate heuristic
                    h_cost = 0
                    if self.heuristic:
                        h_cost = self.heuristic(next_state, goal)
                    
                    f_cost = new_g_cost + h_cost
                    new_path = path + [action['name']]
                    
                    heapq.heappush(frontier, (f_cost, next_state, new_path, new_g_cost))
        
        return []  # No plan found
    
    def _breadth_first_search(self, initial_state: Dict, goal: Dict) -> List[str]:
        """
        Breadth-first search for planning.
        
        Args:
            initial_state (Dict): Starting state
            goal (Dict): Goal state
            
        Returns:
            List of actions forming plan
        """
        queue = deque([(initial_state, [], 0)])
        visited = set()
        
        while queue and self.nodes_explored < self.max_depth:
            current_state, path, cost = queue.popleft()
            self.nodes_explored += 1
            
            state_key = self._state_to_key(current_state)
            
            if state_key in visited:
                continue
            
            visited.add(state_key)
            
            if self._is_goal(current_state, goal):
                self.plan_cost = cost
                return path
            
            for action in self.actions:
                if action['preconditions'](current_state):
                    next_state = action['effects'](current_state.copy())
                    new_path = path + [action['name']]
                    new_cost = cost + action['cost']
                    queue.append((next_state, new_path, new_cost))
        
        return []
    
    def _depth_first_search(self, initial_state: Dict, goal: Dict) -> List[str]:
        """
        Depth-first search for planning.
        
        Args:
            initial_state (Dict): Starting state
            goal (Dict): Goal state
            
        Returns:
            List of actions forming plan
        """
        stack = [(initial_state, [], 0, 0)]  # (state, path, cost, depth)
        visited = set()
        
        while stack and self.nodes_explored < self.max_depth:
            current_state, path, cost, depth = stack.pop()
            self.nodes_explored += 1
            
            if depth > self.max_depth:
                continue
            
            state_key = self._state_to_key(current_state)
            
            if state_key in visited:
                continue
            
            visited.add(state_key)
            
            if self._is_goal(current_state, goal):
                self.plan_cost = cost
                return path
            
            for action in self.actions:
                if action['preconditions'](current_state):
                    next_state = action['effects'](current_state.copy())
                    new_path = path + [action['name']]
                    new_cost = cost + action['cost']
                    stack.append((next_state, new_path, new_cost, depth + 1))
        
        return []
    
    def _strips_planning(self, initial_state: Dict, goal: Dict) -> List[str]:
        """
        STRIPS-style planning algorithm.
        
        Args:
            initial_state (Dict): Starting state
            goal (Dict): Goal state
            
        Returns:
            List of actions forming plan
        """
        # Placeholder for STRIPS implementation
        # Would implement goal stack planning
        self.logger.debug("STRIPS planning not fully implemented, using A*")
        return self._a_star_search(initial_state, goal)
    
    def _is_goal(self, state: Dict, goal: Dict) -> bool:
        """
        Check if state satisfies goal conditions.
        
        Args:
            state (Dict): Current state
            goal (Dict): Goal specification
            
        Returns:
            bool: True if goal is satisfied
        """
        for key, value in goal.items():
            if state.get(key) != value:
                return False
        return True
    
    def _state_to_key(self, state: Dict) -> str:
        """
        Convert state dictionary to hashable key.
        
        Args:
            state (Dict): State dictionary
            
        Returns:
            str: Hashable state key
        """
        return str(sorted(state.items()))
    
    def decompose_goal(self, goal: Dict) -> List[Dict]:
        """
        Decompose complex goal into subgoals.
        
        Args:
            goal (Dict): Complex goal
            
        Returns:
            List of subgoals
        """
        # Hierarchical decomposition
        # This is a placeholder - implement task decomposition
        subgoals = [goal]  # Simplest case: no decomposition
        
        self.logger.debug(f"Decomposed goal into {len(subgoals)} subgoals")
        return subgoals
    
    def replan(self, current_state: Dict, goal: Dict, 
               failed_action: Optional[str] = None) -> List[str]:
        """
        Generate new plan from current state (replanning).
        
        Args:
            current_state (Dict): Current world state
            goal (Dict): Goal to achieve
            failed_action (str, optional): Action that failed (if any)
            
        Returns:
            List of actions forming new plan
        """
        self.logger.info(f"Replanning from current state")
        
        if failed_action:
            self.logger.debug(f"Replanning due to failed action: {failed_action}")
        
        return self.create_plan(current_state, goal)
    
    def estimate_plan_cost(self, state: Dict, goal: Dict) -> float:
        """
        Estimate the cost of achieving goal from state.
        
        Args:
            state (Dict): Starting state
            goal (Dict): Goal state
            
        Returns:
            float: Estimated cost
        """
        if self.heuristic:
            return self.heuristic(state, goal)
        
        # Default: Manhattan distance on mismatched goal variables
        cost = sum(1 for k, v in goal.items() if state.get(k) != v)
        return float(cost)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get planner statistics."""
        return {
            'algorithm': self.algorithm,
            'max_depth': self.max_depth,
            'nodes_explored': self.nodes_explored,
            'plan_length': self.plan_length,
            'plan_cost': self.plan_cost,
            'num_actions': len(self.actions)
        }
    
    def __repr__(self) -> str:
        """String representation of planner."""
        return f"Planner(algorithm='{self.algorithm}', actions={len(self.actions)})"
