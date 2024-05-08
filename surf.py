import argparse
import asyncio

from IPython import display
from playwright.async_api import async_playwright

from src import gladia, graph, perception, utils

auto_config = {
    "auto_steps": 4,
    "max_iterations": 99
}

async def main():
    while True:
        browser = await async_playwright().start()
        # We will set headless=False so we can watch the agent navigate the web.
        browser = await browser.chromium.launch(headless=False, args=None)

        page = await browser.new_page()
        global url 
        url = "https://www.google.com"
        _ = await page.goto(url) # Starting Point

        # 1. Use 'Stop' as the detectable stopping word for the agent, so that it halts the execution.
        # 2. New instruction could leads to a new web-page | need to get deeper into the state & scrathpad

        # Main Entry Point function: Question parsed Once and no more intpu" It does seems that internal state should be manipulatable
        async def call_agent(question: str, page, max_steps: int = auto_config["auto_steps"]):
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
                event["agent"]["input"] = "Search for meaning of life" # Check if the injection works | It does NOT really work here
                url = page.url
                
        # Limit the number of rounds Surfer Agent could surf 
        for i in range(auto_config["max_iterations"]):
            # question = input("Please enter your instruction: ")  # Command Line Input
            tmp_question = await gladia.listen()
            
            if 'proceed' not in tmp_question: # Dummy Input, not very instructive, keep original instruction
                question = tmp_question

            if 'exit' in question or 'Exit' in question: # Exit the Agent
                print("See you next time ;>")
                return

            try:
                url = await call_agent(question, page)
            except:
                continue

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
