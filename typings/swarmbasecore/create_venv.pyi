from _typeshed import Incomplete
from os import PathLike
from pathlib import Path

logger: Incomplete

def create_virtualenv(env_dir: PathLike, requirements_file: Path | None = None): ...
def create_directory(path: Path) -> None: ...
def write_file(file_path: Path, content: str) -> None: ...
