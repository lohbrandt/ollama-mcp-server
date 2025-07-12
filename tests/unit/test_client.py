"""
Unit tests for OllamaClient
"""

import pytest
import asyncio
from unittest.mock import AsyncMock, patch, MagicMock
from typing import Dict, Any

from src.ollama_mcp.client import OllamaClient, ModelInfo


class TestModelInfo:
    """Test ModelInfo dataclass."""

    def test_model_info_creation(self):
        """Test ModelInfo object creation."""
        model = ModelInfo(
            name="test-model",
            size=1024 * 1024 * 1024,  # 1GB
            modified="2024-01-01T12:00:00Z"
        )
        
        assert model.name == "test-model"
        assert model.size == 1024 * 1024 * 1024
        assert model.modified == "2024-01-01T12:00:00Z"

    def test_size_human_property(self):
        """Test human-readable size formatting."""
        # Test bytes
        model = ModelInfo(name="test", size=512, modified="2024-01-01")
        assert model.size_human == "512.0 B"
        
        # Test KB
        model = ModelInfo(name="test", size=1024, modified="2024-01-01")
        assert model.size_human == "1.0 KB"
        
        # Test MB
        model = ModelInfo(name="test", size=1024 * 1024, modified="2024-01-01")
        assert model.size_human == "1.0 MB"
        
        # Test GB
        model = ModelInfo(name="test", size=1024 * 1024 * 1024, modified="2024-01-01")
        assert model.size_human == "1.0 GB"


