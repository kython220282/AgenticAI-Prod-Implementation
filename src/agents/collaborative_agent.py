"""
Collaborative Agent Module
==========================

This module implements an agent designed for multi-agent collaboration,
enabling coordination, communication, and cooperative problem-solving.

Purpose:
--------
- Enable multi-agent collaboration and coordination
- Implement communication protocols between agents
- Handle task allocation and distribution
- Resolve conflicts in cooperative settings

Usage:
------
    from agents import CollaborativeAgent
    
    config = {
        'team_size': 5,
        'communication_protocol': 'message_passing',
        'coordination_strategy': 'hierarchical'
    }
    
    # Create team of agents
    agents = [CollaborativeAgent(config, name=f"Agent_{i}") 
              for i in range(config['team_size'])]
    
    for agent in agents:
        agent.initialize()
        agent.set_team(agents)
    
    # Agents collaborate on task
    for agent in agents:
        action = agent.act(observation)
        agent.communicate(message, recipients)

Key Features:
------------
- Message passing between agents
- Task allocation and delegation
- Shared knowledge/belief systems
- Conflict resolution mechanisms
- Team coordination strategies
"""

from typing import Any, Dict, List, Optional
from .base_agent import BaseAgent


class CollaborativeAgent(BaseAgent):
    """
    An agent designed for multi-agent collaboration and coordination.
    
    This agent can communicate with other agents, share information,
    coordinate actions, and work together to achieve shared goals.
    """
    
    def __init__(self, config: Dict[str, Any], name: Optional[str] = None):
        """
        Initialize the collaborative agent.
        
        Args:
            config (Dict): Configuration including:
                - team_size: Expected number of agents in team
                - communication_protocol: How agents communicate
                - coordination_strategy: How team coordinates
                - conflict_resolution: How conflicts are resolved
            name (str, optional): Agent identifier
        """
        super().__init__(config, name)
        
        self.team_size = config.get('team_size', 5)
        self.communication_protocol = config.get('communication_protocol', 'message_passing')
        self.coordination_strategy = config.get('coordination_strategy', 'hierarchical')
        self.conflict_resolution = config.get('conflict_resolution', 'voting')
        
        # Team and communication
        self.team = []
        self.inbox = []
        self.outbox = []
        self.shared_knowledge = {}
        
        # Role and task management
        self.role = None
        self.assigned_tasks = []
        self.completed_tasks = []
        
    def initialize(self):
        """Initialize the collaborative agent's communication systems."""
        super().initialize()
        
        self.inbox = []
        self.outbox = []
        self.shared_knowledge = {}
        self.assigned_tasks = []
        self.completed_tasks = []
        
        self.logger.info(
            f"Collaborative agent initialized - Team size: {self.team_size}, "
            f"Protocol: {self.communication_protocol}"
        )
        
    def set_team(self, team: List['CollaborativeAgent']):
        """
        Set the team of agents this agent will collaborate with.
        
        Args:
            team: List of collaborative agents in the team
        """
        self.team = [agent for agent in team if agent != self]
        self.logger.info(f"Team set with {len(self.team)} other agents")
    
    def set_role(self, role: str):
        """
        Assign a role to this agent in the team.
        
        Args:
            role: Role identifier (e.g., 'leader', 'scout', 'executor')
        """
        self.role = role
        self.logger.info(f"Role assigned: {role}")
    
    def act(self, observation: Any) -> Any:
        """
        Decide on action considering team coordination.
        
        Args:
            observation: Current environment observation
            
        Returns:
            action: Coordinated action decision
        """
        if not self.initialized:
            raise RuntimeError("Agent must be initialized before acting")
        
        self.step_count += 1
        
        # Process incoming messages
        self._process_messages()
        
        # Coordinate with team based on strategy
        if self.coordination_strategy == 'hierarchical':
            action = self._hierarchical_coordination(observation)
        elif self.coordination_strategy == 'distributed':
            action = self._distributed_coordination(observation)
        else:
            action = self._default_action(observation)
        
        # Send messages to team if needed
        self._send_pending_messages()
        
        return action
    
    def _process_messages(self):
        """Process messages received from other agents."""
        while self.inbox:
            message = self.inbox.pop(0)
            self._handle_message(message)
    
    def _handle_message(self, message: Dict[str, Any]):
        """
        Handle a received message.
        
        Args:
            message: Message dictionary with type, content, sender, etc.
        """
        msg_type = message.get('type')
        sender = message.get('sender')
        content = message.get('content')
        
        self.logger.debug(f"Received {msg_type} message from {sender}")
        
        if msg_type == 'task_assignment':
            self.assigned_tasks.append(content)
        elif msg_type == 'knowledge_share':
            if content and isinstance(content, dict):
                self.shared_knowledge.update(content)
        elif msg_type == 'coordination':
            self._handle_coordination_message(content)
        elif msg_type == 'conflict':
            self._handle_conflict_message(content)
    
    def _handle_coordination_message(self, content: Any):
        """Handle coordination-related messages."""
        self.logger.debug(f"Handling coordination message: {content}")
    
    def _handle_conflict_message(self, content: Any):
        """Handle conflict-related messages."""
        self.logger.debug(f"Handling conflict message: {content}")
        
    def _hierarchical_coordination(self, observation: Any) -> Any:
        """
        Coordinate actions using hierarchical strategy.
        
        Args:
            observation: Current observation
            
        Returns:
            action: Coordinated action
        """
        # Leaders make high-level decisions, followers execute
        if self.role == 'leader':
            return self._leader_action(observation)
        else:
            return self._follower_action(observation)
    
    def _distributed_coordination(self, observation: Any) -> Any:
        """
        Coordinate actions using distributed strategy.
        
        Args:
            observation: Current observation
            
        Returns:
            action: Coordinated action
        """
        # All agents participate equally in decision-making
        return self._consensus_action(observation)
    
    def _leader_action(self, observation: Any) -> Any:
        """Action selection for leader role."""
        # Implement leader decision logic
        return 0  # Placeholder
    
    def _follower_action(self, observation: Any) -> Any:
        """Action selection for follower role."""
        # Execute assigned tasks
        if self.assigned_tasks:
            task = self.assigned_tasks[0]
            # Process task...
        return 0  # Placeholder
    
    def _consensus_action(self, observation: Any) -> Any:
        """Action selection through team consensus."""
        # Implement consensus mechanism
        return 0  # Placeholder
    
    def _default_action(self, observation: Any) -> Any:
        """Default action when no coordination strategy specified."""
        return 0  # Placeholder
    
    def communicate(self, message_type: str, content: Any, 
                   recipients: Optional[List['CollaborativeAgent']] = None):
        """
        Send a message to other agents.
        
        Args:
            message_type: Type of message ('task_assignment', 'knowledge_share', etc.)
            content: Message content
            recipients: List of recipient agents (None = broadcast to all)
        """
        message = {
            'type': message_type,
            'sender': self.name,
            'content': content
        }
        
        if recipients is None:
            recipients = self.team
        
        self.outbox.append((message, recipients))
        self.logger.debug(f"Queued {message_type} message for {len(recipients)} recipients")
    
    def _send_pending_messages(self):
        """Send all queued messages to recipients."""
        while self.outbox:
            message, recipients = self.outbox.pop(0)
            
            for recipient in recipients:
                recipient.receive_message(message)
    
    def receive_message(self, message: Dict[str, Any]):
        """
        Receive a message from another agent.
        
        Args:
            message: Message dictionary
        """
        self.inbox.append(message)
    
    def share_knowledge(self, knowledge: Dict[str, Any]):
        """
        Share knowledge with the team.
        
        Args:
            knowledge: Knowledge to share
        """
        self.communicate('knowledge_share', knowledge)
        self.logger.info(f"Shared knowledge with team: {list(knowledge.keys())}")
    
    def request_help(self, task: Any):
        """
        Request help from team members.
        
        Args:
            task: Task requiring assistance
        """
        self.communicate('help_request', task)
        self.logger.info(f"Requested help for task: {task}")
    
    def resolve_conflict(self, conflict: Dict[str, Any]) -> Any:
        """
        Resolve a conflict using configured resolution strategy.
        
        Args:
            conflict: Conflict specification
            
        Returns:
            resolution: Conflict resolution
        """
        if self.conflict_resolution == 'voting':
            return self._resolve_by_voting(conflict)
        elif self.conflict_resolution == 'hierarchy':
            return self._resolve_by_hierarchy(conflict)
        else:
            return self._resolve_by_negotiation(conflict)
    
    def _resolve_by_voting(self, conflict: Dict[str, Any]) -> Any:
        """Resolve conflict through voting."""
        self.logger.debug("Resolving conflict by voting")
        return None  # Placeholder
    
    def _resolve_by_hierarchy(self, conflict: Dict[str, Any]) -> Any:
        """Resolve conflict through hierarchy."""
        self.logger.debug("Resolving conflict by hierarchy")
        return None  # Placeholder
    
    def _resolve_by_negotiation(self, conflict: Dict[str, Any]) -> Any:
        """Resolve conflict through negotiation."""
        self.logger.debug("Resolving conflict by negotiation")
        return None  # Placeholder
    
    def learn(self, experience: Dict[str, Any]):
        """
        Learn from collaborative experience.
        
        Args:
            experience: Experience dictionary
        """
        # Learn from team outcomes
        self.logger.debug("Learning from collaborative experience")
        
        # Share successful strategies with team
        if experience.get('reward', 0) > 0:
            self.share_knowledge({'successful_strategy': experience})
    
    def reset(self):
        """Reset the collaborative agent."""
        super().reset()
        self.inbox = []
        self.outbox = []
        self.assigned_tasks = []
        
    def get_stats(self) -> Dict[str, Any]:
        """Get collaborative agent statistics."""
        stats = super().get_stats()
        stats.update({
            'role': self.role,
            'team_size': len(self.team),
            'pending_messages': len(self.inbox),
            'assigned_tasks': len(self.assigned_tasks),
            'completed_tasks': len(self.completed_tasks),
            'shared_knowledge_items': len(self.shared_knowledge)
        })
        return stats
