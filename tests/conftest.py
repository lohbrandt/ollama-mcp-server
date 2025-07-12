"""
Pytest configuration and fixtures for Ollama MCP Server tests
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any, List, Optional
import json

from src.ollama_mcp.client import ModelInfo


@pytest.fixture
def mock_ollama_models() -> List[Dict[str, Any]]:
    """Mock Ollama models data."""
    return [
        {
            "name": "llama3.2:latest",
            "size": 2048000000,
            "modified_at": "2024-01-01T12:00:00Z",
            "digest": "sha256:abcd1234"
        },
        {
            "name": "qwen2.5-coder:7b",
            "size": 4096000000,
            "modified_at": "2024-01-02T12:00:00Z",
            "digest": "sha256:efgh5678"
        }
    ]


@pytest.fixture
def mock_ollama_client() -> AsyncMock:
    """Mock Ollama client for testing."""
    client = AsyncMock()
    client.host = "http://localhost:11434"
    client.timeout = 10.0
    return client


@pytest.fixture
def mock_health_response() -> Dict[str, Any]:
    """Mock health check response."""
    return {
        "healthy": True,
        "host": "http://localhost:11434",
        "models_count": 2,
        "message": "Ollama server is running"
    }


@pytest.fixture
def mock_chat_response() -> Dict[str, Any]:
    """Mock chat response."""
    return {
        "success": True,
        "response": "Hello! I'm a test response from the model.",
        "model": "llama3.2",
        "metadata": {
            "eval_count": 10,
            "total_duration": 1500
        }
    }


@pytest.fixture
def sample_model_info() -> List[ModelInfo]:
    """Sample ModelInfo objects for testing."""
    return [
        ModelInfo(
            name="llama3.2:latest",
            size=2048000000,
            modified="2024-01-01T12:00:00Z"
        ),
        ModelInfo(
            name="qwen2.5-coder:7b",
            size=4096000000,
            modified="2024-01-02T12:00:00Z"
        )
    ]


@pytest.fixture
def mock_system_info() -> Dict[str, Any]:
    """Mock system information."""
    return {
        "cpu_count": 8,
        "memory_gb": 16.0,
        "platform": "Darwin",
        "gpu_info": {
            "available": True,
            "name": "Apple M1 Pro",
            "memory_gb": 16.0
        }
    }


def assert_successful_response(
    response_text: str, expected_data_keys: Optional[List[str]] = None
) -> None:
    """Assert that response is successful and contains expected data."""
    response = json.loads(response_text)
    assert response["success"] is True
    assert "data" in response or "models" in response or "response" in response
    
    if expected_data_keys:
        for key in expected_data_keys:
            assert key in response


def assert_error_response(
    response_text: str, expected_error_text: Optional[str] = None
) -> None:
    """Assert that response contains error with troubleshooting."""
    response = json.loads(response_text)
    assert response["success"] is False
    assert "error" in response
    
    if expected_error_text:
        assert expected_error_text in response["error"]
    
    # Should include troubleshooting information
    assert "troubleshooting" in response or "next_steps" in response


def create_mock_model_response(name: str, size_gb: float = 2.0) -> Dict[str, Any]:
    """Create mock model response data."""
    return {
        "name": name,
        "size": int(size_gb * 1024 * 1024 * 1024),
        "size_human": f"{size_gb}GB",
        "modified": "2024-01-01T12:00:00Z",
        "digest": f"sha256:{'a' * 64}"
    } 