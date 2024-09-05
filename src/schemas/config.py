from pydantic import BaseModel

from src.schemas.modal import AgentState


class MainConfig(BaseModel):
    input_type: str
    prompt_file: str | None = None
    start_url: str
    max_steps: int
    max_iterations: int


class OrchestratorConfig(BaseModel):
    system_prompt: str
    llm: str = "openai/gpt-4o"
    agent_state: AgentState = AgentState()
    tools: dict = {}
