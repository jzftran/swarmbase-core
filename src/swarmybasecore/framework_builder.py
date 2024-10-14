# %%
from pathlib import Path
from typing import Optional, Protocol

from .create_venv import create_directory, create_virtualenv, write_file
from .builders import Agent, Swarm, Tool
from .utils import snake_case


class FrameworkCreator(Protocol):
    """Generic interface for swarm framework."""

    @classmethod
    def swarm_as_string(cls, swarm: Swarm) -> str: ...

    """Generate a string representation of the Swarm as an Agency.

        Args:
        ----
            swarm (Swarm): The Swarm object to represent.

        Returns:
        -------
            str: The formatted string representing the Swarm.

        """

    @classmethod
    def agent_as_string(agent: Agent) -> str: ...

    """Generate a string representation of an Agent.

        Args:
        ----
            agent (Agent): The Agent object to represent.

        Returns:
        -------
            str: The formatted string representing the Agent.

        """

    @classmethod
    def tool_as_string(tool: Tool) -> str: ...

    """Generate a string representation of a Tool.

        Args:
        ----
            tool (Tool): The Tool object to represent.

        Returns:
        -------
            str: The formatted string representing the Tool.

        """

    @classmethod
    def create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None: ...

    @staticmethod
    def setup_virtualenv(swarm_name: str, requirements_file: Optional[Path]) -> None:
        """Create a virtual environment for the Swarm."""
        venv_path = Path("./") / swarm_name / ".venv"
        create_virtualenv(venv_path, requirements_file=requirements_file)


class SwarmBaseCreator(FrameworkCreator):

    @staticmethod
    def swarm_as_string(swarm: Swarm) -> str:

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
            f"from agents.{agent.instance_name} import {agent.instance_name}"
            for agent in swarm.agents.values()
        )

        return f"""from swarmybasecore.agency_swarm.swarmy_agency import SwarmyAgency
{agents_imports}
{swarm.instance_name} = SwarmyAgency({str(agency_relationships).replace("'", "")})
"""

    @staticmethod
    def agent_as_string(agent: Agent) -> str:

        tool_imports = "\n".join(
            f"from tools.{tool.instance_name} import {tool.class_name}"
            for tool in agent.tools
        )

        agent_description = f'"""{agent.description}"""' if agent.description else ""
        agent_instructions = agent.instuctions or ""

        tool_names = ", ".join([tool.class_name for tool in agent.tools])

        return f"""from swarmybasecore._agency_swarm.swarmy_agent import LoggedAgent
{tool_imports}
{agent.instance_name} = LoggedAgent(
    name="{agent.name}",
    description={agent_description},
    instuctions="{agent_instructions}",
    tools=[{tool_names}],
    model="{agent.extra_attributes.get("model", "gpt-4o")}"
)"""

    @staticmethod
    def tool_as_string(tool: Tool) -> str:

        tool_description = f'"""{tool.description}"""' if tool.description else ""
        return f"""from swarmybasecore._agency_swarm.swarmy_tool import LoggedBaseTool
class {tool.class_name}(LoggedBaseTool):
    {tool_description}
    {tool.code}
    """

    @classmethod
    def create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None:
        """Create the directory structure and files for the Swarm and its agents/tools."""
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


# %%
class LangchainCreator(FrameworkCreator):
    @staticmethod
    def swarm_as_string(swarm: Swarm) -> str:

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
        """Generuje reprezentację tekstową agenta w formacie Langchain."""
        # TODO: Zaimplementuj logikę generowania kodu agenta dla Langchain
        from .langchain_framework.model_providers import get_llm

        return f"""
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from pydantic import BaseModel
from typing import Literal

class routeResponse(BaseModel):
    next: Literal[*options]

system_prompt = \"\"\"{agent.instuctions}\"\"\"

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
        """Generuje reprezentację tekstową narzędzia w formacie Langchain."""
        return ""

    @classmethod
    def create_swarm_files(cls, swarm: Swarm, base_path: Path) -> None:
        """Create the directory structure and files for the Swarm and its agents/tools."""
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
    @staticmethod
    def get_creator(creator_type: str) -> FrameworkCreator:
        if creator_type == "swarmybasecore":
            return SwarmBaseCreator
        if creator_type == "langchain":
            return LangchainCreator
        else:
            # TODO implement other methods
            raise ValueError(f"Unknown creator type: {creator_type}")


# %%
# LangchainCreator.create_swarm_files(swarm, base_path=Path("./"))
