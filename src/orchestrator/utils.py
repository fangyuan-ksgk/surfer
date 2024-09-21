import inspect
import json
from collections.abc import Callable
from typing import Any

from src.orchestrator.constants import END
from src.schemas.models import AgentState


def format_descriptions(state: dict[str, Any]) -> dict[str, Any]:
    """
    Format the descriptions of bounding boxes in the given state.

    This function takes a state dictionary containing bounding box information
    and formats it into a human-readable string description.

    Args:
        state (dict[str, Any]): A dictionary containing the current state,
                                including a 'bboxes' key with bounding box information.

    Returns:
        dict[str, Any]: The updated state dictionary with an additional
                        'bbox_descriptions' key containing the formatted descriptions.
    """
    labels = []
    for i, bbox in enumerate(state["bboxes"]):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return {**state, "bbox_descriptions": bbox_descriptions}


def parse(text: str) -> dict[str, Any]:
    """
    Parse the LLM output to extract the action and arguments.

    This function takes the LLM output and extracts the action and its parameters.

    Args:
        text (str): The LLM output to parse.

    Returns:
        dict[str, Any]: A dictionary containing the action and its arguments.
    """
    lines = text.strip().split("\n")
    action_line = next((line for line in lines if line.startswith("Action:")), None)
    params_line = next((line for line in lines if line.startswith("Parameters:")), None)

    if not action_line:
        return {"action": "retry", "args": f"Could not parse LLM Output: {text}"}

    action = action_line.split(":", 1)[1].strip()

    args = {}
    if params_line:
        params_str = params_line.split(":", 1)[1].strip()
        try:
            args = json.loads(params_str)
        except json.JSONDecodeError:
            # Fallback to the original parsing method if JSON parsing fails
            params_list = params_str.strip("{}").split(",")
            for param in params_list:
                key, value = param.split(":", 1)
                args[key.strip()] = value.strip().strip('"')

    return {"action": action, "args": args}


def select_tool(state: AgentState) -> str:
    """
    Select the appropriate tool based on the agent's action prediction.

    This function is called every time the agent completes its prediction
    to route the output to a tool or to the end user.

    Args:
        state (AgentState): The current state of the agent, containing
                            the prediction information.

    Returns:
        str: The name of the selected tool, 'END' for final answer,
             or 'agent' for retry.
    """
    action = state["prediction"]["action"]
    if action == "ANSWER":
        return END
    if action == "retry":
        return "agent"
    return action


def convert_tools_to_openai_format(tools: list[Callable]) -> list[dict[str, Any]]:
    """
    Convert function tools to OpenAI expected format.

    Args:
        tools (List[Callable]): A list of tool functions.

    Returns:
        List[Dict[str, Any]]: A list of tool descriptions in OpenAI format.
    """
    openai_tools = []
    for func in tools:
        signature = inspect.signature(func)
        parameters = list(signature.parameters.values())

        # Skip the first parameter (state) as it's not needed in the OpenAI format
        parameters = parameters[1:]

        docstring = inspect.getdoc(func)
        description, params_doc = (
            docstring.split("Args:", 1) if "Args:" in docstring else (docstring, "")
        )

        tool = {
            "type": "function",
            "function": {
                "name": func.__name__,
                "description": description.strip(),
                "parameters": {"type": "object", "properties": {}, "required": []},
            },
        }

        for param in parameters:
            param_doc = next(
                (line.strip() for line in params_doc.split("\n") if param.name in line),
                "",
            )
            param_description = (
                param_doc.split(":", 1)[1].strip() if ":" in param_doc else ""
            )

            tool["function"]["parameters"]["properties"][param.name] = {
                "type": "string",
                "description": param_description,
            }
            if param.default == inspect.Parameter.empty:
                tool["function"]["parameters"]["required"].append(param.name)

        openai_tools.append(tool)

    return openai_tools


def convert_tools_to_paragraphs(tools: list[Callable]) -> str:
    """
    Convert function tools to paragraph format for in-prompt use.

    Args:
        tools (List[Callable]): A list of tool functions.

    Returns:
        str: A string containing paragraph descriptions of the tools.
    """
    paragraphs = []
    for func in tools:
        signature = inspect.signature(func)
        parameters = list(signature.parameters.values())[1:]  # Skip 'state' parameter

        docstring = inspect.getdoc(func)
        description, params_doc = (
            docstring.split("Args:", 1) if "Args:" in docstring else (docstring, "")
        )

        tool_desc = f"Action: {func.__name__}\n"
        tool_desc += f"Description: {' '.join(description.strip().split())}\n"

        if parameters:
            tool_desc += "Parameters: {"
            param_descriptions = []
            for param in parameters:
                param_doc = next(
                    (
                        line.strip()
                        for line in params_doc.split("\n")
                        if param.name in line
                    ),
                    "",
                )
                param_description = (
                    param_doc.split(":", 1)[1].strip() if ":" in param_doc else ""
                )
                param_descriptions.append(f'"{param.name}": "{param_description}"')
            tool_desc += ", ".join(param_descriptions)
            tool_desc += "}\n"

        paragraphs.append(tool_desc.strip())

    return "\n\n".join(paragraphs)
