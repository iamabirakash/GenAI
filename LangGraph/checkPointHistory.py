import os
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import operator

load_dotenv()

# Define the state
class State(TypedDict):
    messages: Annotated[List[dict], operator.add]

# Initialize the LLM
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",  # Using available model
    api_key=os.getenv("API_KEY"),
    temperature=0.7
)

# Define the node function
def call_llm(state: State):
    """Call the LLM with the current messages."""
    # Get the messages from state
    messages = state["messages"]
    
    # Convert dict messages to LangChain message objects if needed
    if messages and isinstance(messages[0], dict):
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        converted = []
        for msg in messages:
            if msg["role"] == "user":
                converted.append(HumanMessage(content=msg["content"]))
            elif msg["role"] == "assistant":
                converted.append(AIMessage(content=msg["content"]))
            elif msg["role"] == "system":
                converted.append(SystemMessage(content=msg["content"]))
        messages = converted
    
    # Get response from LLM
    response = llm.invoke(messages)
    
    # Return updated state
    return {
        "messages": [{"role": "assistant", "content": response.content}]
    }

# Create the graph
graph = StateGraph(State)

# Add the node
graph.add_node("llm_node", call_llm)

# Add edges
graph.add_edge(START, "llm_node")
graph.add_edge("llm_node", END)

# Set up checkpoint
memory = InMemorySaver()
app = graph.compile(checkpointer=memory)

# Configuration for the thread
config = {
    "configurable": {
        "thread_id": "thread_id_1"
    }
}

# First interaction
print("="*50)
print("First Interaction")
print("="*50)
res1 = app.invoke(
    {
        "messages": [
            {"role": "user", "content": "Hi, I'm Abir Akash"}
        ]
    },
    config=config
)

print("Response:")
for msg in res1["messages"]:
    role = msg.get("role", "unknown")
    content = msg.get("content", "")
    print(f"{role}: {content}")

# Second interaction - continuing the conversation
print("\n" + "="*50)
print("Second Interaction (Context Maintained)")
print("="*50)
res2 = app.invoke(
    {
        "messages": [
            {"role": "user", "content": "What's my name?"}
        ]
    },
    config=config
)

print("Response:")
for msg in res2["messages"]:
    role = msg.get("role", "unknown")
    content = msg.get("content", "")
    print(f"{role}: {content}")

# Get the current state
print("\n" + "="*50)
print("Current State")
print("="*50)
current_state = app.get_state(config)
print(f"Number of messages: {len(current_state.values['messages'])}")
print("All messages:")
for msg in current_state.values["messages"]:
    role = msg.get("role", "unknown")
    content = msg.get("content", "")[:100] + "..." if len(msg.get("content", "")) > 100 else msg.get("content", "")
    print(f"  {role}: {content}")

# import os
# from typing import TypedDict, Annotated, List
# from langgraph.graph import StateGraph, END
# from langgraph.checkpoint.sqlite import SqliteSaver
# from langchain_google_genai import ChatGoogleGenerativeAI
# from langchain_core.messages import HumanMessage, AIMessage
# from dotenv import load_dotenv

# load_dotenv()

# class State(TypedDict):
#     messsages : Annotated(list, operator.add)


# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     api_key=os.getenv("GEMINI_API_KEY")
# )

# config = {
#     "configurable": {
#         "thread_id": "thread_id_1"
#     }
# }

# graph.add_node("llm",llm)
# graph.add_edge(START,llm)
# graph.add_edge(llm,END)

# memory = InMemorySaver()
# app = graph.compile(checkpointer=memory)

# res = app.invoke(
#     {"messages":[
#         HumanMessage(content="Hi, Im Abir Akash")
#     ]
#     }, config=config
# )

# print(res)