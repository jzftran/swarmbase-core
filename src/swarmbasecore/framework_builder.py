"""swarmbasecore.framework_builder

This module provides the FrameworkCreator interface and its implementations for 
creating and managing swarm frameworks. It includes functionality for generating 
string representations of swarms, agents, and tools, as well as creating the 
necessary directory structure and files for the exported swarms.

Key Classes:
- FrameworkCreator: A generic interface for swarm framework creation.
- SwarmBaseCreator: An implementation of FrameworkCreator for the SwarmBase framework.
- LangchainCreator: An implementation of FrameworkCreator for the Langchain framework.
- CreatorFactory: A factory class for obtaining the appropriate creator based on type.

Usage:
To create a swarm framework, instantiate the desired creator class and call 
the appropriate methods to generate the necessary files and structures.

Example:
    from swarmbasecore.framework_builder import CreatorFactory

    creator = CreatorFactory.get_creator("swarmbasecore")
    creator.create_swarm_files(swarm, base_path=Path("./"))
"""

from pathlib import Path
from typing import Optional, Protocol

from .create_venv import create_directory, create_virtualenv, write_file
from .builders import Agent, Swarm, Tool
from .utils import snake_case


class FrameworkCreator(Protocol):
    """Generic interface for swarm framework.

    This interface defines methods for generating string representations of
    swarms, agents, and tools, as well as creating swarm files.

    Methods:
        swarm_as_string(swarm: Swarm) -> str: Generate a string representation of the Swarm.
        agent_as_string(agent: Agent) -> str: Generate a string representation of an Agent.
        tool_as_string(tool: Tool) -> str: Generate a string representation of a Tool.
        create_swarm_files(swarm: Swarm, base_path: Path) -> None: Create files for the Swarm.
    """

    @classmethod
    def swarm_as_string(cls, swarm: Swarm) -> str: ...

    @classmethod
    def agent_as_string(agent: Agent) -> str: ...

    @classmethod
    def tool_as_string(tool: Tool) -> str: ...

    @classmethod
    def create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None: ...

    @staticmethod
    def setup_virtualenv(swarm_name: str, requirements_file: Optional[Path]) -> None:
        """Create a virtual environment for the Swarm.

        This method sets up a virtual environment in the specified directory.

        Args:
            swarm_name (str): The name of the swarm for which the virtual environment is created.
            requirements_file (Optional[Path]): The path to the requirements file, if any.
        """
        venv_path = Path("./") / swarm_name / ".venv"
        create_virtualenv(venv_path, requirements_file=requirements_file)


