from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
import os

load_dotenv()

model = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    temperature=1.9,
    api_key=os.getenv("API_KEY"),
)

# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a dark standup comedian. Be funny and sarcastic."),
#     ("ai", "Sure, I can do that. But just a heads up, my jokes are so dark, they make the night look like a sunny day."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}"),
# ])

prompt = PromptTemplate.from_template(
    "Tell {no_of_jokes} dark jokes about {topic}"
)

history=[]

while True:
    no_of_jokes = input("You: ")
    topic = input("You: ")
    # if user_input.lower() == "exit":
    #     break
    # newprompt = prompt.invoke({
    #     "history": history,
    #     "input": user_input
    # })
    # response = model.invoke(newprompt)
    parser = StrOutputParser()
    chain = prompt | model | parser
    response = chain.invoke({
        "history": history,
        "no_of_jokes": no_of_jokes,
        "topic": topic
    })
    print(f"AI: {response}\n")
    history.append(HumanMessage(content=f"{no_of_jokes} {topic}"))
    history.append(AIMessage(content=response))