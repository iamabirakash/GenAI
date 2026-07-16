from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    name: str
    age: int
    # msg: List[str]
    msg: str 

def greet(state: AgentState)->AgentState:
    # state["msg"].append(f"Hi {state['name']}, How are you?")
    state["msg"] += f"Hi {state['name']}, How are you?\n"
    return state

def greetWithAge(state: AgentState)->AgentState:
    # state["msg"].append(f"Hi {state['name']}, Your age is {state['age']}")
    state["msg"] += f"Hi {state['name']}, Your age is {state['age']}\n"
    return state

graph = StateGraph(AgentState)
graph.add_node("Node1", greet)
graph.add_node("Node2", greetWithAge)
graph.add_edge("Node1", "Node2")
graph.set_entry_point("Node1")
graph.set_finish_point("Node2")

app = graph.compile()
# result = app.invoke({"name": "Abir", "age": 23, "msg": []})
result = app.invoke({"name": "Abir", "age": 23, "msg": ""})
print(result["msg"])


# student = {
#     "marks": [100, 90]
# }

# student["marks"].append("Hello")
# print(student["marks"])