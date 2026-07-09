from dotenv import load_dotenv
from google.auth import default
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableBranch
from langchain_openai import ChatOpenAI
import os

load_dotenv()

model = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY"),
)

kidsStory = PromptTemplate.from_template(
    """
    Write a good kids story which should be good and should be backed with a moral story.
    Write the story for a kid of age {age}.
    """
)

horrorStory = PromptTemplate.from_template(
    """
    Write a good horror story which has good story line.
    Write the story for a adult of age {age}.
    """
)

defaultStory = PromptTemplate.from_template(
    """
    Write a funny story which has good story line.
    Write the story for a person of age {age}.
    """
)

parser = StrOutputParser()

def func1(inputs):
    return inputs["age"] < 18

def func2(inputs):
    return inputs["age"] > 18

conditional_chain = RunnableBranch(
    (func1, kidsStory | model | parser),
    (func2, horrorStory | model | parser),
    defaultStory | model | parser
)

while True:
    age = input("Enter your age: ")
    if(age=="exit"):
        break
    response = conditional_chain.invoke({"age": int(age)})
    print("\nGenerated Story:\n", response)