"""Configuration module for the food ordering agent."""
from .settings import settings
from .prompts import AGENT_SYSTEM_PROMPT, MEAL_SUGGESTION_PROMPT

__all__ = ['settings', 'AGENT_SYSTEM_PROMPT', 'MEAL_SUGGESTION_PROMPT']
