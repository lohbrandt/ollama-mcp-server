"""Protocol interfaces for dependency injection and type safety.

These protocols define the interfaces that various components must implement,
enabling clean dependency injection and easier testing.
"""

from abc import abstractmethod
from typing import List, Optional, Protocol

from .models import (
    ModelInfo,
    HealthStatus,
    SystemResources,
    ChatRequest,
    ChatResponse,
    DownloadProgress,
    ModelRecommendation,
)


class OllamaClientProtocol(Protocol):
    """Protocol for Ollama client implementations."""
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """List available models."""
        ...
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send chat request to model."""
        ...
    
    @abstractmethod
    async def health_check(self) -> HealthStatus:
        """Check Ollama server health."""
        ...
    
    @abstractmethod
    async def pull_model(self, model_name: str) -> DownloadProgress:
        """Pull/download a model."""
        ...
    
    @abstractmethod
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model."""
        ...


class SystemMonitorProtocol(Protocol):
    """Protocol for system monitoring implementations."""
    
    @abstractmethod
    async def get_system_resources(self) -> SystemResources:
        """Get current system resource information."""
        ...
    
    @abstractmethod
    async def monitor_resources(self) -> None:
        """Start continuous resource monitoring."""
        ...
    
    @abstractmethod
    async def stop_monitoring(self) -> None:
        """Stop resource monitoring."""
        ...


class ModelServiceProtocol(Protocol):
    """Protocol for model management service."""
    
    @abstractmethod
    async def list_models(self) -> List[ModelInfo]:
        """Get list of available models."""
        ...
    
    @abstractmethod
    async def get_model(self, name: str) -> Optional[ModelInfo]:
        """Get specific model information."""
        ...
    
    @abstractmethod
    async def download_model(self, name: str) -> DownloadProgress:
        """Download a model."""
        ...
    
    @abstractmethod
    async def remove_model(self, name: str, force: bool = False) -> bool:
        """Remove a model."""
        ...
    
    @abstractmethod
    async def recommend_models(
        self, 
        user_needs: str, 
        priority: str = "balanced"
    ) -> List[ModelRecommendation]:
        """Get model recommendations based on user needs."""
        ...


class ChatServiceProtocol(Protocol):
    """Protocol for chat service implementations."""
    
    @abstractmethod
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Process a chat request."""
        ...
    
    @abstractmethod
    async def validate_model(self, model_name: str) -> bool:
        """Validate if a model is available for chat."""
        ...


class HealthServiceProtocol(Protocol):
    """Protocol for health checking service."""
    
    @abstractmethod
    async def check_health(self) -> HealthStatus:
        """Perform comprehensive health check."""
        ...
    
    @abstractmethod
    async def check_ollama_connection(self) -> bool:
        """Check if Ollama server is accessible."""
        ...
    
    @abstractmethod
    async def start_ollama_if_needed(self) -> bool:
        """Start Ollama server if it's not running."""
        ...


class DownloadServiceProtocol(Protocol):
    """Protocol for download management service."""
    
    @abstractmethod
    async def start_download(self, model_name: str) -> DownloadProgress:
        """Start a model download."""
        ...
    
    @abstractmethod
    async def get_download_status(self, job_id: str) -> Optional[DownloadProgress]:
        """Get download progress status."""
        ...
    
    @abstractmethod
    async def cancel_download(self, job_id: str) -> bool:
        """Cancel an active download."""
        ...
    
    @abstractmethod
    async def list_active_downloads(self) -> List[DownloadProgress]:
        """Get list of active downloads."""
        ...