class SwarmBaseCreator(FrameworkCreator):
    """Implementation of FrameworkCreator for the SwarmBase framework.

    This class provides methods to generate string representations of swarms,
    agents, and tools specific to the SwarmBase framework.

    Methods:
        swarm_as_string(swarm: Swarm) -> str: Generate a string representation of the Swarm.
        agent_as_string(agent: Agent) -> str: Generate a string representation of an Agent.
        tool_as_string(tool: Tool) -> str: Generate a string representation of a Tool.
        create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None: Create files for the Swarm.
    """

    @staticmethod
    def swarm_as_string(swarm: Swarm) -> str:
        """Generate a string representation of the Swarm.

        Args:
            swarm (Swarm): The Swarm object to represent.

        Returns:
            str: The formatted string representing the Swarm.
        """
        agency_relationships = []
        if swarm.agency_chart.manager_agent:
            agency_relationships.append(
                swarm.agents[swarm.agency_chart.manager_agent].instance_name,
            )

        for source, targets in swarm.agency_chart.graph.items():
            source_agent = snake_case(swarm.agents[source].instance_name)
            for target in targets:
                target_agent = snake_case(swarm.agents[target].instance_name)
                agency_relationships.append([source_agent, target_agent])

        agents_imports = "\n".join(
            f"from agents.{agent.class_name} import {agent.class_name}"
            for agent in swarm.agents.values()
        )

        agents_init = "\n".join(
            f"{agent.instance_name} = {agent.class_name}()"
            for agent in swarm.agents.values()
        )

        return f"""from swarmbasecore.agency_swarm_framework import SwarmyAgency
{agents_imports}

{agents_init}

{swarm.instance_name} = SwarmyAgency({str(agency_relationships).replace("'", "")})
"""

    @staticmethod
    def agent_as_string(agent: Agent) -> str:
        """Generate a string representation of an Agent.

        Args:
            agent (Agent): The Agent object to represent.

        Returns:
            str: The formatted string representing the Agent.
        """
        tool_imports = "\n".join(
            f"from tools.{tool.instance_name} import {tool.class_name}"
            for tool in agent.tools
        )

        agent_description = f'"""{agent.description}"""' if agent.description else '""'
        agent_instructions = agent.instructions or ""

        tool_names = ", ".join([tool.class_name for tool in agent.tools])

        return f"""from swarmbasecore.agency_swarm_framework import LoggedAgent
{tool_imports}
{agent.instance_name} = LoggedAgent(
    name="{agent.name}",
    description={agent_description},
    instructions="{agent_instructions}",
    tools=[{tool_names}],
    model="{agent.extra_attributes.get("model", "gpt-4o")}"
)"""

    @staticmethod
    def tool_as_string(tool: Tool) -> str:
        """Generate a string representation of a Tool.

        Args:
            tool (Tool): The Tool object to represent.

        Returns:
            str: The formatted string representing the Tool.
        """
        tool_description = f'"""{tool.description}"""' if tool.description else ""
        return f"""from swarmbasecore.agency_swarm_framework import LoggedBaseTool
class {tool.class_name}(LoggedBaseTool):
    {tool_description}
    {tool.code}
    """

    @classmethod
    def create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None:
        """Create the directory structure and files for the Swarm and its agents/tools.

        Args:
            swarm (Swarm): The Swarm object for which files are created.
            base_path (Path): The base path where the files will be created.
        """
        swarm_path = base_path / swarm.instance_name
        create_directory(swarm_path)

        # Create __main__.py for the Swarm
        main_content = f"""from {swarm.instance_name} import {swarm.instance_name}

origins = [
    "http://localhost",
    "http://localhost:8080",
    "http://wails.localhost:34115",
    "http://localhost:5173",
    "wails://wails.localhost:34115",
]

{swarm.instance_name}.serve_agency(origins)
"""
        write_file(swarm_path / "__main__.py", main_content)
        write_file(swarm_path / f"{swarm.instance_name}.py", cls.swarm_as_string(swarm))

        # Create agents' directories and files
        for agent in swarm.agents.values():
            agent_path = swarm_path / "agents" / agent.class_name
            create_directory(agent_path)
            write_file(
                agent_path / "__init__.py",
                f"from agents.{agent.class_name} import {agent.class_name}",
            )
            write_file(
                agent_path / f"{agent.class_name}.py",
                cls.agent_as_string(agent),
            )

        # Create tools' directories and files
        for tool in swarm.tools.values():
            tool_path = swarm_path / "tools" / tool.instance_name
            create_directory(tool_path)
            write_file(
                tool_path / "__init__.py",
                f"from .{tool.instance_name} import {tool.class_name}",
            )
            write_file(tool_path / f"{tool.instance_name}.py", cls.tool_as_string(tool))


# %%
class LangchainCreator(FrameworkCreator):
    """Implementation of FrameworkCreator for the Langchain framework.

    This class provides methods to generate string representations of swarms,
    agents, and tools specific to the Langchain framework.

    Methods:
        swarm_as_string(swarm: Swarm) -> str: Generate a string representation of the Swarm.
        agent_as_string(agent: Agent) -> str: Generate a string representation of an Agent.
        tool_as_string(tool: Tool) -> str: Generate a string representation of a Tool.
        create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None: Create files for the Swarm.
    """

    @staticmethod
    def swarm_as_string(swarm: Swarm) -> str:
        """Generate a string representation of the Swarm.

        Args:
            swarm (Swarm): The Swarm object to represent.

        Returns:
            str: The formatted string representing the Swarm.
        """
        agents_imports = "\n".join(
            f"from agents.{agent.instance_name} import {agent.instance_name}"
            for agent in swarm.agents.values()
        )

        agent_nodes = "\n".join(
            f'workflow.add_node("{agent.name}", {agent.instance_name})'
            for agent in swarm.agents.values()
        )

        manager_agent = swarm.agents[swarm.agency_chart.manager_agent].instance_name

        agency_relationships = dict()
        for source, targets in swarm.agency_chart.graph.items():
            agency_relationships[swarm.agents[source].instance_name] = {
                swarm.agents[target].instance_name for target in targets
            }

        return f"""import functools
import operator
from typing import Sequence, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph import END, StateGraph, START
from langchain_core.messages import HumanMessage

{agents_imports}

# The agent state is the input to each node in the graph
class AgentState(TypedDict):
    # The annotation tells the graph that new messages will always
    # be added to the current states
    messages: Annotated[Sequence[BaseMessage], operator.add]
    # The 'next' field indicates where to route to next
    next: str

workflow = StateGraph(AgentState)
{agent_nodes}

agency_chart = {agency_relationships}

for source, targets in agency_chart.items():
    print(source, targets)
    for target in targets:
        workflow.add_edge(target, source)

    conditional_map = {{k: k for k in targets}}
    if source == '{manager_agent}':
        conditional_map["FINISH"] = END
    print(conditional_map)
    workflow.add_conditional_edges(source, lambda x: x["next"], conditional_map)
workflow.add_edge(START, '{manager_agent}')
{swarm.instance_name} = workflow.compile()
"""

    @classmethod
    def agent_as_string(cls, agent: Agent) -> str:
        """Generate a string representation of an Agent in Langchain format.

        Args:
            agent (Agent): The Agent object to represent.

        Returns:
            str: The formatted string representing the Agent in Langchain format.
        """
        # TODO: Zaimplementuj logikę generowania kodu agenta dla Langchain
        from .langchain_framework.model_providers import get_llm

        return f"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal

