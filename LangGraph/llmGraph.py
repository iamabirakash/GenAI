from typing import TypedDict, List
from langgraph.graph import StateGraph
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
import os
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    human: str
    ai: str

def llmResponder(state:AgentState) -> AgentState:
    model = ChatOpenAI(
        model="gpt-4o",
        temperature=0.9,
        openai_api_key=os.getenv("OPENAI_API_KEY")
    )
    result = model.invoke(state['human'])
    state['ai'] = result.content
    return state

graph = StateGraph(AgentState)
graph.add_node("llmResponder", llmResponder)
graph.set_entry_point("llmResponder")
graph.set_finish_point("llmResponder")

app = graph.compile()

result = app.invoke({"human": "Hello"})
print(result['ai'])