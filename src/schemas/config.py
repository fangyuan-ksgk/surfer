from collections.abc import Callable

from pydantic import BaseModel, ConfigDict

from src.schemas.models import AgentState


class MainConfig(BaseModel):
    input_type: str
    prompt_file: str | None = None
    start_url: str = "https://www.google.com"
    max_steps: int = 20
    max_iterations: int = 1


class OrchestratorConfig(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    system_prompt: str
    llm: str = "openai/gpt-4o"
    agent_state: AgentState = AgentState()
    tools: list[Callable] = []
    max_steps: int = 20
