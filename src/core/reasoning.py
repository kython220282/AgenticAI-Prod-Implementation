"""
Reasoning Module
================

This module implements reasoning engines for logical inference, causal reasoning,
and knowledge-based decision making.

Purpose:
--------
- Perform logical inference (forward/backward chaining)
- Implement causal reasoning
- Handle uncertainty and probabilistic reasoning
- Support analogical reasoning

Usage:
------
    from core import ReasoningEngine
    
    engine = ReasoningEngine(method='forward_chaining')
    
    # Add facts and rules
    engine.add_fact("sky", "blue")
    engine.add_rule(
        premises=[("sky", "blue")],
        conclusion=("weather", "clear")
    )
    
    # Perform inference
    conclusions = engine.infer()
    
    # Query knowledge
    result = engine.query("weather")

Key Features:
------------
- Multiple reasoning strategies
- Rule-based inference
- Probabilistic reasoning with uncertainty
- Explanation generation
"""

from typing import Any, Dict, List, Optional, Tuple, Callable
import logging
from collections import defaultdict


class ReasoningEngine:
    """
    Reasoning engine for logical inference and knowledge-based reasoning.
    
    Supports forward chaining, backward chaining, and probabilistic reasoning.
    """
    
    def __init__(self, method: str = 'forward_chaining', max_depth: int = 10):
        """
        Initialize the reasoning engine.
        
        Args:
            method (str): Reasoning method ('forward_chaining', 'backward_chaining', 'probabilistic')
            max_depth (int): Maximum inference depth
        """
        self.method = method
        self.max_depth = max_depth
        self.logger = logging.getLogger('core.ReasoningEngine')
        
        # Knowledge base
        self.facts = set()  # Known facts
        self.rules = []  # Inference rules
        self.confidences = {}  # Fact confidence scores
        
        # Inference tracking
        self.inference_chain = []
        self.derived_facts = set()
        
        self.logger.info(f"Reasoning engine initialized - Method: {method}")
    
    def add_fact(self, subject: str, predicate: str, confidence: float = 1.0):
        """
        Add a fact to the knowledge base.
        
        Args:
            subject (str): Subject of the fact
            predicate (str): Predicate/property of the subject
            confidence (float): Confidence in the fact (0-1)
        """
        fact = (subject, predicate)
        self.facts.add(fact)
        self.confidences[fact] = confidence
        self.logger.debug(f"Added fact: {subject} -> {predicate} (confidence: {confidence})")
    
    def add_rule(self, premises: List[Tuple[str, str]], 
                 conclusion: Tuple[str, str],
                 confidence: float = 1.0):
        """
        Add an inference rule to the knowledge base.
        
        Args:
            premises (List[Tuple]): List of (subject, predicate) tuples required
            conclusion (Tuple): (subject, predicate) that can be inferred
            confidence (float): Rule confidence/strength
        """
        rule = {
            'premises': premises,
            'conclusion': conclusion,
            'confidence': confidence
        }
        self.rules.append(rule)
        self.logger.debug(f"Added rule: {premises} -> {conclusion}")
    
    def add_custom_rule(self, name: str, condition: Callable, action: Callable):
        """
        Add a custom rule with arbitrary condition and action functions.
        
        Args:
            name (str): Rule identifier
            condition (Callable): Function that returns True if rule applies
            action (Callable): Function to execute when rule fires
        """
        rule = {
            'name': name,
            'type': 'custom',
            'condition': condition,
            'action': action
        }
        self.rules.append(rule)
        self.logger.debug(f"Added custom rule: {name}")
    
    def infer(self) -> List[Tuple[str, str]]:
        """
        Perform inference to derive new facts.
        
        Returns:
            List of newly derived facts
        """
        self.derived_facts.clear()
        self.inference_chain.clear()
        
        if self.method == 'forward_chaining':
            return self._forward_chaining()
        elif self.method == 'backward_chaining':
            return self._backward_chaining()
        elif self.method == 'probabilistic':
            return self._probabilistic_reasoning()
        else:
            self.logger.warning(f"Unknown reasoning method: {self.method}")
            return []
    
    def _forward_chaining(self) -> List[Tuple[str, str]]:
        """
        Forward chaining: Start from facts and derive conclusions.
        
        Returns:
            List of derived facts
        """
        self.logger.info("Performing forward chaining inference")
        
        changed = True
        depth = 0
        
        while changed and depth < self.max_depth:
            changed = False
            depth += 1
            
            for rule in self.rules:
                if rule.get('type') == 'custom':
                    # Handle custom rules
                    if rule['condition'](self):
                        rule['action'](self)
                        changed = True
                    continue
                
                # Check if all premises are satisfied
                premises = rule['premises']
                all_satisfied = all(premise in self.facts for premise in premises)
                
                if all_satisfied:
                    conclusion = rule['conclusion']
                    
                    # Check if conclusion is new
                    if conclusion not in self.facts:
                        # Calculate confidence
                        premise_confidences = [self.confidences.get(p, 1.0) for p in premises]
                        rule_confidence = rule.get('confidence', 1.0)
                        conclusion_confidence = min(premise_confidences) * rule_confidence
                        
                        # Add derived fact
                        self.facts.add(conclusion)
                        self.confidences[conclusion] = conclusion_confidence
                        self.derived_facts.add(conclusion)
                        
                        # Record inference step
                        self.inference_chain.append({
                            'depth': depth,
                            'premises': premises,
                            'conclusion': conclusion,
                            'confidence': conclusion_confidence
                        })
                        
                        changed = True
                        self.logger.debug(f"Derived: {conclusion} (confidence: {conclusion_confidence:.3f})")
        
        self.logger.info(f"Forward chaining complete - Derived {len(self.derived_facts)} new facts")
        return list(self.derived_facts)
    
    def _backward_chaining(self, goal: Optional[Tuple[str, str]] = None) -> List[Tuple[str, str]]:
        """
        Backward chaining: Start from goal and work backward.
        
        Args:
            goal (Tuple, optional): Goal to prove
            
        Returns:
            List of facts needed to prove goal
        """
        self.logger.info("Performing backward chaining inference")
        
        # Placeholder implementation
        # In practice, implement goal-driven reasoning
        
        return []
    
    def _probabilistic_reasoning(self) -> List[Tuple[str, str]]:
        """
        Probabilistic reasoning with uncertainty.
        
        Returns:
            List of derived facts with probabilities
        """
        self.logger.info("Performing probabilistic reasoning")
        
        # Implement Bayesian inference or similar
        # This is a placeholder
        
        return []
    
    def query(self, subject: str) -> List[Tuple[str, float]]:
        """
        Query the knowledge base for facts about a subject.
        
        Args:
            subject (str): Subject to query
            
        Returns:
            List of (predicate, confidence) tuples
        """
        results = []
        
        for fact in self.facts:
            if fact[0] == subject:
                predicate = fact[1]
                confidence = self.confidences.get(fact, 1.0)
                results.append((predicate, confidence))
        
        self.logger.debug(f"Query '{subject}' returned {len(results)} results")
        return results
    
    def explain(self, fact: Tuple[str, str]) -> str:
        """
        Generate an explanation for how a fact was derived.
        
        Args:
            fact (Tuple): Fact to explain
            
        Returns:
            str: Explanation of reasoning chain
        """
        if fact not in self.derived_facts:
            return f"Fact {fact} is not a derived fact (may be asserted or not known)"
        
        # Find inference chain that led to this fact
        explanation_parts = [f"Explanation for {fact}:"]
        
        for step in self.inference_chain:
            if step['conclusion'] == fact:
                premises_str = ", ".join([f"{s}->{p}" for s, p in step['premises']])
                explanation_parts.append(
                    f"  Depth {step['depth']}: From {premises_str} "
                    f"inferred {fact[0]}->{fact[1]} "
                    f"(confidence: {step['confidence']:.3f})"
                )
        
        return "\n".join(explanation_parts)
    
    def check_consistency(self) -> bool:
        """
        Check if the knowledge base is consistent.
        
        Returns:
            bool: True if consistent, False otherwise
        """
        # Check for contradictions
        # This is a simplified check
        
        predicates_by_subject = defaultdict(set)
        
        for subject, predicate in self.facts:
            predicates_by_subject[subject].add(predicate)
        
        # Check for contradictory predicates
        # Example: sky can't be both "blue" and "red" with high confidence
        
        return True  # Placeholder
    
    def clear(self):
        """Clear all facts and rules."""
        self.facts.clear()
        self.rules.clear()
        self.confidences.clear()
        self.inference_chain.clear()
        self.derived_facts.clear()
        self.logger.info("Knowledge base cleared")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get reasoning engine statistics."""
        return {
            'method': self.method,
            'max_depth': self.max_depth,
            'num_facts': len(self.facts),
            'num_rules': len(self.rules),
            'num_derived_facts': len(self.derived_facts),
            'inference_steps': len(self.inference_chain)
        }
    
    def __repr__(self) -> str:
        """String representation of reasoning engine."""
        return f"ReasoningEngine(method='{self.method}', facts={len(self.facts)}, rules={len(self.rules)})"
