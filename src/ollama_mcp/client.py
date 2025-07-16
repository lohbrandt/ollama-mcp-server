"""
Ollama Client - MCP Server v1.2 Refactored
Resilient async client for Ollama communication following MCP protocol standards

Features:
- Full async/await patterns with proper error handling
- MCP protocol compliance with standardized responses
- Professional error handling with troubleshooting information
- Cross-platform compatibility
- Comprehensive timeout management
"""

import asyncio
import logging
from typing import Dict, List, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ModelInfo:
    """Standardized model information following MCP protocol standards."""
    name: str
    size: int
    modified: str
    digest: str = ""
    
    @property
    def size_human(self) -> str:
        """Human readable size formatting."""
        size = float(self.size)
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} PB"


class OllamaClient:
    """
    Resilient async Ollama client following MCP protocol standards.
    
    Key features:
    - Full async/await patterns with proper error handling
    - MCP protocol compliance with standardized responses
    - Professional error handling with troubleshooting information
    - Cross-platform compatibility
    - Comprehensive timeout management
    """
    
    def __init__(self, host: str = "http://localhost:11434", timeout: float = 30.0):
        """Initialize client with proper host formatting."""
        self.host = host.rstrip('/')
        self.timeout = timeout
        self._initialized = False
        self._init_error = None
        logger.debug(f"OllamaClient created for {self.host}")
    
    def _ensure_client(self) -> bool:
        """Ensure client is initialized, return success status."""
        if self._initialized:
            return self._init_error is None
        
        try:
            import ollama
            self._initialized = True
            logger.debug("Ollama client initialized successfully")
            return True
        except ImportError:
            self._init_error = "ollama package not installed. Run: pip install ollama"
            self._initialized = True
            return False
        except Exception as e:
            self._init_error = f"Failed to initialize: {e}"
            self._initialized = True
            return False
    
    async def health_check(self) -> Dict[str, Any]:
        """Check Ollama server health with proper async patterns."""
        if not self._ensure_client():
            return self._create_health_error_response(
                "Client initialization failed", self._init_error
            )
        
        try:
            # Use httpx for async HTTP requests
            import httpx
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(f"{self.host}/api/tags")
                response.raise_for_status()
                
                data = response.json()
                models_count = len(data.get("models", []))
                
                return {
                    "healthy": True,
                    "models_count": models_count,
                    "host": self.host,
                    "message": "Ollama server is running"
                }
                
        except httpx.TimeoutException:
            return self._create_health_error_response(
                "Connection timeout", "Check network connection and Ollama status"
            )
        except httpx.HTTPStatusError as e:
            return self._create_health_error_response(
                f"HTTP error: {e.response.status_code}",
                "Ollama server responded with error"
            )
        except httpx.ConnectError:
            return self._create_health_error_response(
                "Connection refused",
                "Ollama server is not running. Start with: ollama serve"
            )
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return self._create_health_error_response(
                f"Unexpected error: {e}",
                "Check system logs for details"
            )
    
    def _create_health_error_response(self, error: str, troubleshooting: str) -> Dict[str, Any]:
        """Create standardized health error response."""
        return {
            "healthy": False,
            "error": error,
            "host": self.host,
            "troubleshooting": troubleshooting
        }
    
    async def list_models(self) -> Dict[str, Any]:
        """List available models with error handling"""
        if not self._ensure_client():
            return {
                "success": False,
                "error": self._init_error,
                "models": []
            }
        
        try:
            loop = asyncio.get_event_loop()
            raw_models = await asyncio.wait_for(
                loop.run_in_executor(None, self._sync_list),
                timeout=10.0
            )
            
            models = []
            for model_data in raw_models:
                try:
                    models.append(ModelInfo(
                        name=getattr(model_data, 'model', model_data.get('name', 'unknown')),
                        size=getattr(model_data, 'size', model_data.get('size', 0)),
                        modified=str(getattr(model_data, 'modified_at', model_data.get('modified', 'unknown')))
                    ))
                except Exception as e:
                    logger.warning(f"Model parsing error: {e}")
                    continue
            
            return {
                "success": True,
                "models": models,
                "count": len(models)
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Timeout listing models",
                "models": []
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "models": []
            }
    
    async def chat(self, model: str, prompt: str, temperature: float = 0.7) -> Dict[str, Any]:
        """Generate response using Ollama model"""
        if not self._ensure_client():
            return {
                "success": False,
                "error": self._init_error,
                "response": ""
            }
        
        try:
            messages = [{"role": "user", "content": prompt}]
            options = {"temperature": temperature}
            
            loop = asyncio.get_event_loop()
            response = await asyncio.wait_for(
                loop.run_in_executor(None, self._sync_chat, model, messages, options),
                timeout=120.0
            )
            
            content = response.get('message', {}).get('content', '')
            
            return {
                "success": True,
                "response": content,
                "model": model,
                "metadata": {
                    "eval_count": response.get('eval_count', 0),
                    "total_duration": response.get('total_duration', 0)
                }
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Chat timeout - model may be loading",
                "response": ""
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "response": ""
            }
    
    async def pull_model(self, model_name: str) -> Dict[str, Any]:
        """Download/pull a model from Ollama Hub"""
        if not self._ensure_client():
            return {
                "success": False,
                "error": self._init_error
            }
        
        try:
            loop = asyncio.get_event_loop()
            result = await asyncio.wait_for(
                loop.run_in_executor(None, self._sync_pull, model_name),
                timeout=1800.0  # 30 minutes for download
            )
            
            return {
                "success": True,
                "message": f"Model {model_name} downloaded successfully",
                "model_name": model_name
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Download timeout - model may be very large",
                "model_name": model_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name
            }
    
    async def remove_model(self, model_name: str) -> Dict[str, Any]:
        """Remove a model from local storage"""
        if not self._ensure_client():
            return {
                "success": False,
                "error": self._init_error
            }
        
        try:
            loop = asyncio.get_event_loop()
            await asyncio.wait_for(
                loop.run_in_executor(None, self._sync_remove, model_name),
                timeout=30.0
            )
            
            return {
                "success": True,
                "message": f"Model {model_name} removed successfully",
                "model_name": model_name
            }
            
        except asyncio.TimeoutError:
            return {
                "success": False,
                "error": "Remove timeout",
                "model_name": model_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model_name": model_name
            }
    
    # Sync methods for executor
    def _sync_list(self) -> List[Any]:
        """Sync list models"""
        try:
            import ollama
            response = ollama.list()
            return getattr(response, 'models', response.get('models', []))
        except Exception as e:
            raise Exception(f"Failed to list models: {e}")
    
    def _sync_chat(self, model: str, messages: List[Dict], options: Dict) -> Dict:
        """Sync chat"""
        try:
            import ollama
            return ollama.chat(model=model, messages=messages, options=options)
        except Exception as e:
            raise Exception(f"Failed to chat: {e}")
    
    def _sync_pull(self, model_name: str) -> Dict:
        """Sync pull model"""
        try:
            import ollama
            return ollama.pull(model_name)
        except Exception as e:
            raise Exception(f"Failed to pull model: {e}")
    
    def _sync_remove(self, model_name: str) -> Dict:
        """Sync remove model"""
        try:
            import ollama
            return ollama.delete(model_name)
        except Exception as e:
            raise Exception(f"Failed to remove model: {e}")
