"""
swarmbasecore.agency_swarm_framework.swarmy_tool

This module provides the LoggedBaseTool class, which extends the BaseTool class 
to include logging functionality. The LoggedBaseTool class uses a decorator to 
log the execution of its methods, including the method name, arguments, and 
results, as well as handling any exceptions that may occur during execution.

Key Classes:
- LoggedBaseTool: Inherits from BaseTool and adds logging capabilities to the 
  `run` method and potentially other methods.

Usage:
To create a subclass of LoggedBaseTool, simply inherit from it and define 
your methods. The `run` method will be automatically wrapped with logging 
functionality.

"""

from abc import ABC
from functools import wraps

from agency_swarm.tools.BaseTool import BaseTool

from ..logging_utils import setup_logger


def log_execution(logger, func):
    """Decorator for logging the execution of the `run` method.
    Logs the method name, arguments, and the result.
    """

    @wraps(func)
    def wrapper(self, *args, **kwargs):
        logger.info(
            f"Executing {func.__name__} of {self.__class__.__name__} with attributes: {self.__dict__.items()}",
        )
        try:
            result = func(self, *args, **kwargs)
            logger.info(
                f"{func.__name__} of {self.__class__.__name__} with attributes: {self.__dict__.items()} completed successfully. Result: {result}",
            )
            return result
        except Exception as e:
            logger.error(
                f"Error occurred in {func.__name__} of {self.__class__.__name__} with attributes: {self.__dict__.items()}: {e}",
            )
            raise

    return wrapper


class LoggedBaseTool(BaseTool, ABC):

    @classmethod
    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.logger = setup_logger("LoggedBaseTool", cls.__name__)
        # Apply the decorator to the `run` method if it exists
        if "run" in cls.__dict__:
            cls.run = log_execution(cls.logger, cls.run)
