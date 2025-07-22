"""Async Ollama client with connection pooling and robust error handling.

This module provides a high-performance async HTTP client for Ollama API
with comprehensive error handling, connection pooling, and retry logic.
"""

import asyncio
import json
import logging
import time
from datetime import datetime
from typing import Dict, List, Optional, Any, AsyncGenerator
from contextlib import asynccontextmanager

import httpx
from pydantic import ValidationError

from ..core.models import (
    ModelInfo,
    ModelSize,
    HealthStatus,
    ChatRequest,
    ChatResponse,
    DownloadProgress,
    DownloadStatus,
)
from ..core.exceptions import (
    OllamaConnectionError,
    ModelNotFoundError,
    ValidationError as CustomValidationError,
)
from ..config import get_settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """High-performance async Ollama client with connection pooling."""
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        timeout: Optional[float] = None,
        max_connections: Optional[int] = None,
    ) -> None:
        """Initialize Ollama client.
        
        Args:
            base_url: Ollama server URL (defaults to settings)
            timeout: Request timeout (defaults to settings)
            max_connections: Max HTTP connections (defaults to settings)
        """
        self.settings = get_settings()
        
        self.base_url = base_url or self.settings.ollama_url
        self.timeout = timeout or self.settings.ollama_timeout
        self.max_connections = max_connections or self.settings.connection_pool_size
        
        # HTTP client with connection pooling
        self._http_client: Optional[httpx.AsyncClient] = None
        self._client_lock = asyncio.Lock()
        
        logger.info(
            f"Initialized OllamaClient for {self.base_url} "
            f"(timeout={self.timeout}s, pool={self.max_connections})"
        )
    
    async def __aenter__(self) -> "OllamaClient":
        """Async context manager entry."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_client(self) -> httpx.AsyncClient:
        """Ensure HTTP client is initialized."""
        if self._http_client is None or self._http_client.is_closed:
            async with self._client_lock:
                if self._http_client is None or self._http_client.is_closed:
                    # Create HTTP client with optimized settings
                    limits = httpx.Limits(
                        max_keepalive_connections=self.max_connections,
                        max_connections=self.max_connections,
                        keepalive_expiry=30.0,
                    )
                    
                    self._http_client = httpx.AsyncClient(
                        base_url=self.base_url,
                        timeout=httpx.Timeout(self.timeout),
                        limits=limits,
                        headers={"Content-Type": "application/json"},
                        http2=True,  # Enable HTTP/2 if available
                    )
        
        return self._http_client
    
    async def close(self) -> None:
        """Close HTTP client and cleanup resources."""
        if self._http_client and not self._http_client.is_closed:
            await self._http_client.aclose()
            self._http_client = None
            logger.debug("Closed Ollama HTTP client")
    
    async def health_check(self) -> HealthStatus:
        """Perform comprehensive health check.
        
        Returns:
            HealthStatus object with server health information
            
        Raises:
            OllamaConnectionError: If connection fails
        """
        start_time = time.time()
        
        try:
            client = await self._ensure_client()
            response = await client.get("/api/tags")
            
            response_time_ms = (time.time() - start_time) * 1000
            
            if response.status_code == 200:
                try:
                    data = response.json()
                    models_count = len(data.get("models", []))
                    
                    return HealthStatus(
                        healthy=True,
                        host=self.base_url,
                        models_count=models_count,
                        response_time_ms=response_time_ms,
                        last_checked=datetime.now(),
                    )
                except json.JSONDecodeError as e:
                    logger.warning(f"Invalid JSON response from health check: {e}")
                    return HealthStatus(
                        healthy=False,
                        host=self.base_url,
                        error="Invalid JSON response from server",
                        response_time_ms=response_time_ms,
                        last_checked=datetime.now(),
                    )
            else:
                return HealthStatus(
                    healthy=False,
                    host=self.base_url,
                    error=f"Server returned status {response.status_code}",
                    response_time_ms=response_time_ms,
                    last_checked=datetime.now(),
                )
                
        except httpx.ConnectError as e:
            logger.error(f"Connection error during health check: {e}")
            return HealthStatus(
                healthy=False,
                host=self.base_url,
                error=f"Connection failed: {str(e)}",
                last_checked=datetime.now(),
            )
        except httpx.TimeoutException as e:
            response_time_ms = (time.time() - start_time) * 1000
            logger.error(f"Timeout during health check: {e}")
            return HealthStatus(
                healthy=False,
                host=self.base_url,
                error=f"Request timeout after {self.timeout}s",
                response_time_ms=response_time_ms,
                last_checked=datetime.now(),
            )
        except Exception as e:
            logger.error(f"Unexpected error during health check: {e}")
            return HealthStatus(
                healthy=False,
                host=self.base_url,
                error=f"Unexpected error: {str(e)}",
                last_checked=datetime.now(),
            )
    
    async def list_models(self) -> List[ModelInfo]:
        """List all available models.
        
        Returns:
            List of ModelInfo objects
            
        Raises:
            OllamaConnectionError: If connection fails
            ValidationError: If response format is invalid
        """
        try:
            client = await self._ensure_client()
            response = await client.get("/api/tags")
            
            if response.status_code != 200:
                raise OllamaConnectionError(
                    f"Failed to list models: HTTP {response.status_code}"
                )
            
            data = response.json()
            models_data = data.get("models", [])
            
            models = []
            for model_data in models_data:
                try:
                    # Convert Ollama response to our domain model
                    model = ModelInfo(
                        name=model_data["name"],
                        size=ModelSize(bytes=model_data["size"]),
                        digest=model_data.get("digest"),
                        modified=datetime.fromisoformat(
                            model_data["modified_at"].replace("Z", "+00:00")
                        ),
                        families=model_data.get("details", {}).get("families", []),
                        format=model_data.get("details", {}).get("format"),
                        parameter_size=model_data.get("details", {}).get("parameter_size"),
                        quantization_level=model_data.get("details", {}).get("quantization_level"),
                    )
                    models.append(model)
                except (KeyError, ValueError, ValidationError) as e:
                    logger.warning(f"Skipping invalid model data: {e}")
                    continue
            
            logger.debug(f"Listed {len(models)} models")
            return models
            
        except httpx.RequestError as e:
            logger.error(f"Network error listing models: {e}")
            raise OllamaConnectionError(f"Network error: {str(e)}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise CustomValidationError(f"Invalid JSON response: {str(e)}") from e
        except Exception as e:
            logger.error(f"Unexpected error listing models: {e}")
            raise OllamaConnectionError(f"Unexpected error: {str(e)}") from e
    
    async def get_model_info(self, model_name: str) -> Optional[ModelInfo]:
        """Get information for a specific model.
        
        Args:
            model_name: Name of the model
            
        Returns:
            ModelInfo object if found, None otherwise
            
        Raises:
            OllamaConnectionError: If connection fails
        """
        try:
            models = await self.list_models()
            for model in models:
                if model.name == model_name:
                    return model
            return None
        except Exception as e:
            logger.error(f"Error getting model info for {model_name}: {e}")
            raise
    
    async def chat(self, request: ChatRequest) -> ChatResponse:
        """Send chat request to model.
        
        Args:
            request: Chat request object
            
        Returns:
            ChatResponse object with generated response
            
        Raises:
            OllamaConnectionError: If connection fails
            ModelNotFoundError: If model is not available
            ValidationError: If request is invalid
        """
        # Validate model is allowed
        if not self.settings.is_model_allowed(request.model):
            raise CustomValidationError(f"Model '{request.model}' is not allowed")
        
        try:
            client = await self._ensure_client()
            
            # Prepare request payload
            payload = {
                "model": request.model,
                "prompt": request.message,
                "stream": request.stream,
                "options": {
                    "temperature": request.temperature,
                }
            }
            
            if request.max_tokens:
                payload["options"]["num_predict"] = request.max_tokens
            
            response = await client.post("/api/generate", json=payload)
            
            if response.status_code == 404:
                raise ModelNotFoundError(f"Model '{request.model}' not found")
            elif response.status_code != 200:
                error_text = response.text
                raise OllamaConnectionError(
                    f"Chat request failed: HTTP {response.status_code} - {error_text}"
                )
            
            data = response.json()
            
            # Convert response to our domain model
            chat_response = ChatResponse(
                response=data["response"],
                model=request.model,
                total_duration_ms=data.get("total_duration", 0) / 1_000_000,  # Convert from ns
                load_duration_ms=data.get("load_duration", 0) / 1_000_000,
                prompt_eval_count=data.get("prompt_eval_count"),
                prompt_eval_duration_ms=data.get("prompt_eval_duration", 0) / 1_000_000,
                eval_count=data.get("eval_count"),
                eval_duration_ms=data.get("eval_duration", 0) / 1_000_000,
                context_length=data.get("context", []) and len(data["context"]) or None,
            )
            
            logger.debug(
                f"Chat completed: {chat_response.eval_count} tokens "
                f"in {chat_response.total_duration_human}"
            )
            
            return chat_response
            
        except httpx.RequestError as e:
            logger.error(f"Network error during chat: {e}")
            raise OllamaConnectionError(f"Network error: {str(e)}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise CustomValidationError(f"Invalid JSON response: {str(e)}") from e
        except ValidationError as e:
            logger.error(f"Response validation error: {e}")
            raise CustomValidationError(f"Invalid response format: {str(e)}") from e
    
    @asynccontextmanager
    async def chat_stream(self, request: ChatRequest) -> AsyncGenerator[str, None]:
        """Stream chat response from model.
        
        Args:
            request: Chat request with stream=True
            
        Yields:
            Response text chunks
            
        Raises:
            OllamaConnectionError: If connection fails
            ModelNotFoundError: If model is not available
        """
        request.stream = True  # Ensure streaming is enabled
        
        try:
            client = await self._ensure_client()
            
            payload = {
                "model": request.model,
                "prompt": request.message,
                "stream": True,
                "options": {"temperature": request.temperature}
            }
            
            if request.max_tokens:
                payload["options"]["num_predict"] = request.max_tokens
            
            async with client.stream("POST", "/api/generate", json=payload) as response:
                if response.status_code == 404:
                    raise ModelNotFoundError(f"Model '{request.model}' not found")
                elif response.status_code != 200:
                    error_text = await response.aread()
                    raise OllamaConnectionError(
                        f"Stream request failed: HTTP {response.status_code} - {error_text.decode()}"
                    )
                
                async for line in response.aiter_lines():
                    if line.strip():
                        try:
                            chunk_data = json.loads(line)
                            if "response" in chunk_data:
                                yield chunk_data["response"]
                        except json.JSONDecodeError:
                            continue  # Skip invalid JSON lines
                            
        except httpx.RequestError as e:
            logger.error(f"Network error during streaming: {e}")
            raise OllamaConnectionError(f"Network error: {str(e)}") from e
    
    async def pull_model(self, model_name: str, show_progress: bool = True) -> DownloadProgress:
        """Pull/download a model from Ollama Hub.
        
        Args:
            model_name: Name of model to download
            show_progress: Whether to track download progress
            
        Returns:
            DownloadProgress object
            
        Raises:
            OllamaConnectionError: If connection fails
            ValidationError: If model name is invalid
        """
        if not model_name or not model_name.strip():
            raise CustomValidationError("Model name cannot be empty")
        
        # Validate model is allowed
        if not self.settings.is_model_allowed(model_name):
            raise CustomValidationError(f"Model '{model_name}' is not allowed")
        
        try:
            client = await self._ensure_client()
            
            # Generate unique job ID
            job_id = f"pull-{model_name.replace(':', '-')}-{int(time.time())}"
            
            # Start pull request (non-streaming for now)
            payload = {"name": model_name, "stream": False}
            response = await client.post("/api/pull", json=payload)
            
            if response.status_code == 404:
                return DownloadProgress(
                    job_id=job_id,
                    model_name=model_name,
                    status=DownloadStatus.FAILED,
                    error_message=f"Model '{model_name}' not found in Ollama Hub",
                )
            elif response.status_code != 200:
                error_text = response.text
                return DownloadProgress(
                    job_id=job_id,
                    model_name=model_name,
                    status=DownloadStatus.FAILED,
                    error_message=f"Pull failed: HTTP {response.status_code} - {error_text}",
                )
            
            # For now, assume successful completion
            # In a real implementation, this would track actual progress
            return DownloadProgress(
                job_id=job_id,
                model_name=model_name,
                status=DownloadStatus.COMPLETED,
                progress_percent=100.0,
                completed_at=datetime.now(),
            )
            
        except httpx.RequestError as e:
            logger.error(f"Network error during pull: {e}")
            job_id = f"pull-{model_name.replace(':', '-')}-{int(time.time())}"
            return DownloadProgress(
                job_id=job_id,
                model_name=model_name,
                status=DownloadStatus.FAILED,
                error_message=f"Network error: {str(e)}",
            )
        except Exception as e:
            logger.error(f"Unexpected error during pull: {e}")
            job_id = f"pull-{model_name.replace(':', '-')}-{int(time.time())}"
            return DownloadProgress(
                job_id=job_id,
                model_name=model_name,
                status=DownloadStatus.FAILED,
                error_message=f"Unexpected error: {str(e)}",
            )
    
    async def delete_model(self, model_name: str) -> bool:
        """Delete a model.
        
        Args:
            model_name: Name of model to delete
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            OllamaConnectionError: If connection fails
            ModelNotFoundError: If model doesn't exist
        """
        try:
            client = await self._ensure_client()
            
            payload = {"name": model_name}
            response = await client.delete("/api/delete", json=payload)
            
            if response.status_code == 404:
                raise ModelNotFoundError(f"Model '{model_name}' not found")
            elif response.status_code == 200:
                logger.info(f"Successfully deleted model: {model_name}")
                return True
            else:
                error_text = response.text
                logger.error(f"Failed to delete model {model_name}: {error_text}")
                return False
                
        except httpx.RequestError as e:
            logger.error(f"Network error during delete: {e}")
            raise OllamaConnectionError(f"Network error: {str(e)}") from e
        except ModelNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during delete: {e}")
            raise OllamaConnectionError(f"Unexpected error: {str(e)}") from e
    
    async def show_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed model information.
        
        Args:
            model_name: Name of the model
            
        Returns:
            Dict with detailed model information
            
        Raises:
            OllamaConnectionError: If connection fails
            ModelNotFoundError: If model doesn't exist
        """
        try:
            client = await self._ensure_client()
            
            payload = {"name": model_name}
            response = await client.post("/api/show", json=payload)
            
            if response.status_code == 404:
                raise ModelNotFoundError(f"Model '{model_name}' not found")
            elif response.status_code != 200:
                error_text = response.text
                raise OllamaConnectionError(
                    f"Failed to get model info: HTTP {response.status_code} - {error_text}"
                )
            
            return response.json()
            
        except httpx.RequestError as e:
            logger.error(f"Network error getting model info: {e}")
            raise OllamaConnectionError(f"Network error: {str(e)}") from e
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON response: {e}")
            raise CustomValidationError(f"Invalid JSON response: {str(e)}") from e
    
    def __repr__(self) -> str:
        return f"OllamaClient(base_url='{self.base_url}', timeout={self.timeout})"
