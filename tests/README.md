# Testing Guide for Ollama MCP Server

This directory contains comprehensive tests for the Ollama MCP Server, following the established testing patterns and standards.

## Test Structure

```
tests/
├── conftest.py              # Pytest configuration and fixtures
├── unit/                    # Unit tests
│   ├── test_client.py      # OllamaClient tests
│   └── test_base_tools.py  # Base tools tests
├── integration/             # Integration tests
│   └── test_ollama_integration.py
└── README.md               # This file
```

## Test Categories

### Unit Tests (`tests/unit/`)
- **Purpose**: Test individual functions and classes in isolation
- **Scope**: Mock external dependencies, test edge cases
- **Speed**: Fast execution
- **Coverage**: All code paths and error conditions

### Integration Tests (`tests/integration/`)
- **Purpose**: Test component interactions and real-world scenarios
- **Scope**: May require external services (Ollama server)
- **Speed**: Slower execution
- **Coverage**: End-to-end workflows

## Running Tests

### Prerequisites
```bash
# Install test dependencies
pip install -e .[dev]

# Or install individually
pip install pytest pytest-asyncio pytest-cov black isort flake8 mypy httpx
```

### Basic Test Commands
```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=src/ollama_mcp --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py

# Run specific test class
pytest tests/unit/test_client.py::TestOllamaClient

# Run specific test method
pytest tests/unit/test_client.py::TestOllamaClient::test_health_check_success
```

### Test Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Skip slow tests
pytest -m "not slow"

# Skip tests requiring Ollama
pytest -m "not ollama_required"

# Run only fast tests
pytest -m "unit and not slow"
```

### Using the Test Runner
```bash
# Run comprehensive test suite
python run_tests.py
```

## Test Patterns

### Async Testing
All async functions must be tested with `@pytest.mark.asyncio`:

```python
@pytest.mark.asyncio
async def test_async_function():
    result = await some_async_function()
    assert result["success"] is True
```

### Mocking
Use `unittest.mock` for mocking dependencies:

```python
from unittest.mock import AsyncMock, patch

@pytest.mark.asyncio
async def test_with_mock():
    with patch('module.function') as mock_func:
        mock_func.return_value = {"success": True}
        result = await test_function()
        assert result["success"] is True
```

### Error Testing
Always test error conditions:

```python
@pytest.mark.asyncio
async def test_error_handling():
    with patch('module.function', side_effect=Exception("Test error")):
        result = await test_function()
        assert result["success"] is False
        assert "error" in result
```

### Response Validation
Use helper functions for consistent response validation:

```python
from tests.conftest import assert_successful_response, assert_error_response

def test_response_format():
    result = await some_function()
    assert_successful_response(result[0].text, ["data", "success"])
```

## Test Fixtures

Common fixtures are defined in `conftest.py`:

- `mock_ollama_models`: Mock model data
- `mock_ollama_client`: Mock OllamaClient instance
- `mock_health_response`: Mock health check response
- `sample_model_info`: Sample ModelInfo objects
- `mock_system_info`: Mock system information

## Coverage Requirements

- **Unit Tests**: 90%+ coverage for all modules
- **Integration Tests**: Critical user workflows
- **Error Handling**: All exception paths tested
- **Edge Cases**: Boundary conditions and invalid inputs

## Code Quality

Tests are subject to the same code quality standards:

```bash
# Format code
black tests/

# Sort imports
isort tests/

# Type checking
mypy tests/

# Linting
flake8 tests/
```

## Continuous Integration

Tests are automatically run in CI/CD with:

1. **Unit Tests**: All unit tests must pass
2. **Integration Tests**: Basic integration tests (without Ollama)
3. **Code Quality**: Formatting, linting, type checking
4. **Coverage**: Minimum coverage thresholds

## Writing New Tests

### Unit Test Template
```python
"""
Unit tests for [Module Name]
"""

import pytest
from unittest.mock import AsyncMock, patch
from src.ollama_mcp.module import ClassName


class TestClassName:
    """Test ClassName functionality."""

    @pytest.fixture
    def instance(self):
        """Create instance for testing."""
        return ClassName()

    @pytest.mark.asyncio
    async def test_success_case(self, instance):
        """Test successful operation."""
        # Arrange
        # Act
        result = await instance.method()
        # Assert
        assert result["success"] is True

    @pytest.mark.asyncio
    async def test_error_case(self, instance):
        """Test error handling."""
        # Arrange
        with patch('module.dependency', side_effect=Exception("Error")):
            # Act
            result = await instance.method()
            # Assert
            assert result["success"] is False
            assert "error" in result
```

### Integration Test Template
```python
"""
Integration tests for [Feature]
"""

import pytest
from src.ollama_mcp.module import ClassName


@pytest.mark.integration
class TestFeatureIntegration:
    """Integration tests for feature."""

    @pytest.fixture(autouse=True)
    async def setup(self):
        """Setup for integration tests."""
        self.instance = ClassName()

    @pytest.mark.asyncio
    async def test_real_workflow(self):
        """Test complete workflow."""
        result = await self.instance.complete_workflow()
        assert result["success"] is True
```

## Troubleshooting

### Common Issues

1. **Import Errors**: Ensure `src/` is in Python path
2. **Async Issues**: Use `@pytest.mark.asyncio` for async tests
3. **Mock Issues**: Import mocks correctly and use proper patching
4. **Coverage Issues**: Ensure all code paths are tested

### Debugging Tests
```bash
# Run with verbose output
pytest -v -s

# Run single test with debugger
pytest -s --pdb tests/unit/test_client.py::test_specific_method

# Run with coverage and show missing lines
pytest --cov=src/ollama_mcp --cov-report=term-missing
```

## Best Practices

1. **Test Naming**: Use descriptive test names that explain the scenario
2. **Arrange-Act-Assert**: Structure tests clearly
3. **Mock External Dependencies**: Don't rely on external services in unit tests
4. **Test Error Conditions**: Always test failure scenarios
5. **Use Fixtures**: Reuse common test data and setup
6. **Keep Tests Fast**: Unit tests should run quickly
7. **Maintain Coverage**: Add tests for new code paths
8. **Document Complex Tests**: Add comments for complex test logic

## Contributing

When adding new features:

1. Write unit tests for the new functionality
2. Add integration tests for user workflows
3. Ensure all error conditions are tested
4. Update this README if adding new test patterns
5. Run the full test suite before submitting 