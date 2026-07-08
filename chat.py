from dotenv import load_dotenv
import os

import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

st.set_page_config(
    page_title="College Research Assistant",
    page_icon="🎓",
    layout="wide",
)

st.title("College Research Assistant")
st.write("Type a university or college name, then ask follow-up questions using the chat history.")

api_key = os.getenv("API_KEY")
if not api_key:
    st.error("API_KEY is not set in your environment. Add it to your .env file before running the app.")
    st.stop()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.2,
    api_key=api_key,
)

prompt_template = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are an expert education and career counselor. Provide accurate, balanced, and student-friendly information. "
        "Use the chat history to understand follow-up questions. If the user asks 'its location' or similar, answer about the last college or university discussed. "
        "If a detail is uncertain or not well verified, say so instead of guessing. Do not invent rankings, placement numbers, fees, or admissions data.",
    ),
    MessagesPlaceholder(variable_name="history"),
    (
        "human",
        "{user_input}\n\nIf the user entered only a college or university name, write a concise report including location, history, courses offered, campus facilities, faculty, placements, rankings or recognition, admission process, student life, and a short conclusion. If the user asked a follow-up question, answer that question using the previous chat context.",
    ),
])

chain = prompt_template | model | StrOutputParser()

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Sure! Please tell me the name of the college. I will provide a detailed report covering its history, academics, placements, campus life, and admissions.",
        }
    ]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_input = st.chat_input("Type a university name or ask a follow-up question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.chat_message("user"):
        st.write(user_input)

    history = [
        HumanMessage(content=message["content"])
        if message["role"] == "user"
        else AIMessage(content=message["content"])
        for message in st.session_state.messages[:-1]
    ]

    with st.chat_message("assistant"):
        with st.spinner("Generating response..."):
            result = chain.invoke(
                {
                    "history": history,
                    "user_input": user_input.strip(),
                }
            )
        st.write(result)

    st.session_state.messages.append({"role": "assistant", "content": result})