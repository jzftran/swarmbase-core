from ..logging_utils import setup_logger as setup_logger
from _typeshed import Incomplete
from agency_swarm.agents.agent import Agent

def log_method(logger): ...

class LoggedAgent(Agent):
    name: Incomplete
    logger: Incomplete
    def __init__(self, *args, **kwargs) -> None: ...
    def __getattribute__(self, name): ...
