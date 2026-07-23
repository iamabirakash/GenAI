import os
from crewai import Agent,Task,Crew,LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.9,
    api_key=os.getenv("API_KEY")
)

greeter = Agent(
    role="You are a greeter",
    goal="Greet the User",
    backstory=(
        "You are an polite Greeter"
    ),
    llm = llm,
    verbose = True
)

task = Task(
    description="""
        Greet the user with proper greeting
        name:
        {name}
        """,
        expected_output = "A polite greeting",
        agent=greeter,
)

crew = Crew(
    agents = [greeter],
    tasks = [task],
    verbose = True,
)

# result = crew.kickoff()
result = crew.kickoff(inputs={"name": "abir"})

print(result)