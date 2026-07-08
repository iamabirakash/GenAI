from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    temperature=1.9,
    api_key=os.getenv("API_KEY"),
)

prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a dark standup comedian. Be funny and sarcastic."),
    ("ai", "Sure, I can do that. But just a heads up, my jokes are so dark, they make the night look like a sunny day."),
    MessagesPlaceholder(variable_name="history"),
    ("human", "{input}"),
])

history=[]

while True:
    user_input = input("You: ")
    if user_input.lower() == "exit":
        break
    newprompt = prompt.invoke({
        "history": history,
        "input": user_input
    })
    response = model.invoke(newprompt)
    print(f"AI: {response.content}\n")
    history.append(HumanMessage(content=user_input))
    history.append(AIMessage(content=response.content))