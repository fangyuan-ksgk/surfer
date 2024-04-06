import argparse
import asyncio

from IPython import display
from playwright.async_api import async_playwright

from src import graph, perception, utils

# Create the parser
parser = argparse.ArgumentParser(description="Process mode value.")

# Add an argument
parser.add_argument("-m", type=int, choices=[0, 1], required=True, help="Mode value (0 or 1)")

# Parse the argument
args = parser.parse_args()


async def main():
    browser = await async_playwright().start()
    # We will set headless=False so we can watch the agent navigate the web.
    browser = await browser.chromium.launch(headless=False, args=None)
    page = await browser.new_page()
    _ = await page.goto("https://www.google.com")

    async def call_agent(question: str, page, max_steps: int = 150):
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
            print(f"{len(steps) + 1}. {action}: {action_input}")
            steps.append(f"{len(steps) + 1}. {action}: {action_input}")
            if "ANSWER" in action:
                final_answer = action_input[0]
                break
        return final_answer

    # question = input("Please enter your question: ") # Command Line Input
    question = perception.listen()
    answer = await call_agent(question, page)
    print(f"Final answer: {answer}")

    await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
