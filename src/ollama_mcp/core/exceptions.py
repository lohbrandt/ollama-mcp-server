"""Custom exception hierarchy for the Ollama MCP Server.

Exceptions defined here are meant to provide more context and control over error handling.
They are categorized to clearly define the type of error for more granified handling.
"""


class OllamaMCPError(Exception):
    """Base class for all Ollama MCP server exceptions."""
    pass


class OllamaConnectionError(OllamaMCPError):
    """Raised when there is a connection issue with Ollama server."""
    pass


class ModelNotFoundError(OllamaMCPError):
    """Raised when an expected model is not found."""
    pass


class DownloadError(OllamaMCPError):
    """Raised when a download operation fails."""
    pass


class ValidationError(OllamaMCPError):
    """Raised when there is a validation error in request or data."""
    pass
