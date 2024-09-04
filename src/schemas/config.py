from pydantic import BaseModel


class MainConfig(BaseModel):
    input_type: str
    prompt_file: str
    start_url: str
    max_steps: int
    max_iterations: int
