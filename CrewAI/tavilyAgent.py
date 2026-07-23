import os
from crewai import Agent, Task, Crew, LLM
from crewai.tools import BaseTool
from crewai_tools import TavilySearchTool
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gemini/gemini-2.5-flash",
    temperature=0.9,
    api_key=os.getenv("API_KEY")
)

tavily_tool = TavilySearchTool(
    api_key=os.getenv("TAVILY_SEARCH_API")
)

researcher = Agent(
    role="Professional Researcher",
    goal="Research comprehensively about any topic using web search",
    backstory="""You are a professional researcher who uses the Tavily search tool 
                to find accurate and up-to-date information from the web. 
                You gather facts, statistics, and data from authoritative sources.""",
    tools=[tavily_tool],
    llm=llm,
    verbose=True,
    allow_delegation=False
)

research_task = Task(
    description="""
        Conduct comprehensive research on {topic} using the Tavily search tool.
    """,
    expected_output="""A comprehensive research report.""",
    agent=researcher,
    tools=[tavily_tool]
)

class temperatureTool(BaseTool):
    name:str="Delhi Temperature Tool"
    description:str="Returns a hardcoded value when asked about Delhi Temperature"

    def _run(self,text:str)->str:
        return "The current temperature in Delhi is 52°C."

temperature_tool = temperatureTool();

weather_agent = Agent(
    role="Weather Information Specialist",
    goal="Provide accurate weather information for Delhi",
    backstory="""weather specialist""",
    tools=[temperature_tool],
    llm=llm,
    verbose=True,
)

weather_task = Task(
    description="Provide the current temperature in Delhi using the Delhi Temperature Tool.",
    expected_output="A short statement with Delhi's current temperature.",
    agent=weather_agent,
    tools=[temperature_tool]
)

from crewai import Process

router_task = Task(
    description="""
        The user's topic is: {topic}.
        If this topic is about weather/temperature (especially Delhi's temperature),
        delegate to the Weather Information Specialist.
        Otherwise, delegate to the Professional Researcher to do comprehensive research.
    """,
    expected_output="A comprehensive answer appropriate to the topic.",
)

crew = Crew(
    agents=[researcher, weather_agent],
    tasks=[router_task],
    process=Process.hierarchical,
    manager_llm=llm,
    verbose=True
)

result = crew.kickoff(inputs={"topic": "Mobile Phone"})
print(result)