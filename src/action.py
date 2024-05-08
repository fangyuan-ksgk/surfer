import json
import os
import re
import subprocess

import requests
from anthropic import Anthropic
from groq import Groq

GROQ_API_KEY = os.environ.get("GROQ_API_KEY")
E2B_API_KEY = os.environ.get("E2B_API_KEY")
ANTHROPIC_API_KEY = os.environ.get("ANTHROPIC_API_KEY")
groq_client = Groq(api_key=GROQ_API_KEY) if GROQ_API_KEY else None


# Authentic Function Calling with Terminal & File Access
tools = [
    {
        "type": "function",
        "function": {
            "name": "run_command_tool",
            "description": "Executes a terminal command and returns the standard output.",
            "parameters": {
                "type": "object",
                "properties": {
                    "command": {
                        "type": "string",
                        "description": "The command to execute in the terminal.",
                    }
                },
                "required": ["command"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "write_file_tool",
            "description": "Writes content to a specified file.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to write to.",
                    },
                    "content": {
                        "type": "string",
                        "description": "The content to write into the file.",
                    },
                },
                "required": ["filename", "content"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "read_file_tool",
            "description": "Reads content from a specified file and returns it.",
            "parameters": {
                "type": "object",
                "properties": {
                    "filename": {
                        "type": "string",
                        "description": "The name of the file to read from.",
                    }
                },
                "required": ["filename"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "search_web_tool",
            "description": "Searches the web for a given query and returns the top results.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The query to search for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
]


claude_tools = [
    {
        "name": "run_command_tool",
        "description": "Executes a terminal command and returns the standard output.",
        "input_schema": {
            "type": "object",
            "properties": {"command": {"type": "string", "description": "The command to execute in the terminal."}},
            "required": ["command"],
        },
    },
    {
        "name": "write_file_tool",
        "description": "Writes content to a specified file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {"type": "string", "description": "The name of the file to write to."},
                "content": {"type": "string", "description": "The content to write into the file."},
            },
            "required": ["filename", "content"],
        },
    },
    {
        "name": "read_file_tool",
        "description": "Reads content from a specified file and returns it.",
        "input_schema": {
            "type": "object",
            "properties": {"filename": {"type": "string", "description": "The name of the file to read from."}},
            "required": ["filename"],
        },
    },
    {
        "name": "search_web_tool",
        "description": "Searches the web for a given query and returns the top results.",
        "input_schema": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The query to search for."}},
            "required": ["query"],
        },
    },
]


# Terminal Access | Run Command and observe output
def run_command_tool(command):
    result = subprocess.run([command], shell=True, capture_output=True, text=True)
    if result.stderr:
        return result.stderr
    return result.stdout


# Write File | Write File content into system
def write_file_tool(filename, content):
    with open(filename, "w") as file:
        file.write(content)


# Read File | Read file and get content
def read_file_tool(filename):
    with open(filename) as file:
        return file.read()


# Web Search Tool
def search_web_tool(query):

    url = "https://google.serper.dev/search"

    payload = json.dumps({"q": query})
    headers = {"X-API-KEY": os.environ["SERP_API_KEY"], "Content-Type": "application/json"}

    response = requests.request("POST", url, headers=headers, data=payload)
    return json.loads(response.text)["organic"]


SYSTEM_PROMPT = """You are a helpful assistant, helping to navigate the world of operating system. You can run commands in terminal, create and read files, which includes write python file and execute it. Browing through codebase and record your findings is also possible."""

# def chat_with_llama_no_tool(user_message):
#   """
#   llama3-70b groq enabled version ; without tools
#   """
#   print(f"\n{'='*50}\nUser message: {user_message}\n{'='*50}")

#   messages = [
#       {"role": "system", "content": SYSTEM_PROMPT},
#       {"role": "user", "content": user_message}
#   ]

#   MODEL_NAME = "llama3-70b-8192"

#   response = groq_client.chat.completions.create(
#       model=MODEL_NAME,
#       messages=messages,
#       tools = [],
#       max_tokens=4096,
#   )

#   response_message = response.choices[0].message
#   return response_message.content


def chat_with_llama(user_message):
    """
    llama3-70b groq enabled version ; with tools
    """
    print(f"\n{'='*50}\nUser message: {user_message}\n{'='*50}")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": user_message}]

    MODEL_NAME = "llama3-70b-8192"

    use_tools = tools if use_tool else []

    response = groq_client.chat.completions.create(
        model=MODEL_NAME,
        messages=messages,
        tools=use_tools,
        tool_choice="auto",
        max_tokens=4096,
    )

    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls

    if tool_calls:
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            function_args = json.loads(tool_call.function.arguments)

            if function_name == "run_command_tool":
                print("Command Tool")
                command = function_args["command"]
                command_output = run_command_tool(command)
                return command_output

            if function_name == "write_file_tool":
                print("File Writer Tool")
                filename = function_args["filename"]
                content = function_args["content"]
                write_file_tool(filename, content)

            if function_name == "read_file_tool":
                print("File Reader Tool")
                filename = function_args["filename"]
                file_content = read_file_tool(filename)
                return file_content

            if function_name == "search_web_tool":
                print("Web Search Tool")
                query = function_args["query"]
                search_results = search_web_tool(query)
                return search_results

            if function_name not in ["run_command_tool", "write_file_tool", "read_file_tool", "search_web_tool"]:
                raise Exception(f"Unknown tool {function_name}")
    else:
        print(f"(No tool call in model's response) {response_message}")
        return response_message.content
  

def chat_with_claude(user_message):
    print(f"\n{'='*50}\nUser Message: {user_message}\n{'='*50}")

    client = Anthropic(
        api_key=ANTHROPIC_API_KEY,
    )

    MODEL_NAME = "claude-3-opus-20240229"

    message = client.beta.tools.messages.create(
        model=MODEL_NAME,
        system=SYSTEM_PROMPT,
        max_tokens=4096,
        messages=[{"role": "user", "content": user_message}],
        tools=claude_tools,
    )

    print(f"\nInitial Response:")
    print(f"Stop Reason: {message.stop_reason}")
    print(f"Content: {message.content}")

    if message.stop_reason == "tool_use":
        tool_use = next(block for block in message.content if block.type == "tool_use")
        tool_name = tool_use.name
        tool_input = tool_use.input

        print(f"\nTool Used: {tool_name}")
        print(f"Tool Input: {tool_input}")

        if tool_name == "run_command_tool":
            command = tool_input.command
            command_output = run_command_tool(command)
            return command_output
        elif tool_name == "write_file_tool":
            filename = tool_input.filename
            content = tool_input.content
            write_file_tool(filename, content)
        elif tool_name == "read_file_tool":
            filename = tool_input.filename
            file_content = read_file_tool(filename)
            return file_content
        elif tool_name == "search_web_tool":
            query = tool_input.query
            search_results = search_web_tool(query)
            return search_results
        else:
            raise Exception(f"Unknown tool {tool_name}")
