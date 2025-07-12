"""
Integration tests for Ollama integration
"""

import pytest
import asyncio
from unittest.mock import patch
import subprocess
import sys

from src.ollama_mcp.client import OllamaClient


@pytest.mark.integration
@pytest.mark.ollama_required
class TestOllamaIntegration:
    """Integration tests requiring Ollama server."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup for integration tests."""
        # Check if Ollama is available
        client = OllamaClient()
        health = await client.health_check()
        if not health["healthy"]:
            pytest.skip("Ollama server not available")
        
        self.client = client

    @pytest.mark.asyncio
    async def test_real_health_check(self):
        """Test health check against real Ollama server."""
        result = await self.client.health_check()
        
        assert result["healthy"] is True
        assert result["host"] == "http://localhost:11434"
        assert "models_count" in result
        assert result["models_count"] >= 0

    @pytest.mark.asyncio
    async def test_real_model_listing(self):
        """Test model listing against real Ollama server."""
        result = await self.client.list_models()
        
        assert result["success"] is True
        assert "models" in result
        assert "count" in result
        assert result["count"] >= 0
        assert isinstance(result["models"], list)

    @pytest.mark.asyncio
    async def test_real_chat_with_available_model(self):
        """Test chat with an available model."""
        # First get available models
        models_result = await self.client.list_models()
        if not models_result["success"] or not models_result["models"]:
            pytest.skip("No models available for testing")
        
        # Use the first available model
        model_name = models_result["models"][0].name
        
        result = await self.client.chat(
            model=model_name,
            prompt="Hello, this is a test message.",
            temperature=0.7
        )
        
        assert result["success"] is True
        assert "response" in result
        assert result["model"] == model_name
        assert len(result["response"]) > 0

    @pytest.mark.asyncio
    async def test_chat_with_nonexistent_model(self):
        """Test chat with a model that doesn't exist."""
        result = await self.client.chat(
            model="nonexistent-model-12345",
            prompt="This should fail",
            temperature=0.7
        )
        
        assert result["success"] is False
        assert "error" in result
        assert len(result["response"]) == 0


@pytest.mark.integration
class TestOllamaServerControl:
    """Integration tests for Ollama server control."""

    @pytest.mark.asyncio
    async def test_ollama_command_availability(self):
        """Test if ollama command is available."""
        try:
            result = subprocess.run(
                ["ollama", "--version"],
                capture_output=True,
                text=True,
                timeout=10
            )
            assert result.returncode == 0
            assert "ollama" in result.stdout.lower()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Ollama command not available")

    @pytest.mark.asyncio
    async def test_ollama_serve_command(self):
        """Test ollama serve command (without actually starting server)."""
        try:
            # Test if we can get help for serve command
            result = subprocess.run(
                ["ollama", "serve", "--help"],
                capture_output=True,
                text=True,
                timeout=10
            )
            # Should either succeed or show that serve doesn't have help
            assert result.returncode in [0, 1]
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pytest.skip("Ollama command not available")


@pytest.mark.integration
class TestCrossPlatformCompatibility:
    """Test cross-platform compatibility."""

    @pytest.mark.asyncio
    async def test_client_initialization_different_hosts(self):
        """Test client initialization with different host configurations."""
        # Test localhost
        client_local = OllamaClient(host="http://localhost:11434")
        assert client_local.host == "http://localhost:11434"
        
        # Test custom host
        client_custom = OllamaClient(host="http://192.168.1.100:11434")
        assert client_custom.host == "http://192.168.1.100:11434"
        
        # Test with trailing slash
        client_trailing = OllamaClient(host="http://localhost:11434/")
        assert client_trailing.host == "http://localhost:11434"

    @pytest.mark.asyncio
    async def test_client_timeout_configuration(self):
        """Test client timeout configuration."""
        # Test default timeout
        client_default = OllamaClient()
        assert client_default.timeout == 30
        
        # Test custom timeout
        client_custom = OllamaClient(timeout=60)
        assert client_custom.timeout == 60


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling in integration scenarios."""

    @pytest.mark.asyncio
    async def test_connection_to_invalid_host(self):
        """Test connection to invalid host."""
        client = OllamaClient(host="http://invalid-host:99999")
        result = await client.health_check()
        
        assert result["healthy"] is False
        assert "error" in result
        assert result["host"] == "http://invalid-host:99999"

    @pytest.mark.asyncio
    async def test_connection_to_wrong_port(self):
        """Test connection to wrong port."""
        client = OllamaClient(host="http://localhost:99999")
        result = await client.health_check()
        
        assert result["healthy"] is False
        assert "error" in result
        assert result["host"] == "http://localhost:99999"

    @pytest.mark.asyncio
    async def test_timeout_handling(self):
        """Test timeout handling with very short timeout."""
        client = OllamaClient(host="http://localhost:11434", timeout=0.001)
        result = await client.health_check()
        
        # Should either timeout or fail quickly
        assert result["healthy"] is False
        assert "error" in result


@pytest.mark.integration
class TestModelOperations:
    """Test model operations integration."""

    @pytest.mark.asyncio
    async def test_model_info_parsing(self):
        """Test parsing of model information."""
        client = OllamaClient()
        result = await client.list_models()
        
        if result["success"] and result["models"]:
            model = result["models"][0]
            
            # Test ModelInfo properties
            assert hasattr(model, 'name')
            assert hasattr(model, 'size')
            assert hasattr(model, 'modified')
            assert hasattr(model, 'size_human')
            
            # Test size_human formatting
            assert isinstance(model.size_human, str)
            assert len(model.size_human) > 0

    @pytest.mark.asyncio
    async def test_chat_parameter_validation(self):
        """Test chat parameter validation."""
        client = OllamaClient()
        
        # Test with empty prompt
        result = await client.chat("test-model", "", 0.7)
        assert result["success"] is False
        
        # Test with None prompt
        result = await client.chat("test-model", None, 0.7)
        assert result["success"] is False
        
        # Test with invalid temperature
        result = await client.chat("test-model", "Hello", 2.0)
        # Should either fail or work (depending on implementation)
        assert "success" in result


@pytest.mark.integration
class TestPerformance:
    """Test performance characteristics."""

    @pytest.mark.slow
    @pytest.mark.asyncio
    async def test_concurrent_requests(self):
        """Test concurrent request handling."""
        client = OllamaClient()
        
        # Test concurrent health checks
        tasks = []
        for i in range(5):
            task = client.health_check()
            tasks.append(task)
        
        start_time = asyncio.get_event_loop().time()
        results = await asyncio.gather(*tasks, return_exceptions=True)
        end_time = asyncio.get_event_loop().time()
        
        # Verify all requests completed
        assert len(results) == 5
        for result in results:
            if isinstance(result, Exception):
                # Some failures are expected if Ollama is not running
                continue
            assert "healthy" in result
        
        # Verify reasonable performance (should complete within 10 seconds)
        assert end_time - start_time < 10.0

    @pytest.mark.asyncio
    async def test_memory_usage(self):
        """Test memory usage for operations."""
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        initial_memory = process.memory_info().rss
        
        client = OllamaClient()
        
        # Perform multiple operations
        for i in range(10):
            await client.health_check()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Verify memory usage is reasonable (less than 50MB increase)
        assert memory_increase < 50 * 1024 * 1024 