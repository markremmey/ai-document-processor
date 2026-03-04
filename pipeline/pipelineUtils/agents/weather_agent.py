"""
Weather Agent Tool

A sample agent tool that demonstrates how to create a simple tool.
This tool returns mock weather data for any location.

Usage:
    from pipelineUtils.agents import get_weather
    
    # Pass get_weather as a tool to the agent
    agent = client.as_agent(instructions=..., tools=get_weather)

To create a new agent tool:
1. Create a new file in pipelineUtils/agents/
2. Define your tool function with Annotated parameters using pydantic Field
3. Export it in pipelineUtils/agents/__init__.py
4. Import and use in callAiFoundryAgentic.py
"""

from typing import Annotated
from pydantic import Field


def get_weather(
    location: Annotated[str, Field(description="The city or location to get weather for (e.g., 'Seattle, WA')")]
) -> str:
    """
    Gets the current weather for a specified location.
    This is a sample tool that returns mock weather data.
    
    In a real implementation, this would call a weather API.
    """
    # Mock weather response - replace with actual API call for production
    return f"The weather in {location} is currently 72°F (22°C) and sunny with light winds."
