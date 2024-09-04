from .modal import AgentState, Prediction
import platform
import asyncio
from playwright.async_api import Page
import base64



async def click(state: AgentState) -> str:
    """_summary_

    Args:
        state (AgentState): _description_

    Returns:
        str: _description_
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
    _ = state
    sleep_time = 5
    await asyncio.sleep(sleep_time)
    return f"Waited for {sleep_time}s."


async def go_back(state: AgentState) -> str:
    page = state.page
    await page.go_back()
    return f"Navigated back a page to {page.url}."


async def to_google(state: AgentState) -> str:
    page = state.page
    await page.goto("https://www.google.com/")
    return "Navigated to google.com."


async def mark_page(page: Page) -> str:
    with open("./src/mark_page.js") as f:
        mark_page_script = f.read()
    
    await page.evaluate(mark_page_script)
    for _ in range(10):
        try:
            bboxes = await page.evaluate("markPage()")
            break
        except Exception:
            # May be loading...
            await asyncio.sleep(3)
    screenshot = await page.screenshot()
    # Ensure the bboxes don't follow us around
    await page.evaluate("unmarkPage()")
    return {
        "img": base64.b64encode(screenshot).decode(),
        "bboxes": bboxes,
    }


