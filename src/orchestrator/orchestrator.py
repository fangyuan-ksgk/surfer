from typing import Any

from src.llms.anthropic import AnthropicLLM
from src.llms.openai import OpenAILLM
from src.orchestrator.constants import ANSWER
from src.orchestrator.prompt import WEB_BROWSING
from src.orchestrator.utils import convert_tools_to_paragraphs, parse
from src.orchestrator.web_helper import annotate, format_descriptions
from src.schemas.config import OrchestratorConfig
from src.schemas.llm import LLMConfig, LLMType
from src.schemas.models import AgentState
from src.utils.logging import logger


class Orchestrator:
    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.agent_state = config.agent_state
        self.llm = self._get_llm(config.llm)
        self.actions = convert_tools_to_paragraphs(config.tools)

    def _get_llm(self, llm_model_name: str):
        try:
            llm_type, model_name = llm_model_name.split("/")
        except ValueError:
            raise ValueError(
                f"Invalid LLM model name format: {llm_model_name}. Expected format: 'type/model'"
            )

        if llm_type == LLMType.OPENAI.value:
            return OpenAILLM(LLMConfig(llm_type=LLMType.OPENAI, model_name=model_name))
        elif llm_type == LLMType.ANTHROPIC.value:
            return AnthropicLLM(
                LLMConfig(llm_type=LLMType.ANTHROPIC, model_name=model_name)
            )
        else:
            raise ValueError(f"Invalid LLM type: {llm_type}")

    def _format_conversation(self, prompt: str, input: str) -> list[dict]:
        conversation = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": input},
        ]
        return conversation

    async def _run_agent(self) -> dict[str, Any]:
        self.agent_state = await annotate(self.agent_state)
        formatted_descriptions = format_descriptions(self.agent_state)
        prompt = WEB_BROWSING.format(
            actions=self.actions, bounding_boxes=formatted_descriptions
        )

        conversation = self._format_conversation(prompt, self.agent_state.input)
        response = self.llm.generate(conversation)
        text_response = response.choices[0].message.content
        parsed_response = parse(text_response)

        logger.info(f"Parsed response: {parsed_response}")

        self.agent_state.prediction = parsed_response

    def _update_scratchpad(self, state: AgentState) -> AgentState:
        # Implement scratchpad update logic here
        pass

    async def _select_and_run_tool(self) -> str:
        action = self.agent_state.prediction["action"]
        args = self.agent_state.prediction["args"]

        tool = next((t for t in self.config.tools if t.__name__ == action), None)
        if tool is None:
            raise ValueError(f"Unknown action: {action}")

        result = await tool(self.agent_state, **args)
        return result

    async def run(self):
        await self._run_agent()
        if self.agent_state.prediction["action"] == ANSWER:
            logger.info(f"Answer: {self.agent_state.prediction['args']}")
            return

        await self._select_and_run_tool()
