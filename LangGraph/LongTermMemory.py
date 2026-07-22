import re
import sqlite3
from typing import TypedDict, List, Annotated

from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, SystemMessage, BaseMessage
from langchain_google_genai import ChatGoogleGenerativeAI

import os
from dotenv import load_dotenv
load_dotenv()

# ===========================
# LLM
# ===========================

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    api_key=os.getenv("API_KEY"),
    temperature=0.7
)

# ===========================
# SQLite Long-Term Memory
# ===========================

conn = sqlite3.connect(
    "ltm.db",
    check_same_thread=False
)

cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    user_id TEXT PRIMARY KEY,
    name TEXT,
    city TEXT
)
""")

conn.commit()


def get_profile(user_id):

    cursor.execute(
        "SELECT name, city FROM users WHERE user_id=?",
        (user_id,)
    )

    row = cursor.fetchone()

    if row is None:
        return {}

    return {
        "name": row[0],
        "city": row[1]
    }


def save_profile(user_id, profile):

    cursor.execute("""
    INSERT OR REPLACE INTO users(user_id,name,city)
    VALUES(?,?,?)
    """,
    (
        user_id,
        profile.get("name"),
        profile.get("city")
    ))

    conn.commit()


# ===========================
# Graph State
# ===========================

class State(TypedDict):
    # add_messages reducer appends new messages onto the checkpointed
    # history instead of overwriting it on every invoke() call.
    messages: Annotated[List[BaseMessage], add_messages]
    user_id: str
    thread_id: str
    profile: dict


# ===========================
# Nodes
# ===========================

def load_profile(state):

    state["profile"] = get_profile(state["user_id"])

    return state


def extract_profile(state):

    text = state["messages"][-1].content

    profile = state["profile"]

    name = re.search(
        r"my name is ([A-Za-z ]+)",
        text,
        re.I
    )

    city = re.search(
        r"i live in ([A-Za-z ]+)",
        text,
        re.I
    )

    if name:
        profile["name"] = name.group(1).strip()

    if city:
        profile["city"] = city.group(1).strip()

    save_profile(
        state["user_id"],
        profile
    )

    return state


def chatbot(state):

    profile = state["profile"]

    system_prompt = f"""You are a helpful AI assistant.

User Profile:
{profile}

Use the profile whenever relevant."""

    # Full running history (system prompt + all prior turns) is sent
    # each call since the LLM itself is stateless.
    response = llm.invoke(
        [
            SystemMessage(content=system_prompt),
            *state["messages"]
        ]
    )

    state["messages"].append(response)

    return state


# ===========================
# Build Graph
# ===========================

builder = StateGraph(State)

builder.add_node("load_profile", load_profile)
builder.add_node("extract_profile", extract_profile)
builder.add_node("chatbot", chatbot)

builder.set_entry_point("load_profile")

builder.add_edge("load_profile", "extract_profile")
builder.add_edge("extract_profile", "chatbot")
builder.add_edge("chatbot", END)

graph = builder.compile(
    checkpointer=MemorySaver()
)

# ===========================
# Chat Loop
# ===========================

USER_ID = "abir"

THREAD_ID = input("Thread ID: ")

config = {
    "configurable": {
        "thread_id": THREAD_ID
    }
}

print("\nType 'exit' to quit.\n")

while True:

    question = input("You : ")

    if question.lower() == "exit":
        break

    result = graph.invoke(
        {
            "messages": [
                HumanMessage(content=question)
            ],
            "user_id": USER_ID,
            "thread_id": THREAD_ID
        },
        config=config
    )

    print("\nAI :", result["messages"][-1].content)

# import re
# import sqlite3
# from typing import TypedDict, List

# from langgraph.graph import StateGraph, END
# from langgraph.checkpoint.memory import MemorySaver
# from langchain_core.messages import HumanMessage, AIMessage, BaseMessage
# from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
# from langchain_chroma import Chroma

# import os
# from dotenv import load_dotenv
# load_dotenv()

# # ===========================
# # LLM
# # ===========================

# llm = ChatGoogleGenerativeAI(
#     model="gemini-2.5-flash",
#     api_key=os.getenv("API_KEY"),
#     temperature=0.7
# )

# # embeddings = GoogleGenerativeAIEmbeddings(model="gemini-embedding-001")
# embeddings = GoogleGenerativeAIEmbeddings(
#     model="models/embedding-001",
#     google_api_key=os.getenv("API_KEY")
# )

# # ===========================
# # SQLite Long-Term Memory
# # ===========================

# conn = sqlite3.connect(
#     "ltm.db",
#     check_same_thread=False
# )

# cursor = conn.cursor()

# cursor.execute("""
# CREATE TABLE IF NOT EXISTS users(
#     user_id TEXT PRIMARY KEY,
#     name TEXT,
#     city TEXT
# )
# """)

