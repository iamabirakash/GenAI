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
def weather_of_jalandhar(text: str) -> str:
    """Get weather of Jalandhar."""
    return 36

print(weather_of_jalandhar.invoke("Jalandhar"))
