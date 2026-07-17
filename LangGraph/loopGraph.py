from typing import TypedDict, List
from langgraph.graph import StateGraph, START, END
from random import randint

class AgentState(TypedDict):
    name: str
    nums: List[int]
    counter: int

def greet(state: AgentState) -> AgentState:
    print("Hello, Running The Grid Function")
    return state

def randomNumber(state: AgentState) -> AgentState:
    number = randint(1, 10)
    state["nums"].append(number)
    state["counter"] += 1
    return state

def should_continue(state: AgentState) -> str:
    if state["counter"] < 5:
        return "loop"
    else:
        return "end"

graph = StateGraph(AgentState)

graph.add_node("greet", greet)
graph.add_node("random_no", randomNumber)

graph.add_edge(START, "greet")
graph.add_edge("greet", "random_no")

graph.add_conditional_edges(
    "random_no", should_continue, {
        "loop": "random_no",
        "end": END,
    }
)

app = graph.compile()

result = app.invoke({"name": "John", "nums": [], "counter": 0})
print(result)