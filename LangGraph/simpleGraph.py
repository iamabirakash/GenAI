from typing import TypedDict, Dict,List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    name : str
    age : int
    marks : List[int]
    msg : str

def Processor(state: AgentState) -> AgentState:
    print(f"Hello {state['name']}")
    print(f"Your age is {state['age']}")
    print(f"Your marks are {state['marks']}")
    print(f"Your message is {state['msg']}")
    print(f"Sum of marks is {sum(state['marks'])}")

graph = StateGraph(AgentState)
graph.add_node("Processor", Processor)  #"Processor" is the name of the node, Processor is the function that will be executed when this node is reached
graph.set_entry_point("Processor")
graph.set_finish_point("Processor")

app = graph.compile()

app.invoke({"name": "Abir", "age": 23, "marks": [90, 80, 70], "msg": "Hello World!"})

'''
# class AgentState(TypedDict):
#     msg : str

# def hello_world(state: AgentState) -> AgentState:
#     state["msg"] = "Hii, How are you doing?"
#     return state

# graph = StateGraph(AgentState)
# graph.add_node("Abir Akash", hello_world)  #"hello world" is the name of the node, hello_world is the function that will be executed when this node is reached
# graph.set_entry_point("Abir Akash")
# graph.set_finish_point("Abir Akash")

# app = graph.compile()

# result = app.invoke({"msg": ""})

# print(result)
'''