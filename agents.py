import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Create Tool
search_tool = TavilySearch(max_results=2, tavily_api_key=os.getenv("TAVILY_SEARCH_API"))

# Bind Tool
llm_with_tools = llm.bind_tools([search_tool])

# Tool Calling
response = llm_with_tools.invoke(
    "Tell me the todays latest news"
)

print(response.tool_calls)
# Tool Execution
tool_call = response.tool_calls[0]

# result = search_tool.invoke(tool_call["args"])
result = search_tool.invoke(tool_call["args"]["query"])

print(result)
