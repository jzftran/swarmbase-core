from functools import wraps

from agency_swarm.agents.agent import Agent

from ..logging_utils import setup_logger


def log_method(logger):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Calling {func.__name__}")
            try:
                result = func(*args, **kwargs)
                logger.info(f"{func.__name__} completed successfully")
                return result
            except Exception as e:
                logger.error(f"Error in {func.__name__}: {e!s}")
                raise

        return wrapper

    return decorator


class LoggedAgent(Agent):
    def __init__(self, *args, **kwargs):
        self.name = kwargs.get("name", "agent")
        self.logger = setup_logger(self.__class__.__name__, self.name)
        super().__init__(*args, **kwargs)
        self._wrap_methods()

    def _wrap_methods(self):
        for attr_name in dir(self):
            if not attr_name.startswith("_") and attr_name != "assistant":
                try:
                    attr = super().__getattribute__(attr_name)
                    if callable(attr) and not isinstance(attr, property):
                        setattr(self, attr_name, log_method(self.logger)(attr))
                except Exception:
                    self.logger.exception(
                        "Attribure '%s' can't be accessed.",
                        attr_name,
                    )

    def __getattribute__(self, name):
        attr = super().__getattribute__(name)
        if (
            name != "assistant"
            and callable(attr)
            and not name.startswith("_")
            and not isinstance(attr, property)
        ):
            return log_method(self.logger)(attr)
        return attr
