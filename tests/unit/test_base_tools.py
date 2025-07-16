"""
Unit tests for base tools
"""

import pytest
import json
from unittest.mock import AsyncMock, patch
from typing import Dict, Any

from src.ollama_mcp.tools.base_tools import (
    get_base_tools,
    handle_base_tool,
    _handle_list_models,
    _handle_chat,
    _handle_health_check,
    _handle_system_check
)
from src.ollama_mcp.client import OllamaClient, ModelInfo


class TestBaseTools:
    """Test base tools functionality."""

    def test_get_base_tools(self):
        """Test base tools list."""
        tools = get_base_tools()
        
        assert len(tools) == 4
        
        tool_names = [tool.name for tool in tools]
        assert "list_local_models" in tool_names
        assert "local_llm_chat" in tool_names
        assert "ollama_health_check" in tool_names
        assert "system_resource_check" in tool_names

    def test_list_local_models_tool_schema(self):
        """Test list_local_models tool schema."""
        tools = get_base_tools()
        list_tool = next(t for t in tools if t.name == "list_local_models")
        
        assert list_tool.description == "List all locally installed Ollama models with details"
        assert list_tool.inputSchema["type"] == "object"
        assert list_tool.inputSchema["required"] == []

    def test_local_llm_chat_tool_schema(self):
        """Test local_llm_chat tool schema."""
        tools = get_base_tools()
        chat_tool = next(t for t in tools if t.name == "local_llm_chat")
        
        assert "Chat with a local Ollama model" in chat_tool.description
        assert chat_tool.inputSchema["type"] == "object"
        assert "message" in chat_tool.inputSchema["required"]
        assert "message" in chat_tool.inputSchema["properties"]
        assert "model" in chat_tool.inputSchema["properties"]
        assert "temperature" in chat_tool.inputSchema["properties"]


class TestHandleBaseTool:
    """Test base tool handler routing."""

    @pytest.fixture
    def mock_client(self):
        """Create mock OllamaClient."""
        return AsyncMock(spec=OllamaClient)

    @pytest.mark.asyncio
    async def test_handle_list_local_models(self, mock_client):
        """Test list_local_models tool routing."""
        # Configure mock to return JSON-serializable data
        mock_client.list_models.return_value = {
            "success": True,
            "models": [
                ModelInfo(name="test-model", size=1024*1024*1024, modified="2024-01-01")
            ],
            "count": 1
        }
        
        result = await handle_base_tool("list_local_models", {}, mock_client)
        
        assert len(result) == 1
        assert result[0].type == "text"
        # Verify it's valid JSON
        json.loads(result[0].text)

    @pytest.mark.asyncio
    async def test_handle_local_llm_chat(self, mock_client):
        """Test local_llm_chat tool routing."""
        # Configure mock to return JSON-serializable data
        mock_client.chat.return_value = {
            "success": True,
            "response": "Hello! How can I help?",
            "model": "test-model"
        }
        
        arguments = {"message": "Hello", "model": "test-model"}
        result = await handle_base_tool("local_llm_chat", arguments, mock_client)
        
        assert len(result) == 1
        assert result[0].type == "text"
        json.loads(result[0].text)

    @pytest.mark.asyncio
    async def test_handle_ollama_health_check(self, mock_client):
        """Test ollama_health_check tool routing."""
        # Configure mock to return JSON-serializable data
        mock_client.health_check.return_value = {
            "healthy": True,
            "models_count": 3,
            "host": "http://localhost:11434",
            "message": "Ollama server is running"
        }
        
        result = await handle_base_tool("ollama_health_check", {}, mock_client)
        
        assert len(result) == 1
        assert result[0].type == "text"
        json.loads(result[0].text)

    @pytest.mark.asyncio
    async def test_handle_system_resource_check(self, mock_client):
        """Test system_resource_check tool routing."""
        result = await handle_base_tool("system_resource_check", {}, mock_client)
        
        assert len(result) == 1
        assert result[0].type == "text"
        json.loads(result[0].text)

    @pytest.mark.asyncio
    async def test_handle_unknown_tool(self, mock_client):
        """Test unknown tool handling."""
        result = await handle_base_tool("unknown_tool", {}, mock_client)
        
        assert len(result) == 1
        assert result[0].type == "text"
        assert "Unknown base tool" in result[0].text


