import asyncio
import logging

from playwright.async_api import async_playwright

from src.depreciated.langchain_orchestrator import build_web_voyager_graph

logger = logging.getLogger("Surfer Agent")
logger.setLevel(logging.INFO)
hander = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
hander.setFormatter(formatter)
logger.addHandler(hander)

graph = build_web_voyager_graph()


async def main():
    while True:
        browser = await async_playwright().start()
        # We will set headless=False so we can watch the agent navigate the web.
        browser = await browser.chromium.launch(headless=False, args=None)
        global page
        page = await browser.new_page()
        _ = await page.goto(
            "https://www.google.com"
        )  # This is where we decide the starting point of the agent

        # 1. Use 'Stop' as the detectable stopping word for the agent, so that it halts the execution.
        # 2. New instruction could leads to a new web-page | need to get deeper into the state & scrathpad

        global question
        global url
        question = "NA"
        url = "https://www.google.com"

        # Plan B: Record Question, Record Url from last visited page | Spin up another agent to continue the browsing
        async def call_agent(question, page, max_steps: int = 150):
            global url
            await page.goto(url)

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
                if question == "NA":
                    continue
                event["agent"]["input"] = question
                pred = event.get("agent", {}).get("prediction") or {}
                action = pred.get("action")
                action_input = pred.get("args")
                print(f"{len(steps) + 1}. {action}: {action_input}")
                steps.append(f"{len(steps) + 1}. {action}: {action_input}")
                if "ANSWER" in action:
                    final_answer = action_input[0]
                    url = page.url  # Update last url from browsing experience
                    break
            return final_answer

        async def get_real_time_input():
            global question
            while True:
                question = await asyncio.get_event_loop().run_in_executor(
                    None, input, "Please enter your question: "
                )
                logger.info(f"Parsing Question: {question}")

        question = ""
        is_break = False
        while is_break:
            new_input = input("Enter instruction: ")
            if new_input != "":  # Update only when input is not Empty
                question = new_input

            logger.info(f"Getting Instruction: {question}")
            if "stop" in question:
                logger.info("Breaking out upon hearing 'Stop'.")
                is_break = True
                print("Breaking Out")
                break
            if "hold" in question:
                logger.info("Holding the Agent upon hearing 'Hold'.")
                print("Holding the Agent")
                import time

                time.sleep(120)
                continue
            answer = await call_agent(question, page)

        # The get input part should keep running in the background
        input_task = asyncio.create_task(get_real_time_input())

        # When 'stop' is put into question, agent stop
        agent_task = asyncio.create_task(call_agent(question, page))

        await asyncio.gather(input_task, agent_task)
        answer = agent_task.result()
        print(f"Final answer: {answer}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
