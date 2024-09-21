import os

from anthropic import Anthropic

from src.schemas.llm import LLMConfig


class AnthropicLLM:
    def __init__(self, config: LLMConfig):
        self._anthropic_api_key = os.getenv("ANTHROPIC_API_KEY")

        self.client = Anthropic(
            api_key=self._anthropic_api_key,
        )
        self.config = config

    def generate(
        self,
        messages: list[dict],
        stream: bool = False,
        tools: list[dict] | None = None,
    ):
        return self.client.messages.create(
            model=self.config.model_name,
            messages=messages,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature,
            stream=stream,
            tools=tools,
        )
