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

class JargonTool(BaseTool):
    name:str="Company Jargon Tool"
    description:str="Expands company abbreviations."

    def _run(self,text:str)->str:
        mapping={
            "TAS":"Technical Architecture Stack",
            "PRX": "Project Phoenix",
            "DAC": "Design Approval Commitee"
        }
        for k,v in mapping.items():
            text = text.replace(k,v)
        return text;

tool = JargonTool()

email = """
        hey team,
        the TAS is done and also the PRX. We are waiting for DAC.
        thank.        
    """

agent = Agent(
    role="Professional Email Writer",
    goal="Rewrite emails in a professional tone",
    backstory=(
        "You are an expert business communication specialist who writes clear, polite and professional emails."
    ),
    llm = llm,
    tools = [tool],
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
        agent=agent,
)

crew = Crew(
    agents = [agent],
    tasks = [task],
    verbose = True,
)

# result = crew.kickoff()
result = crew.kickoff(inputs={"email": email})

print(result)