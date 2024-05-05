import subprocess
import requests
import os
import os
import json
import re
from groq import Groq
from anthropic import Anthropic


GROQ_API_KEY = os.environ["GROQ_API_KEY"]
E2B_API_KEY = os.environ["E2B_API_KEY"]
ANTHROPIC_API_KEY = os.environ["ANTHROPIC_API_KEY"]
groq_client = Groq(api_key=GROQ_API_KEY)


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
          }
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
  }
]


claude_tools = [
    {
        "name": "run_command_tool",
        "description": "Executes a terminal command and returns the standard output.",
        "input_schema": {
            "type": "object",
            "properties": {
                "command": {
                    "type": "string",
                    "description": "The command to execute in the terminal."
                }
            },
            "required": ["command"]
        }
    },
    {
        "name": "write_file_tool",
        "description": "Writes content to a specified file.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file to write to."
                },
                "content": {
                    "type": "string",
                    "description": "The content to write into the file."
                }
            },
            "required": ["filename", "content"]
        }
    },
    {
        "name": "read_file_tool",
        "description": "Reads content from a specified file and returns it.",
        "input_schema": {
            "type": "object",
            "properties": {
                "filename": {
                    "type": "string",
                    "description": "The name of the file to read from."
                }
            },
            "required": ["filename"]
        }
    },
]

# Terminal Access | Run Command and observe output
def run_command_tool(command):
  print(f"Executing command: {command}")
  result = subprocess.run([command], shell=True, capture_output=True, text=True)
  if result.stderr:
     print(f"Error executing command: {result.stderr}")
     return result.stderr
  print(f"Command output:\n{result.stdout}")
  return result.stdout

# Write File | Write File content into system
def write_file_tool(filename, content):
    print(f"Writing content to file: {filename}")
    with open(filename, 'w') as file:
        file.write(content)
    print(f"Content successfully written to file: {filename}")    
    
    
    if filename.endswith(".py"):
        try:
            print(f"Executing Python script: {filename}")
            result = subprocess.run(["python", filename], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"Python script executed successfully:\n{result.stdout}")
            else:
                print(f"Error executing Python script:\n{result.stderr}")
                # Fix any errors and rerun the script -- NEED TO FIGURE OUT HOW TO FIX ERRORS
                print("Fixing errors and rerunning the script...")
                result = subprocess.run(["python", filename], capture_output=True, text=True)
                if result.returncode == 0:
                    print(f"Python script executed successfully after fixing the errors:\n{result.stdout}")
                else:
                    print(f"Error executing Python script after fixing the errors:\n{result.stderr}")
        except Exception as e:
            print(f"Error executing Python script: {e}")

# Read File | Read file and get content
def read_file_tool(filename):
    try:
        print(f"Reading content from file: {filename}")
        with open(filename, 'r') as file:
            file_content = file.read()
        print(f"Content read from file: {filename}")
        return file_content
    except FileNotFoundError:
        print(f"File not found: {filename}")
        return None
    except Exception as e:
        print(f"Error reading file: {e}")
        return None
    
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

def prompt_for_next_action():
    while True:
        choice = input("What would you like to do next? (1. Perform another task, 2. Exit): ")
        if choice == "1":
            return True
        elif choice == "2":
            print("Exiting...")
            return False
        else:
            print("Invalid choice. Please enter 1 or 2.")
            
def display_welcome_message():
    print("=" * 50)
    print("Welcome to the Operating System Assistant!")
    print("This assistant helps you perform various tasks related to the operating system.")
    #print(SYSTEM_PROMPT)
    print("=" * 50)

  
def chat_with_llama(user_message):
  """ 
  llama3-70b groq enabled version ; with tools
  """
  print(f"\n{'='*50}\nUser message: {user_message}\n{'='*50}")

  messages = [
      {"role": "system", "content": SYSTEM_PROMPT},
      {"role": "user", "content": user_message}
  ]

  MODEL_NAME = "llama3-70b-8192"

  response = groq_client.chat.completions.create(
      model=MODEL_NAME,
      messages=messages,
      tools=tools,
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
      
      if function_name not in ["run_command_tool", "write_file_tool", "read_file_tool"]:
        raise Exception(f"Unknown tool {function_name}")
  else:
    print(f"(No tool call in model's response) {response_message}")
    return []
  
  

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
        else:
            raise Exception(f"Unknown tool {tool_name}")
            
       

        
