from src import gladia, graph, perception, utils
import asyncio
import playwright
from src import gladia, graph, perception, utils
from playwright.async_api import async_playwright
from src.utils import graph
import logging
logger = logging.getLogger("Surfer Agent")
logger.setLevel(logging.INFO)
hander = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
hander.setFormatter(formatter)
logger.addHandler(hander)


# Declare the global variables
break_out = False
if_end = False
question = ""
search_iter = 0

# One Concurrent Async Process | Gradia Streaming Audio Input
async def listen_for_stop():
    global break_out, if_end, question
    while True:
        question = await gladia.listen()
        logger.info(f"Parsing Question: {question}")
        if "Stop" in question:
            logger.info("Breaking out upon hearing 'Stop'.")
            break_out = True
            print("Breaking Out!!!!!!")
        if "End" in question:
            logger.info("End the Agent upon hearing 'End'.")
            if_end = True
            break

async def input_for_stop():
    global break_out, if_end, question
    while True:
        question = input("Enter instruction: ")
        logger.info(f"Getting Question: {question}")
        if "stop" in question:
            logger.info("Breaking out upon hearing 'Stop'.")
            break_out = True
            print("Breaking Out!!!!!!")
        if "end" in question:
            logger.info("End the Agent upon hearing 'End'.")
            if_end = True
            break


async def web_voyager():
    global break_out, if_end, question, search_iter

    while not if_end:
        search_iter += 1
        print(f"------ \nSearch Iteration: {search_iter} \n------")
        browser = await async_playwright().start()
        browser = await browser.chromium.launch(headless=False, args=None)

        # Change the Starting Point for the Web-Browsing Agent
        page = await browser.new_page()
        _ = await page.goto("https://www.google.com") # This is where we decide the starting point of the agent
        logger.info(f"Navigating to Google on a new page with question: {question}")

        event_stream = graph.astream(
            {
                "page": page,
                "input": question,
                "scratchpad": [],
            },
            {
                "recursion_limit": 50,
            },
        )

        final_answer = None
        steps = []
        async for event in event_stream:
            # We'll display an event stream here
            if "agent" not in event:
                continue
            if break_out:
                break_out = False
                break
            event['agent']['input'] = question # Dummny Slot-in Place for further requests from user
            logger.info(f"Updated Agent Input: {event['agent']['input']}")

            pred = event.get("agent", {}).get("prediction") or {}
            # print("Event: ", event)
            # print("Prediction: \n", pred)
            action = pred.get("action")
            action_input = pred.get("args")
            logger.info(f"Action: \n{len(steps) + 1}. {action}: {action_input}")
            print(f"Action: \n{len(steps) + 1}. {action}: {action_input}")
            steps.append(f"{len(steps) + 1}. {action}: {action_input}")
            if "ANSWER" in action:
                final_answer = action_input[0]
                logger.info(f"Final Answer: {final_answer}")
                print("Final Answer: ", final_answer)
                break


async def main():
    # Create and run the tasks concurrently
    # task1 = asyncio.create_task(listen_for_stop())
    task1 = asyncio.create_task(input_for_stop())
    task2 = asyncio.create_task(web_voyager())
    await asyncio.gather(task1, task2)

# Run the async main function
asyncio.run(main())
# asyncio.ensure_future(main())