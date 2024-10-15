from _typeshed import Incomplete
from enum import Enum
from typing import NamedTuple

def snake_case(s): ...
def pascal_case(s): ...

class RelationshipType(str, Enum):
    COLLABORATES = 'collaborates'
    SUPERVISES = 'supervises'

class AgentRelationship(NamedTuple):
    relationship_type: RelationshipType
    source_agent_id: str
    target_agent_id: str

def make_request(method, url, headers: Incomplete | None = None, data: Incomplete | None = None, params: Incomplete | None = None): ...
