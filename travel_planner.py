from dotenv import load_dotenv
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.runnables import RunnableLambda, RunnableParallel, RunnablePassthrough
from langchain_openai import ChatOpenAI
import os

load_dotenv()

model = ChatOpenAI(
    model="gpt-5.4-mini",
    temperature=0.9,
    api_key=os.getenv("OPENAI_API_KEY"),
)

prompt1 = PromptTemplate.from_template(
    """
    You are a travel planner and tourist attraction spot finder.
    Provide a list of the best tourist attractions in {city}.
    For each place, include a detailed description of why it is famous.
    """
)

prompt2 = PromptTemplate.from_template(
    """
    You are a food critic.
    Provide a list of the best restaurants in {city}.
    For each restaurant, explain why it is famous and list its signature dishes.
    """
)

prompt3 = PromptTemplate.from_template(
    """
    You are a time management expert.
    Create a detailed day-wise itinerary for {city} for {no_of_days} days using the tourist attractions and restaurants below.
    Include practical time slots for each activity.
    """
)

parser = StrOutputParser()

chain1 = prompt1 | model | parser
chain2 = prompt2 | model | parser
chain3 = prompt3 | model | parser

parallel_chain = RunnableParallel(
    attractions=chain1,
    restaurants=chain2,
    itinerary=chain3
)

no_of_days = input("Enter the number of days for your trip: ")
city = input("Enter the city you want to visit: ")

response = parallel_chain.invoke({"city": city, "no_of_days": no_of_days})

print("\nTourist Attractions:\n", response["attractions"])
print("\nRestaurants:\n", response["restaurants"])
print("\nItinerary:\n", response["itinerary"])
