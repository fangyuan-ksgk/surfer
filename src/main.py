import asyncio

from playwright.async_api import Browser, Page, async_playwright

from . import gladia
from .orchestrator import build_web_voyager_graph
from .utils.logging import logger
from .utils.utils import load_config, read_file

config = load_config()
graph = build_web_voyager_graph()


async def call_agent(
    question: str, page: Page, max_steps: int = config["auto_steps"]
) -> str | None:
    event_stream = graph.astream(
        {
            "page": page,
            "input": question,
            "scratchpad": [],
        },
        {
            "recursion_limit": max_steps,
        },
    )
    final_answer = None
    steps: list[str] = []
    async for event in event_stream:
        if "agent" not in event:
            continue
        pred = event.get("agent", {}).get("prediction") or {}
        action = pred.get("action")
        action_input = pred.get("args")
        logger.info(f"{len(steps) + 1}. {action}: {action_input}")
        steps.append(f"{len(steps) + 1}. {action}: {action_input}")
        if "ANSWER" in action:
            final_answer = action_input[0]
            break
    return final_answer


async def main() -> None:
    async with async_playwright() as p:
        input_type = config["input_type"]
        assert input_type in ["text", "audio"]

        browser: Browser = await p.chromium.launch(headless=False)

        page: Page = await browser.new_page()
        url = config["url"]
        await page.goto(url)

        if input_type == "text":
            question = read_file(config["prompt_file"])
            try:
                final_answer = await call_agent(question, page)
                logger.info(f"final_answer: {final_answer}")
            except Exception:
                pass
        else:
            for _ in range(config["max_iterations"]):
                question = await gladia.listen()
                try:
                    final_answer = await call_agent(question, page)
                    logger.info(f"final_answer: {final_answer}")
                except Exception:
                    continue

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
