"""swarmbasecore.create_venv

This module provides functionality for creating and managing virtual environments 
for the exported swarms. It includes a function to create a Python virtual 
environment in a specified directory and install required packages from a 
requirements file if provided.

Key Functions:
- create_virtualenv: Creates a virtual environment in the specified directory. 
  It checks if the directory already exists, raises an exception if it does, 
  and uses the venv module to create the environment. If a requirements file 
  is provided, it installs the specified packages using pip.


Usage:
To create a virtual environment, call the `create_virtualenv` function with 
the desired directory and an optional requirements file.

Example:
    from swarmbasecore.create_venv import create_virtualenv
    from pathlib import Path

    create_virtualenv(Path("my_env"), requirements_file=Path("requirements.txt"))
"""

import logging
import subprocess
import venv
from os import PathLike
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Function to create a virtual environment
def create_virtualenv(env_dir: PathLike, requirements_file: Optional[Path] = None):
    """Create a virtual environment in the specified directory.

    This function checks if the specified directory already exists. If it does,
    an exception is raised. If not, it creates a virtual environment using the
    venv module. If a requirements file is provided, it installs the required
    packages using pip.

    Args:
        env_dir (PathLike):
            Path to the virtual environment directory.
        requirements_file (Optional[Path]):
            Path to the requirements.txt file containing the list of packages to install.

    Raises:
        Exception:
            If the specified directory already exists.
        subprocess.CalledProcessError:
            If the pip installation process fails.

    Example:
        create_virtualenv("my_env", requirements_file="requirements.txt")
    """

    # Check if the directory already exists
    if Path(env_dir).exists():
        raise Exception(
            f"The directory '{env_dir}' already exists. Please choose another location or remove it.",
        )

    # Create the virtual environment
    logger.info(f"Creating virtual environment at {env_dir}...")

    # Use venv to create the environment
    venv.create(env_dir, with_pip=True)

    logger.info(f"Virtual environment created successfully at {env_dir}")

    if requirements_file:
        logger.info(f"Installing required packages from {requirements_file}...")
        venv_python = Path(env_dir) / "Scripts" / "python"

        process = subprocess.Popen(
            [str(venv_python), "-m", "pip", "install", "-r", str(requirements_file)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            universal_newlines=True,
        )
        if process.stdout:
            for line in process.stdout:
                logger(line, end="")
        process.wait()
        if process.returncode != 0:
            raise subprocess.CalledProcessError(process.returncode, process.args)
        logger.info("Packages installed successfully")


def create_directory(path: Path) -> None:
    """Create a directory if it does not exist.

    This function checks if the specified directory exists. If it does not,
    it creates the directory along with any necessary parent directories.
    If the directory already exists, a warning is logged.

    Args:
        path (Path):
            The path to the directory to be created.
    """
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {path}")
    else:
        logger.warning(f"Directory already exists: {path}")


def write_file(file_path: Path, content: str) -> None:
    """Write content to a file.

    This function writes the specified content to a file at the given path.
    If the file already exists, it will be overwritten.

    Args:
        file_path (Path):
            The path to the file where content will be written.
        content (str):
            The content to write to the file.
    """
    with file_path.open("w", encoding="utf-8") as f:
        f.write(content)
    logger.info(f"Wrote to file: {file_path}")
