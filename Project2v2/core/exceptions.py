"""
Custom exception types for Trust Bench SecureEval + Ops.

This module defines typed exceptions that provide clear, structured error handling
throughout the application. Each exception type represents a specific failure mode
that can be handled gracefully with appropriate user feedback and logging.
"""


class ConfigurationError(Exception):
    """
    Raised when the system is misconfigured or missing required settings.
    
    Examples:
        - Missing API keys when LLM features are required
        - Invalid repository URL format
        - Missing required environment variables
        - Invalid configuration values (e.g., negative timeouts)
    
    This exception should be caught at application entry points to provide
    user-friendly configuration guidance rather than cryptic stack traces.
    """
    pass


class ProviderError(Exception):
    """
    Raised when an external service provider fails or becomes unavailable.
    
    Examples:
        - LLM provider API failures (OpenAI, Groq, Gemini)
        - Network timeouts or connection errors
        - Invalid API responses or rate limiting
        - Provider authentication failures
    
    This exception indicates the system is properly configured but external
    dependencies are failing. Handlers should suggest fallback options or
    retry strategies.
    """
    pass


class AgentExecutionError(Exception):
    """
    Raised when an agent encounters an unexpected runtime problem.
    
    Examples:
        - Tool execution failures within an agent
        - Unexpected data format from tool results
        - Agent-specific logic errors
        - Resource exhaustion during agent execution
    
    This exception should include context about which agent failed, which tool
    was being executed, and the underlying cause. It helps maintain the chain
    of causality for debugging while providing clean error boundaries.
    """
    pass
