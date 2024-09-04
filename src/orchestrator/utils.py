def parse(text: str) -> str:
    """
    Parse the LLM output to extract the action and arguments.

    This function takes the LLM output, checks if it ends with "Action: ",
    and then extracts the action and its arguments.

    Args:
        text (str): The LLM output to parse.

    Returns:
        str: The action and its arguments.
    """
    action_prefix = "Action: "
    if not text.strip().split("\n")[-1].startswith(action_prefix):
        return {"action": "retry", "args": f"Could not parse LLM Output: {text}"}
    action_block = text.strip().split("\n")[-1]
    action_str = action_block[len(action_prefix) :]
    split_output = action_str.split(" ", 1)
    if len(split_output) == 1:
        action, action_input = split_output[0], None
    else:
        action, action_input = split_output
    action = action.strip()
    if action_input is not None:
        action_input = [
            inp.strip().strip("[]") for inp in action_input.strip().split(";")
        ]
    return {"action": action, "args": action_input}
