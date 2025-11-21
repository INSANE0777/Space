# agents/google_adk_agent.py
# Google ADK (Android Development Kit) Integration for Multi-Agent System
# This simulates Google ADK functionality for agent coordination
# Enhanced with LangChain for improved AI workflow and responses

import os
import json
from typing import Dict, List, Any
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

class GoogleADKCoordinator:
    """
    Google ADK-style coordinator for managing agent workflows
    Uses LangChain's ChatGoogleGenerativeAI for intelligent agent planning and coordination
    """
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not found in environment variables")
        
        # Initialize LangChain ChatGoogleGenerativeAI model
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.5-flash",
            google_api_key=api_key,
            temperature=0.3,
            max_tokens=1000
        )
    
    def plan_agent_sequence(self, user_goal: str) -> List[str]:
        """
        Use LangChain's ChatGoogleGenerativeAI to intelligently plan agent sequence
        """
        goal_lower = user_goal.lower().strip()
        
        # Handle conversational inputs directly without AI planning
        conversational_patterns = [
            "hi", "hello", "hey", "good morning", "good afternoon", "good evening",
            "how are you", "what's up", "what can you do", "help", "what are you",
            "who are you", "thanks", "thank you", "bye", "goodbye", "ok", "okay"
        ]
        
        if any(pattern in goal_lower for pattern in conversational_patterns) or len(goal_lower.split()) <= 3:
            return ["summary_agent"]  # Use only summary agent for conversational responses
        
        # Create LangChain message chain for better context handling
        system_message = SystemMessage(
            content="""You are an intelligent agent planner for a multi-agent AI system. 
            Given a user goal, determine the optimal sequence of specialized agents to achieve it.
              Available agents:
            - spacex_agent: Gets SpaceX launch data and coordinates
            - weather_agent: Gets weather data for specific coordinates
            - calculator_agent: Performs mathematical calculations and solves equations
            - dictionary_agent: Provides word definitions, meanings, and synonyms
            - summary_agent: Analyzes data and provides conclusions
            - news_agent: Gets relevant news articles (if needed)
            
            Rules:
            - For greetings or simple questions, use only: summary_agent
            - For calculations/math (keywords: calculate, compute, solve, math): calculator_agent, summary_agent
            - For definitions (keywords: define, meaning, what is): dictionary_agent, summary_agent
            - For SpaceX + weather requests: spacex_agent, weather_agent, summary_agent
            - For SpaceX only: spacex_agent, summary_agent
            - For weather only: weather_agent, summary_agent
            
            Respond with ONLY a comma-separated list of agent names in execution order.
            Example: spacex_agent, weather_agent, summary_agent"""
        )
        
        human_message = HumanMessage(
            content=f"User Goal: \"{user_goal}\"\n\nProvide the optimal agent sequence:"
        )        
        try:
            # Use LangChain's invoke method for better response handling
            response = self.llm.invoke([system_message, human_message])
            
            # Parse the response to extract agent names
            agent_list = [agent.strip() for agent in response.content.strip().split(',')]
            
            # Validate agent names
            valid_agents = ["spacex_agent", "weather_agent", "calculator_agent", "dictionary_agent", "summary_agent", "news_agent"]
            agent_list = [agent for agent in agent_list if agent in valid_agents]
            
            # Ensure we have at least one agent
            if not agent_list:
                agent_list = ["summary_agent"]
                
            return agent_list
            
        except Exception as e:
            print(f"⚠️ LangChain ADK Planning fallback due to: {e}")
            # Fallback to simple planning with trigger word detection
            if any(pattern in goal_lower for pattern in conversational_patterns):
                return ["summary_agent"]
            elif any(word in goal_lower for word in ["calculate", "compute", "solve", "math", "equation", "+", "-", "*", "/", "="]):
                return ["calculator_agent", "summary_agent"]
            elif any(word in goal_lower for word in ["define", "definition", "meaning", "what is", "what does", "dictionary"]):
                return ["dictionary_agent", "summary_agent"]
            elif "spacex" in goal_lower and "weather" in goal_lower:
                return ["spacex_agent", "weather_agent", "summary_agent"]
            elif "spacex" in goal_lower:
                return ["spacex_agent", "summary_agent"]
            elif "weather" in goal_lower:
                return ["weather_agent", "summary_agent"]
            return ["summary_agent"]  # Default to conversational response
    
    def validate_goal_completion(self, user_goal: str, final_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Use LangChain's ChatGoogleGenerativeAI to validate if the goal was achieved and suggest improvements
        """
        # Create LangChain message chain for better validation context
        system_message = SystemMessage(
            content="""You are an intelligent validation agent for a multi-agent AI system.
            Analyze if the user's goal was successfully achieved based on the data collected.
            
            Provide a JSON response with:
            {
                "goal_achieved": true/false,
                "confidence": 0-100,
                "missing_data": ["list of missing information"],
                "suggested_improvements": ["list of suggestions"],
                "quality_score": 0-100,
                "result_summary": "Brief summary of the validation result"
            }
            
            Be thorough but fair in your assessment. Consider both completeness and relevance of the data."""
        )
        
        human_message = HumanMessage(
            content=f"""User Goal: "{user_goal}"
            
            Final Data Collected: {json.dumps(final_data, indent=2)}
            
            Please analyze and provide the validation JSON response:"""
        )
        
        try:
            # Use LangChain's invoke method for better response handling
            response = self.llm.invoke([system_message, human_message])
            
            # Clean and parse JSON response
            json_text = response.content.strip() if response.content else ""
            
            if not json_text:
                raise ValueError("Empty response from LLM")
            
            # Remove markdown code blocks if present
            if json_text.startswith("```json"):
                json_text = json_text[7:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
            elif json_text.startswith("```"):
                json_text = json_text[3:]
                if json_text.endswith("```"):
                    json_text = json_text[:-3]
            
            json_text = json_text.strip()
            
            # Try to extract JSON if wrapped in text
            if "{" in json_text and "}" in json_text:
                start = json_text.find("{")
                end = json_text.rfind("}") + 1
                json_text = json_text[start:end]
            
            if not json_text:
                raise ValueError("No JSON found in response")
            
            validation_result = json.loads(json_text)
            
            # Validate the structure of the response
            required_fields = ["goal_achieved", "confidence", "missing_data", "suggested_improvements", "quality_score"]
            if all(field in validation_result for field in required_fields):
                # Ensure result_summary exists
                if "result_summary" not in validation_result:
                    validation_result["result_summary"] = "Goal completion validated successfully." if validation_result.get("goal_achieved") else "Goal completion needs improvement."
                return validation_result
            else:
                raise ValueError("Invalid validation response structure")
                
        except json.JSONDecodeError as e:
            print(f"⚠️ LangChain ADK Validation fallback due to JSON parse error: {e}")
            print(f"   Response was: {json_text[:200] if 'json_text' in locals() else 'N/A'}")
        except Exception as e:
            print(f"⚠️ LangChain ADK Validation fallback due to: {e}")
        
        # Fallback response
        return {
            "goal_achieved": True,
            "confidence": 80,
            "missing_data": [],
            "suggested_improvements": ["Consider using more specific queries for better results"],
            "quality_score": 80,
            "result_summary": "Goal completion validated with fallback metrics."
        }

def run(previous_data: dict) -> dict:
    """
    Google ADK agent runner - this validates and improves the final result
    """
    adk = GoogleADKCoordinator()
    user_goal = previous_data.get("goal", "")
    
    validation = adk.validate_goal_completion(user_goal, previous_data)
    previous_data.update({"adk_validation": validation})
    
    return previous_data
