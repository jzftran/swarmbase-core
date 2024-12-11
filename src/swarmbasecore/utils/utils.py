# %%
from re import sub, split
from typing import NamedTuple
from enum import Enum
import requests


def snake_case(s):
    return "_".join(
        sub(
            "([A-Z][a-z]+)",
            r" \1",
            sub("([A-Z]+)", r" \1", s.replace("-", " ")),
        ).split(),
    ).lower()


def pascal_case(s):
    if s and s == "".join(
        word.capitalize() for word in split(r"([A-Z][^A-Z]*)", s) if word
    ):
        return s
    words = sub(r"(_|-| )+", " ", s).split()
    return "".join(word.capitalize() for word in words)


class RelationshipType(str, Enum):
    COLLABORATES = "collaborates"
    SUPERVISES = "supervises"


class AgentRelationship(NamedTuple):
    relationship_type: RelationshipType
    source_agent_id: str
    target_agent_id: str


def make_request(method, url, headers=None, data=None, params=None):
    headers = headers or {"Content-Type": "application/json"}
    response = requests.request(
        method,
        url,
        headers=headers,
        json=data,
        params=params,
    )
    response.raise_for_status()
    if response.content:
        response.raise_for_status()
        json_data = response.json()
        return json_data
    return None
