import os
from typing import TypedDict, Annotated, List
from langgraph.graph import StateGraph, END, START
from langgraph.checkpoint.memory import InMemorySaver
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage
from dotenv import load_dotenv
import operator

load_dotenv()

class State(TypedDict):
    message : Annotated(list,add_messages)
    summary: str

def token_count(messages):
    return sum(len(m.content.split()) for m in messages)

MAX_TOKENS = 100

def summarize_if_needed(state:State):
    if token_count(state['messages'])> MAX_TOKENS:
        messages = state["messages"]
        summary = state.get("summary","")

        if token_count(messages)<=MAX_TOKENS:
            return {}
        
        trimmed = list(messages)
        removed = []

        while token_count(trimmed)>MAX_TOKENS:
            removed.append(trimmed.pop(0))
        
        conversation = "\n".join(
            f"{msg.type}:{msg.content}"
            for msg in removed
        )

        summary_prompt = f"""
        Existing Summary:
        {summary}

        New Messages:
        {conversation}

        Update the summary to include new important details.
        Keep the summary concise and under 100 words.
        Return the updated summary:
        """

        summary_prompt 

def chatBot(state:State):
    prompt = []

    if(state.get("summary")):
        prompt.append(
            content=f"""
            Summary of conversation so far:
            {state['summary']}
            """
        )
    
    prompt.extend(state["messages"])
    response = llm.invoke(prompt)

    return {
        "messages": [
            response
        ]
    }

