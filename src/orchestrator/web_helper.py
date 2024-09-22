import asyncio
import base64

from playwright.async_api import Page

from src.schemas.models import AgentState
from src.utils.logging import logger


async def mark_page(page: Page) -> str:
    """
    Mark the page with bounding boxes and take a screenshot.

    This function reads a JavaScript file to mark elements on the page,
    attempts to execute the marking script, takes a screenshot,
    and then removes the markings.

    Args:
        page (Page): The Playwright Page object representing the current web page.

    Returns:
        dict: A dictionary containing the base64-encoded screenshot and bounding box information.
    """
    # Read the JavaScript file containing the marking script
    with open("./src/orchestrator/mark_page.js") as f:
        mark_page_script = f.read()

    # Attempt to execute the marking script
    await page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await page.evaluate("markPage()")
            break
        except Exception:
            # May be loading, wait for 3 seconds before retrying
            await asyncio.sleep(3)
    screenshot = await page.screenshot()
    await page.evaluate("unmarkPage()")
    return {
        "img": base64.b64encode(screenshot).decode(),
        "bboxes": bboxes,
    }


async def annotate(
    state: AgentState, max_retries: int = 10, retry_delay: float = 0.5
) -> AgentState:
    """
    Annotate the page with bounding boxes and take a screenshot.

    Args:
        state (AgentState): The current state of the agent, containing the page object.
        max_retries (int): The maximum number of retries to attempt.
        retry_delay (float): The delay between retries in seconds.

    Returns:
        AgentState: An updated AgentState object with the screenshot and bounding box information.
    """
    for attempt in range(max_retries):
        try:
            marked_page = await mark_page(state.page)
            return AgentState(**{**state.__dict__, **marked_page})
        except Exception as e:
            if attempt < max_retries - 1:
                logger.info(
                    f"Attempt {attempt + 1} failed. Retrying in {retry_delay} seconds..."
                )
                await asyncio.sleep(retry_delay)
            else:
                logger.info(f"All {max_retries} attempts failed. Last error: {str(e)}")
                raise


def format_descriptions(state: AgentState) -> str:
    """
    Format the descriptions of the bounding boxes.

    This function takes the state containing the bounding box information,
    and formats it into a string description of each bounding box.

    Args:
        state (AgentState): The current state of the agent, containing the bounding box information.

    Returns:
        str: A string description of each bounding box.
    """
    labels = []
    for i, bbox in enumerate(state.bboxes):
        text = bbox.get("ariaLabel") or ""
        if not text.strip():
            text = bbox["text"]
        el_type = bbox.get("type")
        labels.append(f'{i} (<{el_type}/>): "{text}"')
    bbox_descriptions = "\nValid Bounding Boxes:\n" + "\n".join(labels)
    return bbox_descriptions
