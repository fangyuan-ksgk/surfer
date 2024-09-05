from enum import Enum

from pydantic import BaseModel


class LLMType(Enum):
    OPENAI = "openai"
    ANTHROPIC = "anthropic"


class LLMConfig(BaseModel):
    llm_type: LLMType = LLMType.OPENAI
    model_name: str = "gpt-4o"
    max_tokens: int = 4096
    temperature: float = 0.0
    frequency_penalty: float = 0.0
