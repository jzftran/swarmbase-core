"""swarmbasecore.clients

This module defines client classes that facilitate communication with the SwarmBase Flask app.
Each client is responsible for making API requests to manage resources such as
agents, tools, frameworks, and swarms.
The clients provide a structured way to interact with the underlying RESTful services.

Key Classes:
- BaseClient: An abstract base class that provides common functionality for 
  all client classes, including methods for creating, listing, retrieving, 
  updating, and deleting resources.
- AgentClient: A client for managing agent resources, extending the BaseClient 
  with methods specific to agent operations, such as assigning tools and 
  managing relationships.
- FrameworkClient: A client for managing framework resources, providing methods 
  to add and remove swarms from frameworks.
- SwarmClient: A client for managing swarm resources, including methods for 
  adding and removing agents from swarms.
- ToolClient: A client for managing tool resources, with methods for creating 
  and manipulating tools.

Usage:
To use the clients, instantiate the appropriate client class with the base URL 
of the API, and then call the provided methods to interact with the resources.

Example:
    from swarmbasecore.clients import AgentClient

    agent_client = AgentClient(base_url="127.0.0.1:5000")
    new_agent = agent_client.create(data={"name": "Agent 1", "description": "First agent"})
"""

from abc import ABC
from typing import Any, Dict

from .utils import make_request


class BaseClient(ABC):
    def __init__(self, base_url: str, resource: str):
        self.base_url = base_url
        self.client_url = f"{base_url}/api/{resource}"

    def create(self, data: Dict[str, Any]):
        return make_request("POST", self.client_url, data=data)

    def list(self):
        return make_request("GET", self.client_url)

    def get(self, resource_id: str):
        url = f"{self.client_url}/{resource_id}"
        return make_request("GET", url)

    def update(self, resource_id: str, data: Dict[str, Any]):
        url = f"{self.client_url}/{resource_id}"
        return make_request("PUT", url, data=data)

    def delete(self, resource_id: str):
        url = f"{self.client_url}/{resource_id}"
        return make_request("DELETE", url)


class AgentClient(BaseClient):
    def __init__(self, base_url: str):
        super().__init__(base_url, "agents")

    def assign_tool_to_agent(self, agent_id: str, tool_data: Dict[str, Any]):
        url = f"{self.client_url}/{agent_id}/tools"
        return make_request("POST", url, data=tool_data)

    def remove_tool_from_agent(self, agent_id: str, tool_data: Dict[str, Any]):
        url = f"{self.client_url}/{agent_id}/tools"
        return make_request("DELETE", url, data=tool_data)

    def get_tools(self, agent_id: str):
        url = f"{self.client_url}/{agent_id}/tools"
        return make_request("GET", url)

    def add_relationship(self, agent_id: str, data: Dict[str, Any]):
        url = f"{self.client_url}/{agent_id}/relationships"
        return make_request("POST", url, data=data)

    def get_relationships(self, agent_id: str):
        url = f"{self.client_url}/{agent_id}/relationships"
        return make_request("GET", url)

    def remove_relationship(self, agent_id: str, related_agent_id: str):
        url = f"{self.client_url}/{agent_id}/relationships/{related_agent_id}"
        return make_request("DELETE", url)


class FrameworkClient(BaseClient):
    def __init__(self, base_url: str):
        super().__init__(base_url, "frameworks")

    def add_swarm_to_framework(
        self,
        framework_id: str,
        swarm_data: Dict[str, Any],
    ):
        url = f"{self.client_url}/{framework_id}/swarms"
        return make_request("POST", url, data=swarm_data)

    def remove_swarm_from_framework(
        self,
        framework_id: str,
        swarm_data: Dict[str, Any],
    ):
        url = f"{self.client_url}/{framework_id}/swarms"
        return make_request("POST", url, data=swarm_data)

    def add_tool_to_framework(self, framework_id: str, tool_data):
        url = f"{self.client_url}/{framework_id}/tools"
        return make_request("POST", url, data=tool_data)


class SwarmClient(BaseClient):
    def __init__(self, base_url: str):
        super().__init__(base_url, "swarms")

    def add_agent_to_swarm(self, swarm_id: str, agent_data: Dict[str, Any]):
        url = f"{self.client_url}/{swarm_id}/agents"
        return make_request("POST", url, data=agent_data)

    def remove_agent_from_swarm(self, swarm_id: str, agent_data: Dict[str, Any]):
        url = f"{self.client_url}/{swarm_id}/agents"
        return make_request("DELETE", url, data=agent_data)


class ToolClient(BaseClient):
    def __init__(self, base_url: str):
        super().__init__(base_url, "tools")
