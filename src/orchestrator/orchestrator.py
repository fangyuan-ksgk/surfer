import re
from typing import Any

from src.llms.anthropic import AnthropicLLM
from src.llms.openai import OpenAILLM
from src.orchestrator.constants import ANSWER, END
from src.orchestrator.prompt import WEB_BROWSING
from src.orchestrator.utils import convert_tools_to_paragraphs, parse
from src.orchestrator.web_helper import annotate, format_descriptions
from src.schemas.config import OrchestratorConfig
from src.schemas.llm import LLMConfig, LLMType
from src.utils.logging import logger


class Orchestrator:
    """
    The Orchestrator class manages the execution of an AI agent for web browsing tasks.

    This class is responsible for initializing the agent, running it through multiple steps,
    and coordinating between the language model, web tools, and the agent's state.

    Attributes:
        config (OrchestratorConfig): Configuration for the orchestrator.
        agent_state (AgentState): The current state of the agent.
        llm (Union[OpenAILLM, AnthropicLLM]): The language model used by the agent.
        actions (str): A string representation of available tools/actions.
    """

    def __init__(self, config: OrchestratorConfig):
        self.config = config
        self.agent_state = config.agent_state
        self.llm = self._get_llm(config.llm)
        self.actions = convert_tools_to_paragraphs(config.tools)

    def _get_llm(self, llm_model_name: str):
        """
        Initialize and return the appropriate language model based on the configuration.

        Args:
            llm_model_name (str): The name of the language model in the format 'type/model'.

        Returns:
            Union[OpenAILLM, AnthropicLLM]: An instance of the specified language model.

        Raises:
            ValueError: If the LLM type is invalid or the model name format is incorrect.
        """
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
        """
        Format the conversation for the language model.

        Args:
            prompt (str): The system prompt for the conversation.
            input (str): The user input for the conversation.

        Returns:
            list[dict]: A list of dictionaries representing the conversation.
        """
        conversation = [
            {"role": "system", "content": prompt},
            {"role": "user", "content": input},
        ]
        return conversation

    async def _run_agent(self) -> dict[str, Any]:
        """
        Execute one step of the agent's decision-making process.

        This method annotates the current web page, formats the prompt,
        generates a response from the language model, and updates the agent's state.

        Returns:
            dict[str, Any]: The parsed response from the language model.
        """
        self.agent_state = await annotate(self.agent_state)
        formatted_descriptions = format_descriptions(self.agent_state)
        prompt = WEB_BROWSING.format(
            actions=self.actions,
            scratchpad=self.agent_state.scratchpad,
            bounding_boxes=formatted_descriptions,
        )

        conversation = self._format_conversation(prompt, self.agent_state.input)
        response = self.llm.generate(conversation)
        text_response = response.choices[0].message.content
        parsed_response = parse(text_response)
        logger.info(f"Parsed response: {parsed_response}")

        self.agent_state.observation = text_response
        self.agent_state.prediction = parsed_response

    def _update_scratchpad(self):
        """
        Update the agent's scratchpad (memory) with the latest observation.

        This method appends the latest observation to the scratchpad,
        maintaining a record of the agent's actions and observations.
        """
        current_scratchpad = self.agent_state.scratchpad
        if current_scratchpad:
            last_line = current_scratchpad.rsplit("\n", 1)[-1]
            step = int(re.match(r"\d+", last_line).group()) + 1
        else:
            current_scratchpad = "Previous action observations:\n"
            step = 1
        observation = self.agent_state.observation.replace("\n", ". ").strip()
        current_scratchpad += f"\n{step}. {observation}"
        logger.info(f"Current scratchpad: {current_scratchpad}")

        self.agent_state.scratchpad = current_scratchpad

    async def _select_and_run_tool(self) -> str:
        """
        Select and execute the tool chosen by the agent.

        This method identifies the tool based on the agent's prediction,
        executes it with the provided arguments, and returns the result.

        Returns:
            str: The result of executing the selected tool.

        Raises:
            ValueError: If the selected action is unknown.
        """
        logger.info(
            f"Running tool: {self.agent_state.prediction['action']}, "
            f"with parameters: {self.agent_state.prediction['args']}"
        )
        action = self.agent_state.prediction["action"]
        args = self.agent_state.prediction["args"]

        tool = next((t for t in self.config.tools if t.__name__ == action), None)
        if tool is None:
            raise ValueError(f"Unknown action: {action}")

        result = await tool(self.agent_state, **args)
        return result

    async def run(self):
        """
        Main method to run the agent until completion or max steps reached.

        This method executes the agent's decision-making loop, running tools
        and updating the agent's state until an answer is provided or the
        maximum number of steps is reached.

        Returns:
            str: The final answer or end message from the agent.
        """
        logger.info(f"Starting agent with input: {self.agent_state.input}")

        for _ in range(self.config.max_steps):
            # Run the agent to get the next action
            await self._run_agent()

            # Update the scratchpad with the latest observation
            self._update_scratchpad()

            # Check if the agent's prediction is to provide an answer or end the conversation
            # If so, return the content of the answer
            if self.agent_state.prediction["action"].upper() == ANSWER:
                return self.agent_state.prediction["args"]["content"]
            elif self.agent_state.prediction["action"].upper() == END:
                return self.agent_state.prediction["args"]["content"]

            # Run the selected tool if action is not ANSWER or END
            await self._select_and_run_tool()

        logger.info("Max steps reached, ending agent")
