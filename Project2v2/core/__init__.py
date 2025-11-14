"""
Core module for Trust Bench SecureEval + Ops.

This module contains foundational components used throughout the application:
- Custom exception types for structured error handling
- Centralized configuration management with Pydantic Settings
- Shared utilities and constants
"""

from .exceptions import (
    ConfigurationError,
    ProviderError,
    AgentExecutionError,
)
from .settings import settings, Settings

__all__ = [
    "ConfigurationError",
    "ProviderError",
    "AgentExecutionError",
    "settings",
    "Settings",
]
