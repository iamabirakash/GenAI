from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    num1: int
    num2: int
    operation: str
    final_number: int

def addition(state: AgentState)->AgentState:
    state["final_number"] = state["num1"] + state["num2"]
    return state

def subtract(state: AgentState)->AgentState:
    state["final_number"] = state["num1"] - state["num2"]
    return state

def conditional(state: AgentState)->AgentState:
    return state

def deciding_function(state: AgentState)->str:
    if state["operation"] == "+":
        return "addition_edge"
    elif state["operation"] == "-":
        return "subtract_edge"
    return "addition_edge" 
    
graph = StateGraph(AgentState)

graph.add_node("add_node",addition)
graph.add_node("subtract_node",subtract)
graph.add_node("conditional_node",conditional)

graph.set_entry_point("conditional_node")

graph.add_conditional_edges(
    "conditional_node", deciding_function, {
        "addition_edge": "add_node",
        "subtract_edge": "subtract_node",
    },
)

graph.set_finish_point("add_node")
graph.set_finish_point("subtract_node")

app = graph.compile()

result = app.invoke({"num1": 10, "num2": 20, "operation": "+", "final_number": 0})
print(result)
