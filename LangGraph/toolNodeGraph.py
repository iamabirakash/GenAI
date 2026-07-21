from typing import TypedDict, List, Annotated
import operator
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
from langchain.tools import tool
import os
from dotenv import load_dotenv

load_dotenv()

class AgentState(TypedDict):
    num1: int
    num2: int
    sum: int

@tool
def add_numbers(state: AgentState) -> AgentState:
    state['sum'] = state['num1'] + state['num2']
    return state

graph = StateGraph(AgentState)
graph.add_node("add_numbers", add_numbers)
graph.add_edge(START, "add_numbers")
graph.add_edge("add_numbers", END)

app = graph.compile()

result = app.invoke({"num1": 1, "num2": 2, "sum": 0})
print(result)
