# models/llm.py
from langchain.llms.base import LLM
from typing import Optional, List, Mapping, Any
from groq import Groq
import os
from config import (
    GROQ_API_KEY,
    DEFAULT_MODEL,
    DEFAULT_TEMPERATURE,
    DEFAULT_MAX_TOKENS,
)


class GroqLLM(LLM):
    """Custom LLM wrapper for Groq API."""

    model: str = DEFAULT_MODEL
    temperature: float = DEFAULT_TEMPERATURE
    max_tokens: int = DEFAULT_MAX_TOKENS
    api_key: Optional[str] = None

    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        """
        Call the Groq API with the given prompt.

        Args:
            prompt: The prompt to send to the API
            stop: Optional list of stop sequences

        Returns:
            The response from the API
        """
        client = Groq(api_key=self.api_key or GROQ_API_KEY)
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model=self.model,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return chat_completion.choices[0].message.content

    @property
    def _llm_type(self) -> str:
        """Return the type of LLM."""
        return "groq-llm"
