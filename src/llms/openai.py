import os

from openai import OpenAI

from src.schemas.llm import LLMConfig


class OpenAILLM:
    def __init__(self, config: LLMConfig):
        self._openai_api_key = os.getenv("OPENAI_API_KEY")
        self._openai_api_base = os.getenv("OPENAI_API_BASE")

        self.client = OpenAI(
            api_key=self._openai_api_key,
            base_url=self._openai_api_base,
        )
        self.config = config

    def generate(
        self,
        messages: list[dict],
        stream: bool = False,
        tools: list[dict] | None = None,
    ):
        return self.client.chat.completions.create(
            model=self.config.model_name,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            frequency_penalty=self.config.frequency_penalty,
            stream=stream,
            tools=tools,
        )
