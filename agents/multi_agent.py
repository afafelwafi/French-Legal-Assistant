# agents/multi_agent.py
from typing import List
from langchain.agents import initialize_agent, AgentType
from langchain.tools import Tool
from models.llm import GroqLLM
from utils.prompts import MULTI_AGENT_PROMPT


def create_multi_agent(tools: List[Tool], verbose: bool = False):
    """
    Create a multi-agent system with the given tools.

    Args:
        tools: List of tools to use
        verbose: Whether to enable verbose output

    Returns:
        Initialized agent
    """
    # Initialize LLM
    llm = GroqLLM()

    # Create agent
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.OPENAI_FUNCTIONS,  # Supports structured tool use
        verbose=verbose,
        agent_kwargs={"system_message": MULTI_AGENT_PROMPT},
    )

    return agent
