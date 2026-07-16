from typing import TypedDict, Dict
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    msg : str

def hello_world(state: AgentState) -> AgentState:
    state["msg"] = "Hello World"
    return state

graph = StateGraph(AgentState)
graph.add_node("Abir Akash", hello_world)  #"hello world" is the name of the node, hello_world is the function that will be executed when this node is reached
graph.set_entry_point("Abir Akash")
graph.set_finish_point("Abir Akash")

app = graph.compile()

result = app.invoke({"msg": ""})

print(result)