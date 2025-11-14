#!/usr/bin/env python3
"""
Integration tests for Phase 3 code quality improvements.
Tests exception handling, settings behavior, and agent error wrapping.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

import pytest
from core.exceptions import ConfigurationError, ProviderError, AgentExecutionError
from core.settings import Settings


class TestSettings:
    """Test Pydantic Settings behavior."""
    
    def test_settings_defaults(self):
        """Verify default values are sensible."""
        s = Settings()
        assert s.tb_run_mode in ("dev", "strict")
        assert s.tb_max_files > 0
        assert s.tb_max_file_size_mb > 0
        assert s.tb_clone_timeout > 0
        assert s.log_level in ("DEBUG", "INFO", "WARNING", "ERROR")
    
    def test_settings_environment_override(self, monkeypatch):
        """Verify environment variables override defaults."""
        monkeypatch.setenv("TB_MAX_FILES", "5000")
        monkeypatch.setenv("LOG_LEVEL", "DEBUG")
        
        s = Settings()
        assert s.tb_max_files == 5000
        assert s.log_level == "DEBUG"
    
    def test_settings_optional_fields(self):
        """Verify optional fields can be None or empty."""
        s = Settings()
        # API keys are optional (may be None or empty string)
        assert s.openai_api_key is None or isinstance(s.openai_api_key, str)


class TestExceptionTypes:
    """Test custom exception types are properly defined."""
    
    def test_configuration_error_basic(self):
        """ConfigurationError can be raised and caught."""
        with pytest.raises(ConfigurationError) as exc_info:
            raise ConfigurationError("Missing required API key")
        
        assert "Missing required API key" in str(exc_info.value)
    
    def test_provider_error_basic(self):
        """ProviderError can be raised and caught."""
        with pytest.raises(ProviderError) as exc_info:
            raise ProviderError("OpenAI API returned 401: Invalid API key")
        
        assert "401" in str(exc_info.value)
    
    def test_agent_execution_error_basic(self):
        """AgentExecutionError can be raised and caught."""
        with pytest.raises(AgentExecutionError) as exc_info:
            raise AgentExecutionError("SecurityAgent failed: tool returned None")
        
        assert "SecurityAgent" in str(exc_info.value)
    
    def test_agent_execution_error_with_context(self):
        """AgentExecutionError preserves exception context."""
        try:
            try:
                raise RuntimeError("Database connection failed")
            except RuntimeError as e:
                raise AgentExecutionError("Agent crashed during analysis") from e
        except AgentExecutionError as e:
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, RuntimeError)
            assert "Database connection failed" in str(e.__cause__)


class TestErrorMessages:
    """Test that errors produce clean, helpful messages."""
    
    def test_exception_messages_are_descriptive(self):
        """Exception messages should be clear and actionable."""
        try:
            raise ConfigurationError("Missing OPENAI_API_KEY in environment")
        except ConfigurationError as e:
            msg = str(e)
            assert len(msg) > 10  # Not empty
            assert "OPENAI_API_KEY" in msg  # Specific detail
            assert msg[0].isupper()  # Proper capitalization
    
    def test_provider_error_includes_status_codes(self):
        """ProviderError should include HTTP status when available."""
        try:
            raise ProviderError("OpenAI API request failed (401): Invalid API key")
        except ProviderError as e:
            msg = str(e)
            assert "401" in msg  # HTTP status code
            assert "API" in msg or "api" in msg.lower()  # Service context
    
    def test_agent_error_includes_context(self):
        """AgentExecutionError should identify which agent failed."""
        try:
            raise AgentExecutionError("SecurityAgent failed during secret scan")
        except AgentExecutionError as e:
            msg = str(e)
            assert "Agent" in msg  # Identifies error category
            assert len(msg) > 20  # Has meaningful detail


if __name__ == "__main__":
    # Allow running directly for quick testing
    pytest.main([__file__, "-v"])
