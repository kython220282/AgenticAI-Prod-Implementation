"""
Decision Maker Module
=====================

This module implements decision-making frameworks for agents, including
utility-based, rule-based, and multi-criteria decision making.

Purpose:
--------
- Evaluate multiple action alternatives
- Implement various decision strategies
- Handle uncertainty in decision making
- Support multi-objective optimization

Usage:
------
    from core import DecisionMaker
    
    dm = DecisionMaker(strategy='utility_based')
    
    # Define utility function
    dm.set_utility_function(lambda state, action: calculate_utility(state, action))
    
    # Make decision
    action = dm.decide(current_state, available_actions)
    
    # Multi-criteria decision
    criteria = {'safety': 0.4, 'efficiency': 0.3, 'cost': 0.3}
    action = dm.multi_criteria_decide(state, actions, criteria)

Key Features:
------------
- Utility-based decision making
- Rule-based decisions
- Multi-criteria analysis
- Risk assessment
- Decision explanation
"""

from typing import Any, Dict, List, Optional, Callable, Tuple
import logging
import numpy as np


class DecisionMaker:
    """
    Decision-making system for agents.
    
    Implements various decision strategies and evaluation methods.
    """
    
    def __init__(self, strategy: str = 'utility_based', risk_tolerance: float = 0.5):
        """
        Initialize the decision maker.
        
        Args:
            strategy (str): Decision strategy ('utility_based', 'rule_based', 'multi_criteria')
            risk_tolerance (float): Risk tolerance level (0-1, higher = more risk-seeking)
        """
        self.strategy = strategy
        self.risk_tolerance = risk_tolerance
        self.logger = logging.getLogger('core.DecisionMaker')
        
        # Decision functions
        self.utility_function = None
        self.rules = []
        self.criteria_weights = {}
        
        # Decision history
        self.decision_history = []
        
        self.logger.info(f"DecisionMaker initialized - Strategy: {strategy}")
    
    def set_utility_function(self, utility_fn: Callable):
        """
        Set the utility function for utility-based decisions.
        
        Args:
            utility_fn (Callable): Function(state, action) -> utility_value
        """
        self.utility_function = utility_fn
        self.logger.debug("Utility function set")
    
    def add_rule(self, condition: Callable, action: Any, priority: int = 0):
        """
        Add a decision rule for rule-based decisions.
        
        Args:
            condition (Callable): Function(state) -> bool
            action: Action to take when condition is True
            priority (int): Rule priority (higher = more important)
        """
        rule = {
            'condition': condition,
            'action': action,
            'priority': priority
        }
        self.rules.append(rule)
        self.rules.sort(key=lambda r: r['priority'], reverse=True)
        self.logger.debug(f"Added rule with priority {priority}")
    
    def decide(self, state: Dict[str, Any], 
              actions: List[Any],
              context: Optional[Dict] = None) -> Any:
        """
        Make a decision given current state and available actions.
        
        Args:
            state (Dict): Current state
            actions (List): Available actions to choose from
            context (Dict, optional): Additional context for decision
            
        Returns:
            Selected action
        """
        if not actions:
            self.logger.warning("No actions available for decision")
            return None
        
        self.logger.debug(f"Making decision with {len(actions)} options")
        
        # Choose decision method based on strategy
        if self.strategy == 'utility_based':
            action = self._utility_based_decision(state, actions)
        elif self.strategy == 'rule_based':
            action = self._rule_based_decision(state, actions)
        elif self.strategy == 'multi_criteria':
            action = self._multi_criteria_decision(state, actions)
        else:
            self.logger.warning(f"Unknown strategy: {self.strategy}, using random")
            action = np.random.choice(actions)
        
        # Record decision
        self.decision_history.append({
            'state': state,
            'actions': actions,
            'chosen_action': action,
            'strategy': self.strategy,
            'context': context
        })
        
        return action
    
    def _utility_based_decision(self, state: Dict, actions: List[Any]) -> Any:
        """
        Make decision by maximizing expected utility.
        
        Args:
            state (Dict): Current state
            actions (List): Available actions
            
        Returns:
            Action with highest expected utility
        """
        if not self.utility_function:
            self.logger.warning("No utility function set, using random choice")
            return np.random.choice(actions)
        
        # Calculate utility for each action
        utilities = []
        for action in actions:
            utility = self.utility_function(state, action)
            utilities.append((utility, action))
        
        # Sort by utility and select best
        utilities.sort(key=lambda x: x[0], reverse=True)
        best_utility, best_action = utilities[0]
        
        self.logger.debug(f"Selected action with utility: {best_utility:.3f}")
        return best_action
    
    def _rule_based_decision(self, state: Dict, actions: List[Any]) -> Any:
        """
        Make decision using rule-based system.
        
        Args:
            state (Dict): Current state
            actions (List): Available actions
            
        Returns:
            Action from matching rule
        """
        # Check rules in priority order
        for rule in self.rules:
            if rule['condition'](state):
                action = rule['action']
                
                # Verify action is available
                if action in actions:
                    self.logger.debug(f"Rule matched, selecting action: {action}")
                    return action
        
        # No rule matched, use fallback
        self.logger.debug("No rule matched, using random action")
        return np.random.choice(actions)
    
    def _multi_criteria_decision(self, state: Dict, actions: List[Any]) -> Any:
        """
        Make decision using multi-criteria analysis.
        
        Args:
            state (Dict): Current state
            actions (List): Available actions
            
        Returns:
            Best action according to weighted criteria
        """
        if not self.criteria_weights:
            self.logger.warning("No criteria weights set")
            return np.random.choice(actions)
        
        # Evaluate each action on all criteria
        action_scores = []
        
        for action in actions:
            total_score = 0.0
            
            for criterion, weight in self.criteria_weights.items():
                # Get criterion evaluation function
                eval_fn = getattr(self, f'_evaluate_{criterion}', None)
                
                if eval_fn:
                    score = eval_fn(state, action)
                    total_score += weight * score
            
            action_scores.append((total_score, action))
        
        # Select action with highest total score
        action_scores.sort(key=lambda x: x[0], reverse=True)
        best_score, best_action = action_scores[0]
        
        self.logger.debug(f"Multi-criteria decision - Score: {best_score:.3f}")
        return best_action
    
    def set_criteria_weights(self, criteria: Dict[str, float]):
        """
        Set weights for multi-criteria decision making.
        
        Args:
            criteria (Dict): Dictionary of criterion_name -> weight
                           Weights should sum to 1.0
        """
        # Normalize weights
        total = sum(criteria.values())
        self.criteria_weights = {k: v/total for k, v in criteria.items()}
        
        self.logger.info(f"Set criteria weights: {self.criteria_weights}")
    
    def evaluate_risk(self, state: Dict, action: Any) -> float:
        """
        Evaluate the risk of taking an action.
        
        Args:
            state (Dict): Current state
            action: Action to evaluate
            
        Returns:
            float: Risk score (0 = no risk, 1 = high risk)
        """
        # Placeholder risk evaluation
        # In practice, this would evaluate various risk factors
        
        risk = 0.5  # Default moderate risk
        return risk
    
    def decide_under_uncertainty(self, state: Dict, 
                                 actions: List[Any],
                                 outcomes_probabilities: Dict[Any, List[Tuple[Any, float]]]) -> Any:
        """
        Make decision under uncertainty using expected utility.
        
        Args:
            state (Dict): Current state
            actions (List): Available actions
            outcomes_probabilities (Dict): For each action, list of (outcome, probability) tuples
            
        Returns:
            Action maximizing expected utility
        """
        if not self.utility_function:
            self.logger.warning("No utility function for uncertainty handling")
            return np.random.choice(actions)
        
        expected_utilities = []
        
        for action in actions:
            outcomes = outcomes_probabilities.get(action, [])
            expected_utility = 0.0
            
            for outcome, prob in outcomes:
                utility = self.utility_function(outcome, action)
                expected_utility += prob * utility
            
            # Adjust for risk tolerance
            # Risk-averse: penalize variance
            # Risk-seeking: bonus for variance
            variance = np.var([self.utility_function(o, action) for o, p in outcomes])
            risk_adjustment = (self.risk_tolerance - 0.5) * variance
            
            expected_utility += risk_adjustment
            expected_utilities.append((expected_utility, action))
        
        # Select action with highest expected utility
        expected_utilities.sort(key=lambda x: x[0], reverse=True)
        best_action = expected_utilities[0][1]
        
        self.logger.debug(f"Decision under uncertainty - Expected utility: {expected_utilities[0][0]:.3f}")
        return best_action
    
    def explain_decision(self, state: Dict, action: Any) -> str:
        """
        Generate explanation for why an action was chosen.
        
        Args:
            state (Dict): State in which decision was made
            action: Action that was chosen
            
        Returns:
            str: Human-readable explanation
        """
        explanation = f"Decision explanation for action: {action}\n"
        explanation += f"Strategy used: {self.strategy}\n"
        
        if self.strategy == 'utility_based' and self.utility_function:
            utility = self.utility_function(state, action)
            explanation += f"Utility value: {utility:.3f}\n"
        
        elif self.strategy == 'rule_based':
            for rule in self.rules:
                if rule['condition'](state) and rule['action'] == action:
                    explanation += f"Matched rule with priority {rule['priority']}\n"
                    break
        
        return explanation
    
    def get_decision_confidence(self, state: Dict, actions: List[Any]) -> float:
        """
        Get confidence level in the decision.
        
        Args:
            state (Dict): Current state
            actions (List): Available actions
            
        Returns:
            float: Confidence score (0-1)
        """
        if not actions:
            return 0.0
        
        if len(actions) == 1:
            return 1.0  # Only one option, fully confident
        
        # Calculate utility spread
        if self.utility_function:
            utilities = [self.utility_function(state, a) for a in actions]
            if max(utilities) > 0:
                # Confidence based on how much better best option is
                confidence = (max(utilities) - np.mean(utilities)) / max(utilities)
                return np.clip(confidence, 0.0, 1.0)
        
        return 0.5  # Medium confidence by default
    
    def clear_history(self):
        """Clear decision history."""
        self.decision_history.clear()
        self.logger.debug("Decision history cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get decision maker statistics."""
        return {
            'strategy': self.strategy,
            'risk_tolerance': self.risk_tolerance,
            'num_rules': len(self.rules),
            'num_criteria': len(self.criteria_weights),
            'decisions_made': len(self.decision_history),
            'has_utility_function': self.utility_function is not None
        }
    
    def __repr__(self) -> str:
        """String representation of decision maker."""
        return f"DecisionMaker(strategy='{self.strategy}', risk_tolerance={self.risk_tolerance})"