# conn.commit()


# def get_profile(user_id):

#     cursor.execute(
#         "SELECT name, city FROM users WHERE user_id=?",
#         (user_id,)
#     )

#     row = cursor.fetchone()

#     if row is None:
#         return {}

#     return {
#         "name": row[0],
#         "city": row[1]
#     }


# def save_profile(user_id, profile):

#     cursor.execute("""
#     INSERT OR REPLACE INTO users(user_id,name,city)
#     VALUES(?,?,?)
#     """,
#     (
#         user_id,
#         profile.get("name"),
#         profile.get("city")
#     ))

#     conn.commit()


# # ===========================
# # Vector Store
# # ===========================

# vector_db = Chroma(
#     collection_name="memory",
#     embedding_function=embeddings,
#     persist_directory="./vector_db"
# )


# def add_memory(user_id, thread_id, text):

#     vector_db.add_texts(
#         [text],
#         metadatas=[
#             {
#                 "user_id": user_id,
#                 "thread_id": thread_id
#             }
#         ]
#     )


# def retrieve_memory(user_id, query):

#     docs = vector_db.similarity_search(
#         query,
#         k=3,
#         filter={
#             "user_id": user_id
#         }
#     )

#     return docs


# # ===========================
# # Graph State
# # ===========================

# class State(TypedDict):
#     messages: List[BaseMessage]
#     user_id: str
#     thread_id: str
#     profile: dict
#     memories: list


# # ===========================
# # Nodes
# # ===========================

# def load_profile(state):

#     state["profile"] = get_profile(state["user_id"])

#     return state


# def search_memories(state):

#     question = state["messages"][-1].content

#     state["memories"] = retrieve_memory(
#         state["user_id"],
#         question
#     )

#     return state


# def extract_profile(state):

#     text = state["messages"][-1].content

#     profile = state["profile"]

#     name = re.search(
#         r"my name is ([A-Za-z ]+)",
#         text,
#         re.I
#     )

#     city = re.search(
#         r"i live in ([A-Za-z ]+)",
#         text,
#         re.I
#     )

#     if name:
#         profile["name"] = name.group(1).strip()

#     if city:
#         profile["city"] = city.group(1).strip()

#     save_profile(
#         state["user_id"],
#         profile
#     )

#     return state


# def chatbot(state):

#     profile = state["profile"]

#     memory_text = "\n".join(
#         doc.page_content
#         for doc in state["memories"]
#     )

#     system_prompt = f"""
# You are a helpful AI assistant.

# User Profile:
# {profile}

# Relevant Cross Thread Memories:
# {memory_text}

# Use the profile and memories whenever relevant.
# """

#     response = llm.invoke(
#         [
#             AIMessage(content=system_prompt),
#             *state["messages"]
#         ]
#     )

#     add_memory(
#         state["user_id"],
#         state["thread_id"],
#         state["messages"][-1].content
#     )

#     state["messages"].append(response)

#     return state


# # ===========================
# # Build Graph
# # ===========================

# builder = StateGraph(State)

# builder.add_node("load_profile", load_profile)
# builder.add_node("search_memories", search_memories)
# builder.add_node("extract_profile", extract_profile)
# builder.add_node("chatbot", chatbot)

# builder.set_entry_point("load_profile")

# builder.add_edge("load_profile", "search_memories")
# builder.add_edge("search_memories", "extract_profile")
# builder.add_edge("extract_profile", "chatbot")
# builder.add_edge("chatbot", END)

# graph = builder.compile(
#     checkpointer=MemorySaver()
# )

# # ===========================
# # Chat Loop
# # ===========================

# USER_ID = "abir"

# THREAD_ID = input("Thread ID: ")

# config = {
#     "configurable": {
#         "thread_id": THREAD_ID
#     }
# }

# print("\nType 'exit' to quit.\n")

# while True:

#     question = input("You : ")

#     if question.lower() == "exit":
#         break

#     result = graph.invoke(
#         {
#             "messages": [
#                 HumanMessage(content=question)
#             ],
#             "user_id": USER_ID,
#             "thread_id": THREAD_ID
#         },
#         config=config
#     )

#     print("\nAI :", result["messages"][-1].content)