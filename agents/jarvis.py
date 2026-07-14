import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()

llm = ChatOpenAI(
    model="gpt-4.1",
    temperature=0.8,
    api_key=os.getenv("OPENAI_API_KEY")
)

@tool
def open_vscode(text: str) -> str:
    """Opens VS Code."""
    return "Opening VS Code"

@tool
def open_chrome(text: str) -> str:
    """Opens Chrome."""
    return "Opening Chrome"

tools = [open_vscode, open_chrome]

# Bind tools to the LLM (passing the tools list directly)
llm_binding = llm.bind_tools(tools)

# Invoke the model
response = llm_binding.invoke(
    "Hey Jarvis, open vs code"
)

# print("LLM Response:")
# print(response)
# print("====================")

# Execute the requested tool call(s)
if response.tool_calls:
    tool_map = {t.name: t for t in tools}
    for tool_call in response.tool_calls:
        name = tool_call["name"]
        args = tool_call["args"]
        print(f"Jarvis is executing tool: {name} with args: {args}")
        if name in tool_map:
            result = tool_map[name].invoke(args)
            print(f"Tool Output: {result}")
        else:
            print(f"Tool {name} not found in tools list.")
else:
    print("No tool call was triggered.")