class routeResponse(BaseModel):
    next: Literal[*options]

system_prompt = \"\"\"{agent.instructions}\"\"\"

prompt = ChatPromptTemplate.from_messages(
[
    ("system", system_prompt),
    MessagesPlaceholder(variable_name="messages"),
]
)

model = {get_llm(agent.extra_attributes.get("model", "gpt-4o"))}

def {agent.instance_name}(state):
    {agent.instance_name}_chain = (
        prompt
        | model.with_structured_output(routeResponse)
    )
    return {agent.instance_name}_chain.invoke(state)


"""

    @classmethod
    def tool_as_string(cls, tool: Tool) -> str:
        """Generate a string representation of a Tool in Langchain format.

        Args:
            tool (Tool): The Tool object to represent.

        Returns:
            str: The formatted string representing the Tool in Langchain format.
        """
        return ""

    @classmethod
    def create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None:
        """Create the directory structure and files for the Swarm and its agents/tools.

        Args:
            swarm (Swarm): The Swarm object for which files are created.
            base_path (Path): The base path where the files will be created.
        """
        swarm_path = base_path / swarm.instance_name
        create_directory(swarm_path)

        # Create __main__.py for the Swarm
        main_content = f"""from {swarm.instance_name} import {swarm.instance_name}

for s in {swarm.instance_name}.stream(
    {{"messages": [HumanMessage(content="Write a brief research report on pikas. Ask researcher to tell Coder to write hello pika in Python.")]}},
    {{"recursion_limit": 100}},
):
    if "__end__" not in s:
        print(s)
        print("----")
"""
        write_file(swarm_path / "__main__.py", main_content)
        write_file(swarm_path / f"{swarm.instance_name}.py", cls.swarm_as_string(swarm))

        # Create agents' directories and files
        for agent in swarm.agents.values():
            agent_path = swarm_path / "agents" / agent.instance_name
            create_directory(agent_path)
            write_file(
                agent_path / "__init__.py",
                f"from agents.{agent.instance_name} import {agent.instance_name}",
            )
            write_file(
                agent_path / f"{agent.instance_name}.py",
                cls.agent_as_string(agent),
            )

        # Create tools' directories and files
        for tool in swarm.tools.values():
            tool_path = swarm_path / "tools" / tool.instance_name
            create_directory(tool_path)
            write_file(
                tool_path / "__init__.py",
                f"from .{tool.instance_name} import {tool.class_name}",
            )
            write_file(tool_path / f"{tool.instance_name}.py", cls.tool_as_string(tool))


class CreatorFactory:
    """Factory class for obtaining the appropriate creator based on type.

    This class provides a method to get the appropriate creator class
    based on the specified creator type.

    Methods:
        get_creator(creator_type: str) -> FrameworkCreator: Get the creator class based on type.
    """

    @staticmethod
    def get_creator(creator_type: str) -> FrameworkCreator:
        """Get the creator class based on the specified type.

        Args:
            creator_type (str): The type of creator to obtain.

        Returns:
            FrameworkCreator: The appropriate creator class.

        Raises:
            ValueError: If the specified creator type is unknown.
        """
        if creator_type == "swarmbasecore":
            return SwarmBaseCreator
        if creator_type == "langchain":
            return LangchainCreator
        else:
            # TODO implement other methods
            raise ValueError(f"Unknown creator type: {creator_type}")
