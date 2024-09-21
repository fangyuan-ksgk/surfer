from src.schemas.models import AgentState


async def answer(state: AgentState, content: str) -> str:
    """
    Return the final answer to the user's query.

    This function is used when the agent has determined it has sufficient information
    to provide a final answer to the user's original question.

    Args:
        state (AgentState): The current state of the agent.
        content (str): The final answer content to be returned to the user.

    Returns:
        str: A message indicating that the final answer has been provided.
    """
    _ = state  # Explicitly acknowledge the unused argument
    return f"ANSWER: {content}"