class TestOllamaClient:
    """Test OllamaClient class."""

    @pytest.fixture
    def client(self):
        """Create OllamaClient instance for testing."""
        return OllamaClient(host="http://localhost:11434", timeout=10)

    def test_client_initialization(self, client):
        """Test client initialization."""
        assert client.host == "http://localhost:11434"
        assert client.timeout == 10
        assert client.client is None
        assert client._initialized is False
        assert client._init_error is None

    @patch('src.ollama_mcp.client.ollama')
    def test_ensure_client_success(self, mock_ollama, client):
        """Test successful client initialization."""
        mock_client = MagicMock()
        mock_ollama.Client.return_value = mock_client
        
        result = client._ensure_client()
        
        assert result is True
        assert client.client == mock_client
        assert client._initialized is True
        assert client._init_error is None
        mock_ollama.Client.assert_called_once_with(host="http://localhost:11434")

    @patch('src.ollama_mcp.client.ollama')
    def test_ensure_client_import_error(self, mock_ollama, client):
        """Test client initialization with import error."""
        mock_ollama.Client.side_effect = ImportError("ollama not found")
        
        result = client._ensure_client()
        
        assert result is False
        assert client.client is None
        assert client._initialized is True
        assert "ollama package not installed" in client._init_error

    @patch('src.ollama_mcp.client.ollama')
    def test_ensure_client_other_error(self, mock_ollama, client):
        """Test client initialization with other errors."""
        mock_ollama.Client.side_effect = Exception("Connection failed")
        
        result = client._ensure_client()
        
        assert result is False
        assert client.client is None
        assert client._initialized is True
        assert "Failed to initialize" in client._init_error

    @pytest.mark.asyncio
    async def test_health_check_success(self, client):
        """Test successful health check."""
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_list', return_value=[1, 2, 3]):
                result = await client.health_check()
                
                assert result["healthy"] is True
                assert result["models_count"] == 3
                assert result["host"] == "http://localhost:11434"
                assert "responsive" in result["message"]

    @pytest.mark.asyncio
    async def test_health_check_client_failure(self, client):
        """Test health check when client initialization fails."""
        with patch.object(client, '_ensure_client', return_value=False):
            client._init_error = "Test error"
            result = await client.health_check()
            
            assert result["healthy"] is False
            assert result["error"] == "Test error"
            assert result["host"] == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_health_check_timeout(self, client):
        """Test health check timeout handling."""
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_list', side_effect=asyncio.TimeoutError):
                result = await client.health_check()
                
                assert result["healthy"] is False
                assert "timeout" in result["error"]
                assert result["host"] == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_health_check_exception(self, client):
        """Test health check exception handling."""
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_list', side_effect=Exception("Test error")):
                result = await client.health_check()
                
                assert result["healthy"] is False
                assert result["error"] == "Test error"
                assert result["host"] == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_list_models_success(self, client):
        """Test successful model listing."""
        mock_models = [
            MagicMock(model="model1", size=1024, modified_at="2024-01-01"),
            MagicMock(model="model2", size=2048, modified_at="2024-01-02")
        ]
        
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_list', return_value=mock_models):
                result = await client.list_models()
                
                assert result["success"] is True
                assert len(result["models"]) == 2
                assert result["count"] == 2
                assert result["models"][0].name == "model1"
                assert result["models"][1].name == "model2"

    @pytest.mark.asyncio
    async def test_list_models_empty(self, client):
        """Test model listing with no models."""
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_list', return_value=[]):
                result = await client.list_models()
                
                assert result["success"] is True
                assert result["models"] == []
                assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_list_models_client_failure(self, client):
        """Test model listing when client initialization fails."""
        with patch.object(client, '_ensure_client', return_value=False):
            client._init_error = "Test error"
            result = await client.list_models()
            
            assert result["success"] is False
            assert result["error"] == "Test error"
            assert result["models"] == []

    @pytest.mark.asyncio
    async def test_list_models_timeout(self, client):
        """Test model listing timeout handling."""
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_list', side_effect=asyncio.TimeoutError):
                result = await client.list_models()
                
                assert result["success"] is False
                assert "timeout" in result["error"]
                assert result["models"] == []

    @pytest.mark.asyncio
    async def test_list_models_parsing_error(self, client):
        """Test model listing with parsing errors."""
        # Mock model with missing attributes
        mock_models = [MagicMock()]
        del mock_models[0].model
        del mock_models[0].size
        del mock_models[0].modified_at
        
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_list', return_value=mock_models):
                result = await client.list_models()
                
                assert result["success"] is True
                assert result["models"] == []
                assert result["count"] == 0

    @pytest.mark.asyncio
    async def test_chat_success(self, client):
        """Test successful chat."""
        mock_response = {
            'message': {'content': 'Hello, how can I help?'},
            'eval_count': 10,
            'total_duration': 1500
        }
        
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_chat', return_value=mock_response):
                result = await client.chat("test-model", "Hello", 0.7)
                
                assert result["success"] is True
                assert result["response"] == "Hello, how can I help?"
                assert result["model"] == "test-model"
                assert result["metadata"]["eval_count"] == 10
                assert result["metadata"]["total_duration"] == 1500

    @pytest.mark.asyncio
    async def test_chat_client_failure(self, client):
        """Test chat when client initialization fails."""
        with patch.object(client, '_ensure_client', return_value=False):
            client._init_error = "Test error"
            result = await client.chat("test-model", "Hello")
            
            assert result["success"] is False
            assert result["error"] == "Test error"
            assert result["response"] == ""

    @pytest.mark.asyncio
    async def test_chat_timeout(self, client):
        """Test chat timeout handling."""
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_chat', side_effect=asyncio.TimeoutError):
                result = await client.chat("test-model", "Hello")
                
                assert result["success"] is False
                assert "timeout" in result["error"]
                assert result["response"] == ""

    @pytest.mark.asyncio
    async def test_chat_exception(self, client):
        """Test chat exception handling."""
        with patch.object(client, '_ensure_client', return_value=True):
            with patch.object(client, '_sync_chat', side_effect=Exception("Test error")):
                result = await client.chat("test-model", "Hello")
                
                assert result["success"] is False
                assert result["error"] == "Test error"
                assert result["response"] == ""

    def test_sync_list_method(self, client):
        """Test _sync_list method."""
        mock_client = MagicMock()
        mock_client.list.return_value = [{"name": "test"}]
        client.client = mock_client
        
        result = client._sync_list()
        
        assert result == [{"name": "test"}]
        mock_client.list.assert_called_once()

    def test_sync_chat_method(self, client):
        """Test _sync_chat method."""
        mock_client = MagicMock()
        mock_client.chat.return_value = {"message": {"content": "test"}}
        client.client = mock_client
        
        messages = [{"role": "user", "content": "Hello"}]
        options = {"temperature": 0.7}
        
        result = client._sync_chat("test-model", messages, options)
        
        assert result == {"message": {"content": "test"}}
        mock_client.chat.assert_called_once_with(
            model="test-model",
            messages=messages,
            options=options
        )

    def test_sync_pull_method(self, client):
        """Test _sync_pull method."""
        mock_client = MagicMock()
        mock_client.pull.return_value = {"status": "success"}
        client.client = mock_client
        
        result = client._sync_pull("test-model")
        
        assert result == {"status": "success"}
        mock_client.pull.assert_called_once_with("test-model")

    def test_sync_remove_method(self, client):
        """Test _sync_remove method."""
        mock_client = MagicMock()
        mock_client.delete.return_value = {"status": "success"}
        client.client = mock_client
        
        result = client._sync_remove("test-model")
        
        assert result == {"status": "success"}
        mock_client.delete.assert_called_once_with("test-model") 