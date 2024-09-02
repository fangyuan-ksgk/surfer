import os
from typing import Any

import dotenv
import yaml

dotenv.load_dotenv()


def load_config(file_path: str = "src/config.yaml") -> dict[str, Any]:
    # Check that the following environment variables are set
    for env_var in [
        "LANGCHAIN_API_KEY",
        "OPENAI_API_KEY",
        "GLADIA_API_KEY",
        "LINKEDIN_USERNAME",
        "LINKEDIN_PASSWORD",
    ]:
        if not os.getenv(env_var):
            raise ValueError(
                f"Environment variable {env_var} is not set, please set it in the .env file."
            )

    with open(file_path) as file:
        config: dict[str, Any] = yaml.safe_load(file)
        config["linkedin_username"] = os.getenv("LINKEDIN_USERNAME")
        config["linkedin_password"] = os.getenv("LINKEDIN_PASSWORD")
        return config


def read_file(file_path: str) -> str:
    with open(file_path) as file:
        return file.read()
