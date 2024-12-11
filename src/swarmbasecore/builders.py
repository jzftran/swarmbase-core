"""swarmbasecore.builders

This module defines builder classes for constructing different types of 
products within the SwarmBase Core framework. Builders provide an interface
for creating instances of products such as **Tool**, **Agent**, *Framework**,
and **Swarm**.

Key Classes:

Products:
    - **Product**: A base class representing a generic product with common attributes 
    and validation logic.
    - Tool: A subclass of Product representing a tool with additional attributes 
    like description, version, and code.
    - Agent: A subclass of Product representing an agent with attributes for 
    relationships and tools.
    - Framework: A subclass of Product representing a framework.
    - Swarm: A subclass of Product representing a collection of agents and tools.

Builders:
    - BaseBuilder: A generic builder class for creating products, providing methods 
    to set attributes and build the product.
    - ToolBuilder: A builder specifically for creating Tool instances.
    - AgentBuilder: A builder specifically for creating Agent instances.
    - FrameworkBuilder: A builder specifically for creating Framework instances.
    - SwarmBuilder: A builder specifically for creating Swarm instances.

Usage:
To use the builders, instantiate the appropriate builder class and use its 
methods to set the desired attributes before calling the build method to 
create the product instance.

Example:
    from swarmbasecore.builders import ToolBuilder
    from swarmbasecore.clients import ToolClient

    tool_builder = ToolBuilder(client=ToolClient(base_url="127.0.0.1:5000"))
    tool = (tool_builder
            .set_name("Example Tool")
            .set_description("This is an example tool.")
            .set_version("1.0.0")
            .build())
"""

import keyword
import re
from dataclasses import asdict, field
from datetime import datetime
from typing import (
    Any,
    ClassVar,
    Dict,
    Generic,
    List,
    Optional,
    TypeVar,
)

from pydantic import ConfigDict, field_validator
from pydantic.dataclasses import dataclass

from .agency_chart import AgencyChart
from .clients import (
    AgentClient,
    BaseClient,
    FrameworkClient,
    SwarmClient,
    ToolClient,
)
from .utils import RelationshipType, AgentRelationship, pascal_case, snake_case


@dataclass
class Product:
    id: Optional[str] = None
    _name: str = field(init=False)
    count: ClassVar[int] = 0
    extra_attributes: Dict[str, Any] = field(default_factory=dict)

    @field_validator("_name")
    def validate_variable_name(cls, v: str) -> str:
        """Validate whether _name can be used as a valid Python identifier."""
        if not re.match(r"^[a-zA-Z_][a-zA-Z0-9_ ]*$", v):
            raise ValueError("Provided name is not a valid Python identifier.")
        if keyword.iskeyword(v):
            raise ValueError("Provided name is a reserved keyword in Python.")

        return v

    @property
    def name(self):
        return self._name

    @property
    def instance_name(self) -> str:
        return (
            snake_case(self.name)
            if self.name
            else snake_case(f"{self.__class__.__name__}{Product.count}")
        )

    @name.setter
    def name(self, value: str) -> None:
        self._name = value

    def __post_init__(self):
        self.name = self.__class__.__name__


T = TypeVar("T", bound="Product")


@dataclass(
    config=ConfigDict(arbitrary_types_allowed=True, revalidate_instances="always"),
)
class BaseBuilder(Generic[T]):
    client: BaseClient
    _product_type: Any = field(init=False)
    _product: T = field(init=False)

    def __post_init__(self):
        self.reset()

    def reset(self) -> None:
        self._product = self._product_type()

    def set_id(self, id: str):
        self._product.id = id
        return self

    def set_name(self, name: str):
        self._product.name = name
        return self

    def set_extra_attributes(self, extra_attributes):
        self._product.extra_attributes = extra_attributes
        return self

    def build(self):
        return self.client.create(asdict(self._product))

    @property
    def product(self) -> T:
        product = self._product
        self.reset()
        return product


@dataclass
class Tool(Product):
    description: Optional[str] = None
    version: Optional[str] = None
    code: Optional[str] = None

    def __post_init__(self):
        Tool.count += 1
        super().__post_init__()

    @property
    def class_name(self):
        return (
            pascal_case(self.name)
            if (self.name or self.name == "")
            else f"Tool{Tool.count}"
        )


@dataclass
class ToolBuilder(BaseBuilder[Tool]):
    client: ToolClient

    def __post_init__(self):
        self._product_type = Tool
        super().__post_init__()

    def set_description(self, description):
        self._product.description = description

    def set_version(self, version):
        self._product.version = version

    def set_code(self, code):
        self._product.code = code

    def from_id(self, id: str):
        data = self.client.get(id)
        if data:
            self.set_id(data.get("id"))
            self.set_name(data.get("name"))
            self.set_description(data.get("description"))

            self.set_extra_attributes(data.get("extra_attributes"))
            newest_code_data = (
                sorted(
                    data["code_versions"],
                    key=lambda item: datetime.strptime(
                        item["created_at"],
                        "%Y-%m-%dT%H:%M:%S.%f",
                    ),
                )[-1]
                if data["code_versions"]
                else {}
            )
            self.set_version(newest_code_data.get("version"))
            self.set_code(newest_code_data.get("code"))
        return self


@dataclass
class Agent(Product):
    description: Optional[str] = None
    instructions: Optional[str] = None
    relationships: List[AgentRelationship] = field(default_factory=list)
    tools: List[Tool] = field(default_factory=list)

    def __post_init__(self):
        Agent.count += 1
        super().__post_init__()

    @property
    def class_name(self):
        return (
            pascal_case(self.name)
            if (self.name or self.name == "")
            else f"Agent{Agent.count}"
        )


@dataclass
class AgentBuilder(BaseBuilder[Agent]):
    client: AgentClient

    def __post_init__(self):
        self._product_type = Agent
        super().__post_init__()

    def set_description(self, description: str):
        self._product.description = description
        return self

    def set_instructions(self, instructions: str):
        self._product.instructions = instructions
        return self

    def add_relationship(self, relationship: AgentRelationship):
        self._product.relationships.append(relationship)
        return self

    def add_tool(self, tool: Tool):
        self._product.tools.append(tool)
        return self

    def from_id(self, id: str):
        data = self.client.get(id)
        tool_builder = ToolBuilder(ToolClient(self.client.base_url))

        if data:
            self.set_id(data.get("id"))
            self.set_name(data.get("name"))
            self.set_description(data.get("description"))
            self.set_instructions(data.get("instructions"))
            self.set_extra_attributes(data.get("extra_attributes"))

            for _ in data.get("relationships"):
                relationship = AgentRelationship(
                    RelationshipType(_["relationship_type"]),
                    _.get("source_agent_id"),
                    _.get("target_agent_id"),
                )
                self.add_relationship(relationship)

            for tool_id in data.get("tools"):
                self.add_tool(tool_builder.from_id(tool_id).product)

        return self


@dataclass
class Framework(Product):
    def __post_init__(self):
        super().__post_init__()


@dataclass
class FrameworkBuilder(BaseBuilder[Framework]):
    client: FrameworkClient
    _product: Framework

    def __post_init__(self):
        self._product_type = Framework
        super().__post_init__()


@dataclass
class Swarm(Product):
    parent_id: Optional[str] = None
    agents: Dict[str, Agent] = field(default_factory=dict)
    tools: Dict[str, Tool] = field(default_factory=dict)
    agency_chart = AgencyChart()

    def __post_init__(self):
        super().__post_init__()


@dataclass
class SwarmBuilder(BaseBuilder[Swarm]):
    client: SwarmClient

    def __post_init__(self):
        self._product_type = Swarm
        super().__post_init__()

    def add_agent(self, agent: Agent):

        if agent.id:
            self._product.agents[agent.id] = agent

        return self

    def add_agents_relationship(self, relationship: AgentRelationship):
        self._product.agency_chart.add_relationship(relationship)
        return self

    def add_tool(self, tool: Tool):
        if tool.id:
            self._product.tools[tool.id] = tool
        return self

    def from_id(self, id: str):
        data = self.client.get(id)

        agent_builder = AgentBuilder(AgentClient(self.client.base_url))
        if data:
            self.set_id(data.get("id"))
            self.set_name(data.get("name"))

            for agent_data in data.get("agents"):
                agent: Agent = agent_builder.from_id(agent_data.get("id")).product
                for rel in agent.relationships:
                    self.add_agents_relationship(rel)

                    # adds source and target agents to dict
                    self.add_agent(agent_builder.from_id(rel.source_agent_id).product)
                    self.add_agent(agent_builder.from_id(rel.target_agent_id).product)

                for tool in agent.tools:
                    self.add_tool(tool)

            self.set_extra_attributes(data.get("extra_attributes"))

        return self
