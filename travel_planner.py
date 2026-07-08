from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import os

load_dotenv()

model1 = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY"),
)