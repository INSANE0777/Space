"""
Shared utilities for agent management and Gemini API interactions.
This module is separate to avoid circular imports.
"""

import os
from dotenv import load_dotenv
from agents import (
    get_spacex_agent,
    get_weather_agent,
    get_summary_agent,
    get_calculator_agent,
    get_dictionary_agent,
    get_news_agent,
    get_satellite_data_agent,
    get_anomalies_detection_agent,
)

try:
    from langchain_google_genai import ChatGoogleGenerativeAI
    from langchain_core.messages import HumanMessage, SystemMessage
    LANGCHAIN_AVAILABLE = True
except ImportError:
    LANGCHAIN_AVAILABLE = False
    ChatGoogleGenerativeAI = None
    HumanMessage = None
    SystemMessage = None

load_dotenv()

# Map agent names to lazy getters
AGENT_GETTERS = {
    "spacex_agent": get_spacex_agent,
    "weather_agent": get_weather_agent,
    "summary_agent": get_summary_agent,
    "calculator_agent": get_calculator_agent,
    "dictionary_agent": get_dictionary_agent,
    "news_agent": get_news_agent,
    "satellite_data_agent": get_satellite_data_agent,
    "anomalies_detection_agent": get_anomalies_detection_agent,
}


def load_agent(name: str):
    """Load an agent by name."""
    getter = AGENT_GETTERS.get(name)
    if not getter:
        raise ValueError(f"Unknown agent: {name}")
    return getter()


def get_gemini_response(user_message: str, system_prompt: str, temperature: float = 0.7, max_tokens: int = 2000) -> str:
    """Get a response from Gemini API with improved error handling."""
    if not LANGCHAIN_AVAILABLE:
        print("Warning: langchain_google_genai not available. Cannot use Gemini API.")
        return None
    
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            print("Warning: GOOGLE_API_KEY not found in environment variables.")
            return None

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=temperature,
            max_tokens=max_tokens
        )

        system_message = SystemMessage(content=system_prompt)
        human_message = HumanMessage(content=user_message)
        
        # Truncate message if too long (Gemini has token limits)
        max_message_length = 15000  # Approximate character limit
        if len(user_message) > max_message_length:
            user_message = user_message[:max_message_length] + "\n\n[Content truncated due to length...]"
            human_message = HumanMessage(content=user_message)
        
        response = llm.invoke([system_message, human_message])
        
        if response and hasattr(response, 'content'):
            return response.content
        else:
            print("Warning: Gemini API returned empty or invalid response.")
            return None
    except Exception as e:
        print(f"Warning: Gemini API error: {e}")
        return None

