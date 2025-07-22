"""Core domain models and business logic."""

from .models import (
    ModelInfo,
    SystemResources,
    HealthStatus,
    DownloadProgress,
    ChatRequest,
    ChatResponse,
    GPUInfo,
)
from .exceptions import (
    OllamaMCPError,
    OllamaConnectionError,
    ModelNotFoundError,
    DownloadError,
    ValidationError,
)
from .protocols import (
    OllamaClientProtocol,
    SystemMonitorProtocol,
    ModelServiceProtocol,
)

__all__ = [
    # Models
    "ModelInfo",
    "SystemResources", 
    "HealthStatus",
    "DownloadProgress",
    "ChatRequest",
    "ChatResponse",
    "GPUInfo",
    # Exceptions
    "OllamaMCPError",
    "OllamaConnectionError",
    "ModelNotFoundError",
    "DownloadError",
    "ValidationError",
    # Protocols
    "OllamaClientProtocol",
    "SystemMonitorProtocol",
    "ModelServiceProtocol",
]
