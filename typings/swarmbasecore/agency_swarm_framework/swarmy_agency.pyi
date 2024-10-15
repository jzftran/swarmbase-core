import gradio as gr
from ..logging_utils import setup_logger as setup_logger
from _typeshed import Incomplete
from agency_swarm import Agency
from fastapi import Request as Request
from openai.types.beta.threads import Message as Message
from openai.types.beta.threads.runs import RunStep as RunStep
from openai.types.beta.threads.runs.tool_call import ToolCall as ToolCall

class SwarmyAgency(Agency):
    logger: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def log_message(self, message_log) -> None: ...
    message_output: Incomplete
    def demo_gradio(self, height: int = 450, dark_mode: bool = True) -> gr.Blocks: ...
    def serve_agency(self, origins: list[str], height: int = 450, dark_mode: bool = True, **kwargs): ...
