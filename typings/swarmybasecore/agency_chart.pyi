from .utils import AgentRelationship as AgentRelationship, RelationshipType as RelationshipType
from _typeshed import Incomplete
from typing import Annotated

class AgencyChart:
    graph: Incomplete
    def __init__(self) -> None: ...
    def add_relationship(self, relationship: AgentRelationship): ...
    def remove_agent(self, agent: Annotated[str, 'agent_id']): ...
    def is_connected(self, source: Annotated[str, 'agent_id'], target: Annotated[str, 'agent_id']): ...
    def find_path(self, source: Annotated[str, 'agent_id'], target: Annotated[str, 'agent_id'], path=[]): ...
    @property
    def manager_agent(self) -> Annotated[str, 'agent_id'] | None: ...