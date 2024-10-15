from ..logging_utils import setup_logger as setup_logger
from abc import ABC
from agency_swarm.tools.BaseTool import BaseTool

def log_execution(logger, func): ...

class LoggedBaseTool(BaseTool, ABC):
    @classmethod
    def __init_subclass__(cls, **kwargs) -> None: ...
