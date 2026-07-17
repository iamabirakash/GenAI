from typing import TypedDict,List
from langgraph.graph import StateGraph,START,END

class AgentState(TypedDict):
    num: int
    ai_guess: int
    secret_number: int
    count: int

def setup(state:AgentState)->AgentState:
    state["ai_guess"] = 50
    state["count"] = 0
    print("AI Guessing game started")
    return state

#initially the ai guesses number 50, if it equal then it returns, and if it not then it goes to hint and then the hint says if it is greater or smaller then the secret number, and it increments and decremenyts accordingly
def aiGuess(state:AgentState)->AgentState:
    state["count"] += 1
    if state["ai_guess"] == state["secret_number"]:
        print(f"AI guessed the number: {state['secret_number']} in {state['count']} attempts")
    
    return state
    

def hint(state:AgentState)->AgentState:
    if state["ai_guess"] < state["secret_number"]:
        print(f"Secret number is HIGHER than {state['ai_guess']}")
        state["ai_guess"] += 1 
    else:
        print(f"Secret number is LOWER than {state['ai_guess']}")
        state["ai_guess"] -= 1
    
    return state

def should_continue(state: AgentState) -> str:
    if state["ai_guess"] == state["secret_number"]:
        return "end"
    else:
        return "hint"

graph = StateGraph(AgentState)

graph.add_node("setup", setup)
graph.add_node("aiGuess", aiGuess)
graph.add_node("hint", hint)

graph.add_edge(START, "setup")
graph.add_edge("setup", "aiGuess")

graph.add_conditional_edges(
    "aiGuess", should_continue, {
        "hint": "hint",
        "end": END,
    }
)

graph.add_edge("hint", "aiGuess")

app = graph.compile()

result = app.invoke({"num": 10, "ai_guess": 0, "secret_number": 42, "count": 0})
print(result)