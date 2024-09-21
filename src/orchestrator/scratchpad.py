import re

from src.schemas.models import AgentState
from src.schemas.prompt import Message


def update_scratchpad(state: AgentState) -> AgentState:
    """
    Update the scratchpad in the agent's state with the latest action and observation.

    This function appends the most recent action and observation to the scratchpad,
    maintaining a history of the agent's interactions.

    Args:
        state (AgentState): The current state of the agent, containing the scratchpad,
                            last action, and last observation.

    Returns:
        AgentState: The updated state with the new scratchpad.
    """
    old = state.scratchpad
    if old:
        txt = old[0].content
        last_line = txt.rsplit("\n", 1)[-1]
        step = int(re.match(r"\d+", last_line).group()) + 1
    else:
        txt = "Previous action observations:\n"
        step = 1
    txt += f"\n{step}. {state.observation}"
    return AgentState(**{**state.model_dump(), "scratchpad": [Message(content=txt)]})
