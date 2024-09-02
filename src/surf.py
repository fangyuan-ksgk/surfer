import asyncio

from orchestrator import build_web_voyager_graph  # type: ignore
from playwright.async_api import Browser, Page, async_playwright

from src.utils.utils import load_config, read_file

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
    steps: list[str] = []
    async for event in event_stream:
        if "agent" not in event:
            continue
        pred = event.get("agent", {}).get("prediction") or {}
        action = pred.get("action")
        action_input = pred.get("args")
        print(f"{len(steps) + 1}. {action}: {action_input}")
        steps.append(f"{len(steps) + 1}. {action}: {action_input}")
        event["agent"]["input"] = "Search for meaning of life"
    return page.url


async def main() -> None:
    async with async_playwright() as p:
        browser: Browser = await p.chromium.launch(headless=False)

        page: Page = await browser.new_page()
        url = config["url"]
        await page.goto(url)

        for _ in range(config["max_iterations"]):
            question = read_file(config["prompt_file"])

            if "exit" in question.lower():
                print("See you next time ;>")
                return

            try:
                url = await call_agent(question, page)
            except Exception:
                continue

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
