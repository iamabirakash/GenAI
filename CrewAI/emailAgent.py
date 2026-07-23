import os
from crewai import Agent,Task,Crew,LLM
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.9,
    api_key=os.getenv("API_KEY")
)

email = """
        hey team,
        wip is almost done.
        I will send the report tomorrow.
        thank.        
    """

email_agent = Agent(
    role="Professional Email Writer",
    goal="Rewrite emails in a professional tone",
    backstory=(
        "You are an expert business communication specialist who writes clear, polite and professional emails."
    ),
    llm = llm,
    verbose = True
)

task = Task(
    description="""
        Rewritethe following email professionally.
        Expand abbrevations if possible.
        Email:
        {email}
        """,
        expected_output = "A polished professional email.",
        agent=email_agent,
)

crew = Crew(
    agents = [email_agent],
    tasks = [task],
    verbose = True,
)

# result = crew.kickoff()
result = crew.kickoff(inputs={"email": email})

print(result)