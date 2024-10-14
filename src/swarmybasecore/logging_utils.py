import logging
from typing import Optional


def setup_logger(class_name: str, name: Optional[str] = None):
    logger = logging.getLogger(f"{class_name}_{name}" if name else class_name)
    logger.setLevel(logging.INFO)

    class_name_lower = class_name.lower()
    if "agent" in class_name_lower:
        log_name = "agent"
    elif "tool" in class_name_lower:
        log_name = "tool"
    elif "agency" in class_name_lower or "swarm" in class_name_lower:
        log_name = "swarm"
    else:
        log_name = "log"

    file_handler = logging.FileHandler(
        (
            f"{class_name}_{name}_{log_name}.log"
            if name
            else f"{class_name}_{log_name}.log"
        ),
    )
    file_handler.setLevel(logging.INFO)

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger
