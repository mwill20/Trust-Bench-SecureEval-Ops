"""
Phase 3 verification tests for error handling behavior.

Tests that ConfigurationError, ProviderError, and AgentExecutionError
are raised correctly and propagate through the system.
"""

import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.exceptions import ConfigurationError, ProviderError, AgentExecutionError


def test_configuration_error_basic():
    """Verify ConfigurationError can be raised and caught."""
    with pytest.raises(ConfigurationError) as exc_info:
        raise ConfigurationError("Missing API key")
    
    assert "Missing API key" in str(exc_info.value)


def test_provider_error_basic():
    """Verify ProviderError can be raised and caught."""
    with pytest.raises(ProviderError) as exc_info:
        raise ProviderError("OpenAI API quota exceeded")
    
    assert "OpenAI API quota exceeded" in str(exc_info.value)


def test_agent_execution_error_basic():
    """Verify AgentExecutionError can be raised and caught."""
    with pytest.raises(AgentExecutionError) as exc_info:
        raise AgentExecutionError("SecurityAgent failed during secret scan")
    
    assert "SecurityAgent failed" in str(exc_info.value)


def test_agent_execution_error_with_context():
    """Verify AgentExecutionError preserves error context from underlying exceptions."""
    original_error = RuntimeError("Tool crashed unexpectedly")
    
    with pytest.raises(AgentExecutionError) as exc_info:
        try:
            raise original_error
        except RuntimeError as e:
            raise AgentExecutionError(f"Agent failed: {e}") from e
    
    assert "Agent failed" in str(exc_info.value)
    assert exc_info.value.__cause__ is original_error


def test_exception_inheritance():
    """Verify custom exceptions inherit from appropriate base classes."""
    assert issubclass(ConfigurationError, Exception)
    assert issubclass(ProviderError, Exception)
    assert issubclass(AgentExecutionError, Exception)


def test_exception_messages():
    """Verify custom exceptions preserve detailed error messages."""
    config_err = ConfigurationError("Missing required setting: OPENAI_API_KEY")
    assert "OPENAI_API_KEY" in str(config_err)
    
    provider_err = ProviderError("Rate limit exceeded for provider: groq")
    assert "Rate limit" in str(provider_err)
    assert "groq" in str(provider_err)
    
    agent_err = AgentExecutionError("QualityAgent failed during structure analysis: FileNotFoundError")
    assert "QualityAgent" in str(agent_err)
    assert "structure analysis" in str(agent_err)
