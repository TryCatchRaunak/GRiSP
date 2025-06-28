import os
import yaml
from crewai import Agent, Task, Crew, LLM
from tools.climate_api_tool import ClimateApiTool
from tools.global_terrorism_database_scraper import GlobalTerrorismDatabaseTool
from tools.google_search_tool import GoogleSearchTool
from tools.twitter_sentiment_tool import TwitterSentimentTool
from tools.world_bank_api import WorldBankApiTool
from tools.news_api_tool import NewsApiTool
from dotenv import load_dotenv

load_dotenv()

llm = LLM(
    model="gemini/gemini-2.5-flash-preview-04-17",
    api_key=os.getenv("GEMINI_API_KEY"),
    temperature=0.3,
    stream=True,
    reasoning_effort="high"
)

# Tool map
TOOL_MAP = {
    "ClimateApiTool": ClimateApiTool(),
    "GlobalTerrorismDatabaseTool": GlobalTerrorismDatabaseTool(),
    "GoogleSearchTool": GoogleSearchTool(),
    "TwitterSentimentTool": TwitterSentimentTool(),
    "WorldBankApiTool": WorldBankApiTool(),
    "NewsApiTool": NewsApiTool()
}

# Load Agents and map by name
agent_map = {}

def load_agents(folder="agents"):
    agents = []
    for file in os.listdir(folder):
        if file.endswith(".yaml"):
            with open(os.path.join(folder, file), "r") as f:
                data = yaml.safe_load(f)
                tools = [TOOL_MAP[t] for t in data.get("tools", [])]
                agent = Agent(
                    name=data["name"],
                    role=data["role"],
                    goal=data["goal"],
                    backstory=data["backstory"],
                    tools=tools,
                    memory=True,
                    verbose=True
                )
                agents.append(agent)
                agent_map[data["name"]] = agent
    return agents

def load_tasks(folder="tasks"):
    tasks = []
    for file in os.listdir(folder):
        if file.endswith(".yaml"):
            with open(os.path.join(folder, file), "r") as f:
                data = yaml.safe_load(f)
                agent_name = data["agent"]
                task = Task(
                    description=data["description"],
                    agent=agent_map.get(agent_name),
                    expected_output=data["expected_output"],
                    tools=[TOOL_MAP[t] for t in data.get("tools", [])],
                    verbose=True
                )
                tasks.append(task)
    return tasks

# Load agents and tasks
agents = load_agents("agents")
tasks = load_tasks("tasks")

# Create Crew
def callCrew():
    crew = Crew(
        agents=agents,
        tasks=tasks,
        memory=True,
        memory_path="memory/shared_memory.json",
        output_file="reports/final_report.md",
        verbose=True,
        llm=llm
    )

    return crew