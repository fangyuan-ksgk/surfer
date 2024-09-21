"""
This module contains web interaction tools for the orchestrator.

These tools are designed to be used as LLM tools and must adhere to the parameter
and docstring format required by OpenAI's function calling API. Each function
should have a clear docstring with a description and properly formatted Args
and Returns sections.

The functions in this module should be compatible with the FunctionDefinition
schema used by OpenAI, which includes:
- name: The name of the function (inferred from the function name)
- description: A description of what the function does (from the docstring)
- parameters: The parameters the function accepts, described as a JSON Schema object
  (inferred from the function signature and docstring)

For more details on the required format, refer to the OpenAI function calling guide:
https://platform.openai.com/docs/guides/function-calling
"""


import asyncio
import platform

from src.schemas.models import AgentState


async def click(state: AgentState, bbox_id: int) -> str:
    """
    Perform a click action on a specified bounding box.

    This function extracts the click target from the prediction, finds the corresponding
    bounding box, and performs a mouse click at the center of that box.

    Args:
        state (AgentState): The current state of the agent, containing page, prediction, and bboxes.
        bbox_id (int): The numerical label of the bounding box to click.

    Returns:
        str: A message indicating the result of the click action.
    """
    page = state.page
    try:
        bbox = state.bboxes[int(bbox_id)]
    except Exception:
        return f"Error: no bbox for : {bbox_id}"
    x, y = bbox["x"], bbox["y"]
    await page.mouse.click(x, y)
    return f"Clicked {bbox_id}"


async def type_text(state: AgentState, bbox_id: int, text_content: str) -> str:
    """
    Type text into a specified element and submit.

    This function extracts the target element and text content from the prediction,
    clicks on the specified element, clears any existing text, types the new content,
    and submits it by pressing Enter.

    Args:
        state (AgentState): The current state of the agent, containing page, prediction, and bboxes.
        bbox_id (int): The numerical label of the bounding box to type into.
        text_content (str): The text content to type into the bounding box.

    Returns:
        str: A message indicating the result of the typing action.
    """
    page = state.page
    bbox = state.bboxes[int(bbox_id)]
    x, y = bbox["x"], bbox["y"]
    await page.mouse.click(x, y)
    # Check if MacOS
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await page.keyboard.press("Backspace")
    await page.keyboard.type(text_content)
    await page.keyboard.press("Enter")
    return f"Typed {text_content} and submitted"


async def scroll(state: AgentState, target: int, direction: str) -> str:
    """
    Scroll the page or a specific element.

    This function handles scrolling either the entire window or a specific element on the page.
    It interprets the scroll direction and target from the prediction args and performs the appropriate action.

    Args:
        state (AgentState): The current state of the agent, containing page, prediction, and bboxes.
        target (str): The target to scroll, either a bbox_id or "WINDOW".
        direction (str): The direction to scroll, either "up" or "down".

    Returns:
        str: A message indicating the result of the scrolling action.
    """
    page = state.page
    if target.upper() == "WINDOW":
        # Not sure the best value for this:
        scroll_amount = 500
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.evaluate(f"window.scrollBy(0, {scroll_direction})")
    else:
        # Scrolling within a specific element
        scroll_amount = 200
        target_id = int(target)
        bbox = state.bboxes[target_id]
        x, y = bbox["x"], bbox["y"]
        scroll_direction = (
            -scroll_amount if direction.lower() == "up" else scroll_amount
        )
        await page.mouse.move(x, y)
        await page.mouse.wheel(0, scroll_direction)

    return f"Scrolled {direction} in {'window' if target.upper() == 'WINDOW' else 'element'}"


async def wait(state: AgentState) -> str:
    """
    Pause execution for a fixed amount of time.

    Args:
        state (AgentState): The current state of the agent (unused in this function).

    Returns:
        str: A message indicating the duration of the wait.
    """
    _ = state
    sleep_time = 5
    await asyncio.sleep(sleep_time)
    return f"Waited for {sleep_time}s."


async def go_back(state: AgentState) -> str:
    """
    Navigate back to the previous page in the browser history.

    Args:
        state (AgentState): The current state of the agent, containing the page object.

    Returns:
        str: A message indicating the navigation action and the new URL.
    """
    page = state.page
    await page.go_back()
    return f"Navigated back a page to {page.url}."


async def to_google(state: AgentState) -> str:
    """
    Navigate to the Google homepage.

    Args:
        state (AgentState): The current state of the agent, containing the page object.

    Returns:
        str: A message confirming the navigation to Google.
    """
    page = state.page
    await page.goto("https://www.google.com/")
    return "Navigated to google.com."
