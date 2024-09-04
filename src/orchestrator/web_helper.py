import asyncio
import base64

from playwright.async_api import Page

from src.schemas.modal import AgentState


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
    with open("./src/mark_page.js") as f:
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


async def annotate(state: AgentState) -> str:
    """
    Annotate the page with bounding boxes and take a screenshot.

    This function reads a JavaScript file to mark elements on the page,
    attempts to execute the marking script, takes a screenshot,
    and then removes the markings.

    Args:
        state (AgentState): The current state of the agent, containing the page object.

    Returns:
        dict: A dictionary containing the base64-encoded screenshot and bounding box information.
    """
    marked_page = await mark_page.with_retry().ainvoke(state.page)
    return {**state, **marked_page}


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
