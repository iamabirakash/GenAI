import os
from crewai import Agent,Task,Crew,LLM
from crewai.tools import BaseTool
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.9,
    api_key=os.getenv("API_KEY")
)

research = Agent(
    role="Professional Researcher",
    goal="Give all the facts and information regarding the topic",
    backstory="You are a professional researcher who researches through the web and gives out all the facts and information",
    llm = llm,
    verbose = True
)

blog = Agent(
    role="Professional Blog Writer",
    goal="Write a Professional blog on the topic",
    backstory="You are experienced and professional blog writer",
    llm = llm,
    verbose = True
)

research_task = Task(
    description="""
        Research comprehensively about {topic} and give 5 intresting facts.
    """,
    expected_output="A list of 5 most intresting facts on the {topic}.",
    agent=research
)

blog_task = Task(
    description="""
        Write a professional blog post about {topic} using the research provided.
        The blog should be engaging, well-structured, and informative.
        Include an introduction, key points, and a conclusion.
    """,
    expected_output="A well-written professional blog post about {topic}.",
    agent=blog
)

crew = Crew(
    agents=[research,blog],
    tasks=[research_task,blog_task],
    verbose=True
)

result = crew.kickoff(inputs={"topic": "Global Warming"})

print(result)