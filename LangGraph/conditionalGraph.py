from typing import TypedDict, List
from langgraph.graph import StateGraph

class AgentState(TypedDict):
    num1: int
    num2: int
    num3: int
    operation1: str
    operation2: str
    final_num: int

def addition(state: AgentState) -> AgentState:
    state["final_num"] = state["num1"] + state["num2"]
    return state;

def subtraction(state: AgentState) -> AgentState:
    state["final_num"] = state["num1"] - state["num2"]
    return state;

def multiply(state: AgentState) -> AgentState:
    state["final_num"] = state["final_num"] * state["num3"]
    return state;

def divide(state: AgentState) -> AgentState:
    state["final_num"] = state["final_num"] / state["num3"]
    return state;

def condition(state: AgentState) -> AgentState:
    return state;

def end_node(state: AgentState) -> AgentState:
    return state

def decide_op1(state: AgentState) -> str:
    if(state["operation1"]=="+"):
        return "addition_edge"
    elif (state["operation1"]=="-"):
        return "subtraction_edge"

def decide_op2(state: AgentState) -> str:
    if(state["operation2"]=="*"):
        return "multiply_edge"
    elif (state["operation2"]=="/"):
        return "divide_edge"
    
graph = StateGraph(AgentState)

graph.add_node("add",addition)
graph.add_node("sub",subtraction)
graph.add_node("mul",multiply)
graph.add_node("div",divide)
graph.add_node("end_node",end_node)
graph.add_node("conditional_node",condition)

graph.set_entry_point("conditional_node")

def router(state: AgentState) -> AgentState:
    return state

graph.add_node("router", router)

graph.add_conditional_edges(
    "conditional_node", decide_op1, {
        "addition_edge": "add",
        "subtraction_edge": "sub",
    },
)

graph.add_edge("add", "router")
graph.add_edge("sub", "router")

graph.add_conditional_edges(
    "router", decide_op2,{
        "multiply_edge": "mul",
        "divide_edge": "div",
    }
)

# graph.set_finish_point("mul")
# graph.set_finish_point("div")
graph.add_edge("mul", "end_node")
graph.add_edge("div", "end_node")
graph.set_finish_point("end_node")

app = graph.compile()

result = app.invoke({"num1":10, "num2":20, "num3":30, "operation1":"+", "operation2":"*", "final_num":0})
print(result)


'''
# from typing import TypedDict, List
# from langgraph.graph import StateGraph

# class AgentState(TypedDict):
#     num1: int
#     num2: int
#     operation: str
#     final_number: int

# def addition(state: AgentState)->AgentState:
#     state["final_number"] = state["num1"] + state["num2"]
#     return state

# def subtract(state: AgentState)->AgentState:
#     state["final_number"] = state["num1"] - state["num2"]
#     return state

# def conditional(state: AgentState)->AgentState:
#     return state

# def deciding_function(state: AgentState)->str:
#     if state["operation"] == "+":
#         return "addition_edge"
#     elif state["operation"] == "-":
#         return "subtract_edge"
#     return "addition_edge" 
    
# graph = StateGraph(AgentState)

# graph.add_node("add_node",addition)
# graph.add_node("subtract_node",subtract)
# graph.add_node("conditional_node",conditional)

# graph.set_entry_point("conditional_node")

# graph.add_conditional_edges(
#     "conditional_node", deciding_function, {
#         "addition_edge": "add_node",
#         "subtract_edge": "subtract_node",
#     },
# )

# graph.set_finish_point("add_node")
# graph.set_finish_point("subtract_node")

# app = graph.compile()

# result = app.invoke({"num1": 10, "num2": 20, "operation": "+", "final_number": 0})
# print(result)
'''