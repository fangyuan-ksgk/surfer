import asyncio
import platform

from ..modal import AgentState


async def click(state: AgentState) -> str:
    """
    Perform a click action on a specified bounding box.

    Args:
        state (AgentState): The current state of the agent, containing page, prediction, and bboxes.

    Returns:
        str: A message indicating the result of the click action.

    This function extracts the click target from the prediction, finds the corresponding
    bounding box, and performs a mouse click at the center of that box.
    """
    page = state.page
    prediction = state.prediction
    click_args = prediction.args
    if click_args is None or len(click_args) != 1:
        return f"Failed to click bounding box labeled as number {click_args}"
    bbox_id = click_args[0]
    try:
        bbox = state.bboxes[int(bbox_id)]
    except Exception:
        return f"Error: no bbox for : {bbox_id}"
    x, y = bbox["x"], bbox["y"]
    await page.mouse.click(x, y)
    return f"Clicked {bbox_id}"


async def type_text(state: AgentState) -> str:
    """
    Type text into a specified element and submit.

    Args:
        state (AgentState): The current state of the agent, containing page, prediction, and bboxes.

    Returns:
        str: A message indicating the result of the typing action.

    This function extracts the target element and text content from the prediction,
    clicks on the specified element, clears any existing text, types the new content,
    and submits it by pressing Enter.
    """
    page = state.page
    prediction = state.prediction
    type_args = prediction.args
    if type_args is None or len(type_args) != 2:
        return (
            f"Failed to type in element from bounding box labeled as number {type_args}"
        )
    bbox_id = type_args[0]
    bbox = state.bboxes[int(bbox_id)]
    x, y = bbox["x"], bbox["y"]
    text_content = type_args[1]
    await page.mouse.click(x, y)
    # Check if MacOS
    select_all = "Meta+A" if platform.system() == "Darwin" else "Control+A"
    await page.keyboard.press(select_all)
    await page.keyboard.press("Backspace")
    await page.keyboard.type(text_content)
    await page.keyboard.press("Enter")
    return f"Typed {text_content} and submitted"


async def scroll(state: AgentState) -> str:
    """
    Scroll the page or a specific element.

    Args:
        state (AgentState): The current state of the agent, containing page, prediction, and bboxes.

    Returns:
        str: A message indicating the result of the scrolling action.

    This function handles scrolling either the entire window or a specific element on the page.
    It interprets the scroll direction and target from the prediction args and performs the appropriate action.
    """
    page = state.page
    prediction = state.prediction
    scroll_args = prediction.args
    if scroll_args is None or len(scroll_args) != 2:
        return "Failed to scroll due to incorrect arguments."
    target, direction = scroll_args
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
