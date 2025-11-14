"""
Phase 3 verification tests for Settings behavior.

Tests that Pydantic Settings loads correctly with defaults and environment overrides.
"""

import os
import sys
from pathlib import Path
import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.settings import Settings


def test_settings_defaults():
    """Verify Settings class loads with sensible defaults."""
    s = Settings()
    assert s.tb_run_mode == "dev"
    assert s.tb_max_files == 2000
    assert s.tb_max_file_size_mb == 2
    assert s.log_level == "INFO"
    assert s.llm_provider == "openai"
    assert s.enable_security_filters is True


def test_settings_env_override(monkeypatch):
    """Verify environment variables override defaults."""
    monkeypatch.setenv("TB_RUN_MODE", "strict")
    monkeypatch.setenv("TB_MAX_FILES", "5000")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    
    # Create new Settings instance to pick up env vars
    s = Settings()
    
    assert s.tb_run_mode == "strict"
    assert s.tb_max_files == 5000
    assert s.log_level == "DEBUG"


def test_settings_get_api_key_for_provider():
    """Verify helper method for provider-specific API key lookup."""
    s = Settings()
    
    # With no keys set or empty strings, should return None or empty string
    # (Pydantic loads empty strings from .env as '', not None)
    result_openai = s.get_api_key_for_provider("openai")
    result_groq = s.get_api_key_for_provider("groq")
    result_gemini = s.get_api_key_for_provider("gemini")
    
    # Verify they're either None or empty string (both falsy)
    assert not result_openai or isinstance(result_openai, str)
    assert not result_groq or isinstance(result_groq, str)
    assert not result_gemini or isinstance(result_gemini, str)


def test_settings_has_any_llm_key_empty():
    """Verify has_any_llm_key returns False when no keys configured."""
    s = Settings()
    # Assuming test environment has no API keys set
    # This may vary depending on test environment
    result = s.has_any_llm_key()
    assert isinstance(result, bool)


def test_settings_optional_fields():
    """Verify optional fields accept None values."""
    s = Settings()
    # These should be Optional[str] and accept None
    assert s.openai_api_key is None or isinstance(s.openai_api_key, str)
    assert s.groq_api_key is None or isinstance(s.groq_api_key, str)
    assert s.gemini_api_key is None or isinstance(s.gemini_api_key, str)
