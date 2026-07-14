import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.tools import tool

load_dotenv()

llm = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY"),
)

@tool
def add_nums(num1: int, num2: int) -> int:
    """Add two numbers."""
    return num1 + num2

result = add_nums.invoke({"num1": 1, "num2": 2})
print(result)