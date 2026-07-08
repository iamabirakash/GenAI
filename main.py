from dotenv import load_dotenv
from langchain_core.messages import HumanMessage, AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.2,
    api_key=os.getenv("API_KEY"),
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Answer clearly and concisely."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

chain = prompt | model
messages = []

while True:
    user_input = input("You: ")
    if user_input.lower() in ["exit", "quit"]:
        break

    response = chain.invoke({
        "history": messages,
        "input": user_input,
    })
    print("AI:", response.content)

    messages.append(HumanMessage(content=user_input))
    messages.append(AIMessage(content=response.content))
