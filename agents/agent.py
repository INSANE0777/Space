import datetime
from zoneinfo import ZoneInfo
from google.adk.agents import Agent
from google.adk.agents import LlmAgent
from google.adk.tools.agent_tool import AgentTool
from .sub_agents.websearch import websearch_agent
from .sub_agents.weather import weather_agent

MODEL = "gemini-2.5-flash"  # Or your preferred Gemini model



root_agent = Agent(
    name="weather_time_agent",
    model="gemini-2.0-flash",
    description=(
        "Agent to search anything on web and get weather report."
    ),
    instruction=(
        "You are a helpful agent who can answer user questions about the time and weather in a city."
    ),
    tools=[ AgentTool(agent=websearch_agent),
           AgentTool(agent=weather_agent)],
)