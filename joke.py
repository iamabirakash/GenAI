from dotenv import load_dotenv
from langchain_core.messages import HumanMessage,AIMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder, PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from langchain_core.runnables import RunnableLambda
import os

load_dotenv()

model1 = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY"),
)

model2 = ChatAnthropic(
    model="claude-sonnet-5",
    api_key=os.getenv("ANTHROPIC_API_KEY")
)

# prompt = ChatPromptTemplate.from_messages([
#     ("system", "You are a dark standup comedian. Be funny and sarcastic."),
#     ("ai", "Sure, I can do that. But just a heads up, my jokes are so dark, they make the night look like a sunny day."),
#     MessagesPlaceholder(variable_name="history"),
#     ("human", "{input}"),
# ])

prompt1 = PromptTemplate.from_template(
    "Tell {no_of_jokes} dark jokes about {topic}"
)

prompt2 = PromptTemplate.from_template(
    """You are a comedy expert.
    Analyze these jokes:
    {joke}
    Create a funnier version of each joke.
    For each joke, return:
    - Old joke: [original joke]
    - New joke: [improved version]
    - Analysis: [why the new version is funnier]
    Make the new jokes DARKER and more SARCASTIC than the originals!"""
)

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
    chain = (
        prompt1 | model1 | parser | RunnableLambda(lambda joke: {"joke": joke}) | prompt2 | model2 | parser
    )
    response = chain.invoke({
        "no_of_jokes": no_of_jokes,
        "topic": topic
    })
    print(f"AI: {response}\n")