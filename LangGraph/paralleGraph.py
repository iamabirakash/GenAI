from typing import TypedDict, List, Annotated  # Add Annotated
import operator  # Add operator
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, START, END
import os
from dotenv import load_dotenv

load_dotenv()

model = ChatOpenAI(
    model="gpt-4o",
    temperature=0.9,
    openai_api_key=os.getenv("OPENAI_API_KEY")
)

class AgentState(TypedDict):
    name: str
    human: str
    ai: str
    topic: str
    # FIX: Add Annotated with operator.add to handle concurrent updates
    funny: str;
    formal: str;
    cringe: str;


def greet(state: AgentState) -> AgentState:
    state['human'] = f"Hi {state['name']}, generating tweets on {state['topic']}"

    return {"human": state['human']}  # Return only the updated field

def funny(state: AgentState) -> AgentState:
    tweets = model.invoke(f"Generate funny tweets on {state['topic']}").content
    # Return as a list so the reducer can append it
    return {"funny": tweets}

def formal(state: AgentState) -> AgentState:
    tweets = model.invoke(f"Generate formal tweets on {state['topic']}").content
    return {"formal": tweets}

def cringe(state: AgentState) -> AgentState:
    tweets = model.invoke(f"Generate cringe tweets on {state['topic']}").content
    return {"cringe": tweets}

# The rest of your graph definition stays the same
graph = StateGraph(AgentState)
graph.add_node("greet", greet)
graph.add_node("funny", funny)
graph.add_node("formal", formal)
graph.add_node("cringe", cringe)

graph.add_edge(START, "greet")
graph.add_edge("greet", "funny")
graph.add_edge("greet", "formal")
graph.add_edge("greet", "cringe")
graph.add_edge("funny", END)
graph.add_edge("formal", END)
graph.add_edge("cringe", END)

app = graph.compile()

result = app.invoke({"name": "Abir", "topic": "AI", "funny": "", "formal": "", "cringe": ""})
print(result)