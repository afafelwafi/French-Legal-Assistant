import pytest
from unittest.mock import MagicMock, patch
from langchain.tools import Tool
from agents.multi_agent import create_multi_agent


@pytest.fixture
def mock_groq_llm():
    with patch("agents.multi_agent.GroqLLM") as mock_llm:
        mock_llm_instance = MagicMock()
        mock_llm.return_value = mock_llm_instance
        yield mock_llm_instance


@pytest.fixture
def mock_initialize_agent():
    with patch("agents.multi_agent.initialize_agent") as mock_init:
        mock_agent = MagicMock()
        mock_init.return_value = mock_agent
        yield mock_init


@pytest.fixture
def sample_tools():
    tool1 = Tool(name="tool1", func=lambda x: x, description="Test tool 1")
    tool2 = Tool(name="tool2", func=lambda x: x, description="Test tool 2")
    return [tool1, tool2]


def test_create_multi_agent(mock_groq_llm, mock_initialize_agent, sample_tools):
    # Act
    result = create_multi_agent(sample_tools, verbose=True)

    # Assert
    from agents.multi_agent import AgentType, MULTI_AGENT_PROMPT

    # Check that initialize_agent was called with the right arguments
    mock_initialize_agent.assert_called_once()
    args, kwargs = mock_initialize_agent.call_args

    assert args[0] == sample_tools  # First arg should be tools
    assert args[1] == mock_groq_llm  # Second arg should be LLM
    assert kwargs["agent"] == AgentType.OPENAI_FUNCTIONS
    assert kwargs["verbose"] == True
    assert kwargs["agent_kwargs"]["system_message"] == MULTI_AGENT_PROMPT


def test_create_multi_agent_default_verbose(
    mock_groq_llm, mock_initialize_agent, sample_tools
):
    # Act
    result = create_multi_agent(sample_tools)  # Default verbose=False

    # Assert
    args, kwargs = mock_initialize_agent.call_args
    assert kwargs["verbose"] == False
