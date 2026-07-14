from langchain_core.prompts import ChatPromptTemplate
from dotenv import load_dotenv
import os
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain_classic.agents import create_tool_calling_agent, AgentExecutor

load_dotenv()

# -----------------------------
# Tool 1
# -----------------------------
@tool
def add_numbers(a: int, b: int) -> int:
    """Adds two numbers."""
    return a + b


# -----------------------------
# Tool 2
# -----------------------------
@tool
def weather_jalandhar() -> str:
    """Returns the current temperature in Jalandhar."""
    return "The current temperature in Jalandhar is 36°C."


# -----------------------------
# Create LLM
# -----------------------------
llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY"),
)

# -----------------------------
# Create Prompt
# -----------------------------
prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful assistant."),
    ("human", "{input}"),
    ("placeholder", "{agent_scratchpad}")
])

# -----------------------------
# Create Agent
# -----------------------------
tools = [add_numbers, weather_jalandhar]

agent = create_tool_calling_agent(
    llm=llm,
    tools=tools,
    prompt=prompt
)

# -----------------------------
# Create Agent Executor
# -----------------------------
agent_executor = AgentExecutor(
    agent=agent,
    tools=tools,
    verbose=True
)

# ==================================================
# Example : Addition
# ==================================================
response = agent_executor.invoke({
    "input": "Tell me the current temperature of Jalandhar & add 4 to it"
})

print("\nAddition Output")
print("\n")
print(response["output"])


# import os
# from dotenv import load_dotenv
# from langchain_openai import ChatOpenAI
# from langchain_tavily import TavilySearch

# load_dotenv()

# llm = ChatOpenAI(
#     model="gpt-5.4-mini",
#     temperature=0.9,
#     api_key=os.getenv("OPENAI_API_KEY"),
# )

# # Create Tool
# search_tool = TavilySearch(max_results=2, tavily_api_key=os.getenv("TAVILY_SEARCH_API"))

# # Bind Tool
# llm_with_tools = llm.bind_tools([search_tool])

# # Tool Calling
# response = llm_with_tools.invoke(
#     "Tell me the todays latest news"
# )

# print(response)
# print("====================")

# print(response.tool_calls)
# print("========= ===========")

# # Tool Execution
# tool_call = response.tool_calls[0]
# print(tool_call);
# print("========= ===========")

# # result = search_tool.invoke(tool_call["args"])
# result = search_tool.invoke(tool_call["args"]["query"])
# print("\n")
# print("========== Search_Tool_Query ==========")
# print(tool_call["args"]["query"])
# print("\n")

# print(result)
