from _typeshed import Incomplete
from langchain_anthropic import ChatAnthropic as ChatAnthropic
from langchain_core.language_models.chat_models import BaseChatModel as BaseChatModel
from langchain_openai import ChatOpenAI as ChatOpenAI
from typing import NamedTuple

class LLMConfig(NamedTuple):
    provider: Incomplete
    provider_class: Incomplete
    args: Incomplete

LLM_MODELS: Incomplete

def get_llm(model_name) -> BaseChatModel: ...
