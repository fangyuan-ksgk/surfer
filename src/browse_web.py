import argparse
import asyncio

from playwright.async_api import async_playwright

from .orchestrator import build_web_voyager_graph

graph = build_web_voyager_graph()


async def browse_web(question: str, max_steps: int = 150):
    browser = await async_playwright().start()
    # We will set headless=False so we can watch the agent navigate the web.
    browser = await browser.chromium.launch(headless=False, args=None)
    page = await browser.new_page()
    _ = await page.goto("https://www.google.com")

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
    steps = []
    async for event in event_stream:
        # We'll display an event stream here
        if "agent" not in event:
            continue
        pred = event.get("agent", {}).get("prediction") or {}
        action = pred.get("action")
        action_input = pred.get("args")
        # print(f"{len(steps) + 1}. {action}: {action_input}")
        steps.append(f"{len(steps) + 1}. {action}: {action_input}")
        if "ANSWER" in action:
            final_answer = action_input[0]
            break
    await browser.close()
    return final_answer


async def main(question: str):
    result = await browse_web(question)
    print(result)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("question", type=str, help="The question to search for")

    args = parser.parse_args()

    asyncio.run(main(args.question))
