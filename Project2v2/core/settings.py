"""
Centralized configuration management for Trust Bench SecureEval + Ops.

This module uses Pydantic Settings to load and validate all configuration
from environment variables and .env files. It provides type-safe access to
configuration values throughout the application.

Usage:
    from core.settings import settings
    
    if settings.openai_api_key:
        # Use OpenAI provider
        pass
"""

import os
from typing import Optional
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables and .env file.
    
    All configuration values are centralized here to provide:
    - Type safety and validation
    - Clear defaults
    - Single source of truth for configuration
    - Easy testing with override values
    """
    
    # LLM Provider Configuration
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key for chat features (recommended provider)"
    )
    groq_api_key: Optional[str] = Field(
        default=None,
        description="Groq API key (alternative LLM provider)"
    )
    gemini_api_key: Optional[str] = Field(
        default=None,
        description="Google Gemini API key (alternative LLM provider)"
    )
    llm_provider: str = Field(
        default="openai",
        description="Which LLM provider to use: openai, groq, or gemini"
    )
    
    # Security & Safety
    enable_security_filters: bool = Field(
        default=True,
        description="Enable input validation and prompt sanitization"
    )
    
    # Repository Analysis Limits
    tb_max_files: int = Field(
        default=2000,
        description="Maximum number of files to scan per repository"
    )
    tb_max_file_size_mb: int = Field(
        default=2,
        description="Skip files larger than this size in megabytes"
    )
    tb_clone_timeout: int = Field(
        default=120,
        description="Repository clone timeout in seconds"
    )
    
    # Runtime Configuration
    tb_run_mode: str = Field(
        default="dev",
        description="Runtime mode: dev (permissive) or strict (production)"
    )
    web_port: int = Field(
        default=5001,
        description="Port for Flask web interface"
    )
    flask_debug: bool = Field(
        default=False,
        description="Enable Flask debug mode (development only)"
    )
    
    # Resilience & Reliability
    max_retry_attempts: int = Field(
        default=3,
        description="Maximum retry attempts for failed operations"
    )
    retry_backoff_seconds: float = Field(
        default=0.5,
        description="Initial delay between retry attempts (exponential backoff)"
    )
    agent_timeout_seconds: int = Field(
        default=120,
        description="Timeout for individual agent execution"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        description="Logging verbosity: DEBUG, INFO, WARNING, ERROR"
    )
    log_format: str = Field(
        default="json",
        description="Log output format: json or text"
    )
    
    class Config:
        """Pydantic configuration for Settings class."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False  # Allow case-insensitive env var names
        extra = "ignore"  # Ignore extra env vars not defined in Settings
    
    def get_api_key_for_provider(self, provider: Optional[str] = None) -> Optional[str]:
        """
        Get the API key for the specified or configured LLM provider.
        
        Args:
            provider: LLM provider name (openai, groq, gemini). 
                     If None, uses llm_provider setting.
        
        Returns:
            API key string if available, None otherwise.
        """
        target_provider = (provider or self.llm_provider).lower()
        
        if target_provider == "openai":
            return self.openai_api_key
        elif target_provider == "groq":
            return self.groq_api_key
        elif target_provider == "gemini":
            return self.gemini_api_key
        else:
            return None
    
    def has_any_llm_key(self) -> bool:
        """Check if at least one LLM provider API key is configured."""
        return any([
            self.openai_api_key,
            self.groq_api_key,
            self.gemini_api_key
        ])


# Global settings instance
# Import this in other modules: from core.settings import settings
settings = Settings()