class TestHandleListModels:
    """Test list models handler."""

    @pytest.fixture
    def mock_client(self):
        """Create mock OllamaClient."""
        return AsyncMock(spec=OllamaClient)

    @pytest.mark.asyncio
    async def test_handle_list_models_success(self, mock_client):
        """Test successful model listing."""
        models = [
            ModelInfo(name="model1", size=1024*1024*1024, modified="2024-01-01"),
            ModelInfo(name="model2", size=2048*1024*1024, modified="2024-01-02")
        ]
        mock_client.list_models.return_value = {
            "success": True,
            "models": models,
            "count": 2
        }
        
        result = await _handle_list_models(mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is True
        assert len(response["models"]) == 2
        assert response["total_count"] == 2
        assert response["models"][0]["name"] == "model1"
        assert response["models"][1]["name"] == "model2"
        assert "usage_tip" in response

    @pytest.mark.asyncio
    async def test_handle_list_models_empty(self, mock_client):
        """Test model listing with no models."""
        mock_client.list_models.return_value = {
            "success": True,
            "models": [],
            "count": 0
        }
        
        result = await _handle_list_models(mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is True
        assert response["models"] == []
        assert response["total_count"] == 0
        assert "No models found" in response["message"]
        assert "next_steps" in response

    @pytest.mark.asyncio
    async def test_handle_list_models_error(self, mock_client):
        """Test model listing with error."""
        mock_client.list_models.return_value = {
            "success": False,
            "error": "Connection failed",
            "models": []
        }
        
        result = await _handle_list_models(mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is False
        assert "Connection failed" in response["error"]
        assert "troubleshooting" in response


class TestHandleChat:
    """Test chat handler."""

    @pytest.fixture
    def mock_client(self):
        """Create mock OllamaClient."""
        return AsyncMock(spec=OllamaClient)

    @pytest.mark.asyncio
    async def test_handle_chat_success(self, mock_client):
        """Test successful chat."""
        mock_client.chat.return_value = {
            "success": True,
            "response": "Hello! How can I help?",
            "model": "test-model",
            "metadata": {"eval_count": 10}
        }
        
        arguments = {"message": "Hello", "model": "test-model"}
        result = await _handle_chat(arguments, mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is True
        assert response["response"] == "Hello! How can I help?"
        assert response["model_used"] == "test-model"
        assert response["user_message"] == "Hello"
        assert "privacy_note" in response

    @pytest.mark.asyncio
    async def test_handle_chat_no_message(self, mock_client):
        """Test chat with no message."""
        arguments = {}
        result = await _handle_chat(arguments, mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is False
        assert "Message is required" in response["error"]

    @pytest.mark.asyncio
    async def test_handle_chat_auto_model_selection(self, mock_client):
        """Test chat with automatic model selection."""
        # Mock available models
        models = [ModelInfo(name="auto-model", size=1024, modified="2024-01-01")]
        mock_client.list_models.return_value = {
            "success": True,
            "models": models,
            "count": 1
        }
        
        # Mock chat response
        mock_client.chat.return_value = {
            "success": True,
            "response": "Auto-selected model response",
            "model": "auto-model"
        }
        
        arguments = {"message": "Hello"}
        result = await _handle_chat(arguments, mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is True
        assert response["model_used"] == "auto-model"

    @pytest.mark.asyncio
    async def test_handle_chat_no_models_available(self, mock_client):
        """Test chat when no models are available."""
        mock_client.list_models.return_value = {
            "success": True,
            "models": [],
            "count": 0
        }
        
        arguments = {"message": "Hello"}
        result = await _handle_chat(arguments, mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is False
        assert "No models available" in response["error"]
        assert "next_steps" in response

    @pytest.mark.asyncio
    async def test_handle_chat_error(self, mock_client):
        """Test chat with error."""
        mock_client.chat.return_value = {
            "success": False,
            "error": "Model not found",
            "response": ""
        }
        
        arguments = {"message": "Hello", "model": "test-model"}
        result = await _handle_chat(arguments, mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["success"] is False
        assert "Model not found" in response["error"]


class TestHandleHealthCheck:
    """Test health check handler."""

    @pytest.fixture
    def mock_client(self):
        """Create mock OllamaClient."""
        return AsyncMock(spec=OllamaClient)

    @pytest.mark.asyncio
    async def test_handle_health_check_success(self, mock_client):
        """Test successful health check."""
        mock_client.health_check.return_value = {
            "healthy": True,
            "models_count": 3,
            "host": "http://localhost:11434",
            "message": "Ollama server is running"
        }
        
        result = await _handle_health_check(mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["status"] == "HEALTHY"
        assert response["models_available"] == 3
        assert "next_steps" in response

    @pytest.mark.asyncio
    async def test_handle_health_check_unhealthy(self, mock_client):
        """Test unhealthy health check."""
        mock_client.health_check.return_value = {
            "healthy": False,
            "error": "Connection refused",
            "host": "http://localhost:11434"
        }
        
        result = await _handle_health_check(mock_client)
        
        assert len(result) == 1
        response = json.loads(result[0].text)
        assert response["status"] == "UNHEALTHY"
        assert "troubleshooting" in response


class TestHandleSystemCheck:
    """Test system check handler."""

    @pytest.mark.asyncio
    async def test_handle_system_check_success(self):
        """Test successful system check."""
        with patch('psutil.cpu_count', return_value=8):
            with patch('psutil.virtual_memory') as mock_memory:
                # Mock memory object with required attributes
                mock_memory.return_value.total = 16 * 1024 * 1024 * 1024  # 16GB
                mock_memory.return_value.available = 8 * 1024 * 1024 * 1024  # 8GB
                mock_memory.return_value.percent = 50.0
                
                with patch('psutil.disk_usage') as mock_disk:
                    # Mock disk object with required attributes
                    mock_disk.return_value.total = 500 * 1024 * 1024 * 1024  # 500GB
                    mock_disk.return_value.free = 200 * 1024 * 1024 * 1024  # 200GB
                    
                    with patch('src.ollama_mcp.tools.base_tools._get_gpu_info') as mock_gpu:
                        mock_gpu.return_value = {
                            "gpu_count": 0,
                            "gpus": [],
                            "detection_method": "none"
                        }
                        
                        result = await _handle_system_check()
                        
                        assert len(result) == 1
                        response = json.loads(result[0].text)
                        assert response["success"] is True
                        assert response["system_resources"]["cpu_cores"] == 8
                        assert response["system_resources"]["total_memory_gb"] == 16.0
                        assert "ai_readiness" in response

    @pytest.mark.asyncio
    async def test_handle_system_check_with_gpu(self):
        """Test system check with GPU detection."""
        with patch('psutil.cpu_count', return_value=8):
            with patch('psutil.virtual_memory') as mock_memory:
                mock_memory.return_value.total = 16 * 1024 * 1024 * 1024
                mock_memory.return_value.available = 8 * 1024 * 1024 * 1024
                mock_memory.return_value.percent = 50.0
                
                with patch('psutil.disk_usage') as mock_disk:
                    mock_disk.return_value.total = 500 * 1024 * 1024 * 1024
                    mock_disk.return_value.free = 200 * 1024 * 1024 * 1024
                    
                    # Mock GPU detection
                    with patch('src.ollama_mcp.tools.base_tools._get_gpu_info') as mock_gpu:
                        mock_gpu.return_value = {
                            "gpu_count": 1,
                            "gpus": [{"name": "Test GPU"}],
                            "detection_method": "nvidia-smi"
                        }
                        
                        result = await _handle_system_check()
                        
                        assert len(result) == 1
                        response = json.loads(result[0].text)
                        assert response["success"] is True
                        assert response["gpu_resources"]["gpu_count"] == 1
                        assert response["gpu_resources"]["detection_method"] == "nvidia-smi" 