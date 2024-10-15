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

    Args:
    ----
        env_dir (PathLike): Path to the virtual environment directory.
        requirements_file (Optional[Path]): Path to the requirements.txt file.

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
    """Create a directory if it does not exist."""
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        logger.info(f"Created directory: {path}")
    else:
        logger.warning(f"Directory already exists: {path}")


def write_file(file_path: Path, content: str) -> None:
    """Write content to a file."""
    with file_path.open("w") as f:
        f.write(content)
    logger.info(f"Wrote to file: {file_path}")
