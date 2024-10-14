from collections import namedtuple

from langchain_anthropic import ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

# Define a simple namedtuple for each LLM configuration
LLMConfig = namedtuple("LLMConfig", ["provider", "provider_class", "args"])

# Define the mapping of model names to LLM configurations
LLM_MODELS = {
    "gpt-4o-mini": LLMConfig(
        provider="openai",
        provider_class="ChatOpenAI",
        args='{"model": "gpt-4o-mini"}',
    ),
    "gpt-4o": LLMConfig(
        provider="openai",
        provider_class="ChatOpenAI",
        args='{"model": "gpt-4o"}',
    ),
    "claude-2": LLMConfig(
        provider="anthropic",
        provider_class="ChatAnthropic",
        args='{"model": "claude-2"}',
    ),
}


def get_llm(model_name) -> BaseChatModel:
    # Get the LLM config from the dictionary
    config = LLM_MODELS.get(model_name)
    if config:
        # Instantiate the appropriate LLM class using the arguments
        return config.provider_class + "(**" + config.args + ")"
    raise ValueError(f"Model {model_name} not found")
