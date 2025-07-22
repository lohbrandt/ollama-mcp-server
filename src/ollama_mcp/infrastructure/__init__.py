"""Infrastructure layer for external integrations and system interactions."""

from .ollama_client import OllamaClient

__all__ = [
    "OllamaClient",
]
