"""swarmbasecore.agency_chart

This module defines the AgencyChart class, which represents a directed graph structure
for managing relationships between agents. It provides functionality to add, remove, 
and query relationships, making it suitable for applications that require tracking 
interactions among various entities.

Key Features:
- Add and manage directed and bidirectional relationships between agents.
- Remove agents and their associated relationships from the graph.
- Check connectivity between agents and find paths in the graph.
- Identify top-level agents without incoming edges.

Usage:
To use the AgencyChart class, create an instance and utilize its methods to manage 
agent relationships as needed.

Example:
    from swarmbasecore.agency_chart import AgencyChart
    from swarmbasecore.utils import AgentRelationship, RelationshipType

    chart = AgencyChart()
    relationship = AgentRelationship(source_agent_id="agent1", target_agent_id="agent2", 
                                      relationship_type=RelationshipType.COLLABORATES)
    chart.add_relationship(relationship)
"""

from collections import defaultdict
from typing import Union, Annotated, Set
from .utils import AgentRelationship, RelationshipType


class AgencyChart:
    """AgencyChart data structure for representing agent relationships and tools in a directed graph."""

    def __init__(self):
        self.graph: defaultdict[str, Set[str]] = defaultdict(set)

    def add_relationship(self, relationship: AgentRelationship):
        """Add a directed relationship from source to target.
        For 'collaborates', add bidirectional connections.
        """
        if relationship.relationship_type == RelationshipType.COLLABORATES:
            self._add_bidirectional(
                relationship.source_agent_id,
                relationship.target_agent_id,
            )
        elif relationship.relationship_type == RelationshipType.SUPERVISES:
            self._add_directed(
                relationship.source_agent_id,
                relationship.target_agent_id,
            )
        # will add default bidirectional connection
        else:
            self._add_bidirectional(
                relationship.source_agent_id,
                relationship.target_agent_id,
            )

    def _add_directed(
        self,
        source: Annotated[str, "agent_id"],
        target: Annotated[str, "agent_id"],
    ):
        """Add a single directed relationship from source to target"""
        self.graph[source].add(target)

    def _add_bidirectional(
        self,
        source: Annotated[str, "agent_id"],
        target: Annotated[str, "agent_id"],
    ):
        """Add bidirectional relationship (A -> B and B -> A)"""
        self._add_directed(source, target)
        self._add_directed(target, source)

    def remove_agent(self, agent: Annotated[str, "agent_id"]):
        """Remove an agent and all its associated relationships"""
        # Remove all edges where agent is the source
        if agent in self.graph:
            del self.graph[agent]

        # Remove all edges where agent is the target
        for targets in self.graph.values():
            targets.discard(agent)

    def is_connected(
        self,
        source: Annotated[str, "agent_id"],
        target: Annotated[str, "agent_id"],
    ):
        """Check if there is a direct connection from source to target"""
        return source in self.graph and target in self.graph[source]

    def find_path(
        self,
        source: Annotated[str, "agent_id"],
        target: Annotated[str, "agent_id"],
        path=[],
    ):
        """Find a path from source to target (may not be the shortest)"""
        path = path + [source]
        if source == target:
            return path
        if source not in self.graph:
            return None
        for node in self.graph[source]:
            if node not in path:
                new_path = self.find_path(node, target, path)
                if new_path:
                    return new_path
        return None

    @property
    def manager_agent(self) -> Union[Annotated[str, "agent_id"], None]:
        """Find all agents that do not have any incoming edges."""
        targets = set()
        for target_set in self.graph.values():
            targets.update(target_set)

        no_incoming_edges = [agent for agent in self.graph if agent not in targets]
        if len(no_incoming_edges) > 1:
            raise Exception("Swarm cannot contain multiple top-level agents.")
        if not no_incoming_edges:
            return None
        return no_incoming_edges.pop()

    def __str__(self):
        return f"{self.__class__.__name__}({dict(self.graph)})"
