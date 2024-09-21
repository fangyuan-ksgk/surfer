import asyncio
import json
import os
import subprocess
import threading
from functools import wraps

import anyio
import dotenv
from openai import OpenAI

from src.depreciated import gladia
from src.utils.logging import logger

dotenv.load_dotenv()


MODEL_NAME = "gpt-4-turbo-2024-04-09"

SYSTEM_PROMPT = """
    You are a helpful assistant.
    You can run a command to start a browser search if necessary.
    When a tool is used, it is triggered in the background, and the user is able to continue the conversation.
    Try to use browser search sparingly and only when the latest information is required.
    If not, converse with me normally.
    Don't re-use the browse_web tool for the same question, just answer the question based on your new knowledge.
    only use the browse_web tool one at a time mainly for the user's latest question only.
"""

TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "browse_web",
            "description": "Search the web for the latest information",
            "parameters": {
                "type": "object",
                "properties": {
                    "question": {
                        "type": "string",
                        "description": "The question to search for",
                    },
                    "wait_message": {
                        "type": "string",
                        "description": "The message to display while waiting for the response from the web search, always append say will get back to you or equivalent messaging.",
                    },
                },
                "required": ["question", "wait_message"],
            },
        },
    }
]

MESSAGES = [{"role": "system", "content": SYSTEM_PROMPT}]


def run_async(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        async def coro_wrapper():
            return await func(*args, **kwargs)

        return anyio.run(coro_wrapper)

    return wrapper


def run_async_script(python_file_name: str, question: str):
    # This function will be run in a separate thread to handle the subprocess
    process = subprocess.Popen(
        ["python", f"{python_file_name}.py", question],
        stdout=subprocess.PIPE,
        text=True,
    )
    (
        output,
        _,
    ) = process.communicate()  # Wait for the process to complete and get the stdout
    logger.info(f"Agent: {output}")
    MESSAGES.append({"role": "assistant", "content": output})


def call_async_script_in_thread(python_file_name: str, question: str):
    # Start the run_async_script function in a new thread
    thread = threading.Thread(
        target=run_async_script,
        args=(
            python_file_name,
            question,
        ),
    )
    thread.start()


async def async_user_interaction(conversation_type: str = "text"):
    """Main function to run the assistant.

    Args:
        mode (int, optional): Mode value (0 or 1). Defaults to 0.
        conversation_type (str, optional): Input type (text or voice). Defaults to "text".
        continuous (bool, optional): Enable continuous mode. Defaults to False.
    """
    client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

    # Generate the first welcome message
    response = client.chat.completions.create(
        model=MODEL_NAME,
        messages=MESSAGES,
    )
    response_message = response.choices[0].message
    logger.info(f"Agent: {response_message.content}")
    MESSAGES.append({"role": "assistant", "content": response_message.content})

    while True:
        if conversation_type == "text":
            # logger.info("User: ")
            question = input("User: ")
        elif conversation_type == "voice":
            question = await gladia.listen()

        MESSAGES.append({"role": "user", "content": question})

        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=MESSAGES,
            tools=TOOLS,
            tool_choice="auto",
        )

        response_message = response.choices[0].message
        tool_calls = response_message.tool_calls

        if tool_calls:
            tool_call = tool_calls[-1]
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "browse_web":
                call_async_script_in_thread(function_name, function_args["question"])
                logger.info(f"Agent: {function_args['wait_message']}")
                MESSAGES.append(
                    {"role": "assistant", "content": function_args["wait_message"]}
                )
            else:
                raise Exception(f"Unknown tool {function_name}")
        else:
            logger.info(f"Agent: {response_message.content}")
            MESSAGES.append({"role": "assistant", "content": response_message.content})


async def main():
    await asyncio.gather(
        async_user_interaction(),
    )


if __name__ == "__main__":
    asyncio.run(main())
