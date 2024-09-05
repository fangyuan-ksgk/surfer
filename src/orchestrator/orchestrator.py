from src.llms.anthropic import AnthropicLLM
from src.llms.openai import OpenAILLM
from src.schemas.config import OrchestratorConfig
from src.schemas.llm import LLMConfig, LLMType


class Orchestrator:
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.agent_state = config.agent_state
        self.llm = self._get_llm(config.llm)

    def _get_llm(self, llm_model_name: str):
        try:
            llm_type, model_name = llm_model_name.split('/')
        except ValueError:
            raise ValueError(f"Invalid LLM model name format: {llm_model_name}. Expected format: 'type/model'")

        if llm_type == LLMType.OPENAI.value:
            return OpenAILLM(LLMConfig(llm_type=LLMType.OPENAI, model_name=model_name))
        elif llm_type == LLMType.ANTHROPIC.value:
            return AnthropicLLM(LLMConfig(llm_type=LLMType.ANTHROPIC, model_name=model_name))
        else:
            raise ValueError(f"Invalid LLM type: {llm_type}")

    def _build(self):
        pass

    def run(self, user_message: str):
        pass

