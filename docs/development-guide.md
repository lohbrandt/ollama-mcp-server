# Development Guide

## Getting Started

### Prerequisites
- Python 3.8 or higher
- Git
- Ollama installed and accessible (for integration testing)
- Code editor with Python support (VS Code, PyCharm, etc.)

### Development Environment Setup

1. **Clone the Repository**
   ```bash
   git clone https://github.com/paolodalprato/ollama-mcp-server.git
   cd ollama-mcp-server
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Development Dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

4. **Verify Installation**
   ```bash
   python -m ollama_mcp.server --help
   pytest --version
   black --version
   ```

## Development Workflow

### Code Standards

#### Formatting and Linting
```bash
# Format code
black src/ tests/
isort src/ tests/

# Check formatting
black --check src/ tests/
isort --check-only src/ tests/

# Type checking
mypy src/

# Linting
flake8 src/ tests/
```

#### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit
pre-commit install

# Run manually
pre-commit run --all-files
```

### Testing Workflow

#### Running Tests
```bash
# Run all tests
pytest

# Run specific categories
pytest -m unit
pytest -m integration
pytest -m "not slow"

# Run with coverage
pytest --cov=src/ollama_mcp --cov-report=html

# Run specific test file
pytest tests/unit/test_client.py -v
```

#### Test Development
1. Write tests before implementing features (TDD approach)
2. Use descriptive test names that explain the scenario
3. Follow the AAA pattern (Arrange, Act, Assert)
4. Mock external dependencies in unit tests
5. Test both success and failure scenarios

### Feature Development Process

#### 1. Planning Phase
- Review existing architecture and patterns
- Check if similar functionality already exists
- Plan the API and integration points
- Write or update documentation

#### 2. Implementation Phase
- Create feature branch: `git checkout -b feature/your-feature`
- Implement following established patterns
- Add comprehensive tests
- Update documentation

#### 3. Testing Phase
- Run full test suite: `pytest`
- Test manually with real Ollama server
- Test on different platforms if possible
- Check code coverage

#### 4. Review Phase
- Create pull request with detailed description
- Address review feedback
- Ensure CI passes
- Update documentation if needed

## Project Structure

### Directory Layout
```
ollama-mcp-server/
├── src/
│   └── ollama_mcp/
│       ├── __init__.py
│       ├── server.py           # Main MCP server
│       ├── client.py           # Ollama client
│       ├── config.py           # Configuration management
│       ├── tools/              # Tool implementations
│       │   ├── __init__.py
│       │   ├── base_tools.py   # Core 4 tools
│       │   └── advanced_tools.py # Extended 7 tools
│       ├── hardware_checker.py # System info detection
│       ├── job_manager.py      # Progress tracking
│       └── server_manager.py   # Server lifecycle
├── tests/
│   ├── unit/
│   ├── integration/
│   ├── fixtures/
│   └── conftest.py
├── docs/
│   ├── architecture.md
│   ├── development-guide.md
│   └── platform-compatibility.md
├── .cursor/
│   └── rules/                  # Cursor IDE rules
├── pyproject.toml
├── README.md
└── LICENSE
```

### Key Files

#### `src/ollama_mcp/server.py`
- Main MCP server implementation
- Tool registration and routing
- Server lifecycle management

#### `src/ollama_mcp/client.py`
- Ollama HTTP client wrapper
- Error handling and classification
- Response parsing and validation

#### `src/ollama_mcp/tools/`
- Tool implementations following MCP protocol
- Separated into base and advanced tools
- JSON schema definitions

## Adding New Tools

### Tool Development Template

1. **Define the Tool**
   ```python
   def create_your_tool() -> Tool:
       return Tool(
           name="your_tool_name",
           description="Clear description of what the tool does",
           inputSchema={
               "type": "object",
               "properties": {
                   "param_name": {
                       "type": "string",
                       "description": "Parameter description"
                   }
               },
               "required": ["param_name"]
           }
       )
   ```

2. **Implement the Handler**
   ```python
   async def handle_your_tool(
       arguments: Dict[str, Any], 
       client: OllamaClient
   ) -> List[TextContent]:
       try:
           # Validate parameters
           param = arguments.get("param_name")
           if not param:
               return error_response("param_name is required")
           
           # Execute tool logic
           result = await your_tool_logic(param, client)
           
           # Return successful response
           return [TextContent(
               type="text",
               text=json.dumps(result, indent=2)
           )]
       except Exception as e:
           return error_response(str(e))
   ```

3. **Add to Tool Registry**
   ```python
   # In appropriate tools module
   def get_tools() -> List[Tool]:
       return [
           # ... existing tools ...
           create_your_tool(),
       ]
   
   # In handler routing
   if name == "your_tool_name":
       return await handle_your_tool(arguments, client)
   ```

4. **Add Tests**
   ```python
   class TestYourTool:
       @pytest.mark.asyncio
       async def test_successful_execution(self):
           # Test implementation
           pass
       
       @pytest.mark.asyncio
       async def test_parameter_validation(self):
           # Test validation
           pass
       
       @pytest.mark.asyncio
       async def test_error_handling(self):
           # Test error scenarios
           pass
   ```

## Debugging

### Local Development
```bash
# Run server in development mode
python src/ollama_mcp/server.py

# Run with debug logging
PYTHONPATH=src python -m ollama_mcp.server --debug

# Test specific tool
python -c "
from src.ollama_mcp.client import OllamaClient
client = OllamaClient()
print(client.health_check())
"
```

### Common Issues

#### 1. Import Errors
- Check PYTHONPATH includes src directory
- Verify virtual environment is activated
- Check for circular imports

#### 2. Async Issues
- Ensure using `await` for async operations
- Check for blocking operations in async context
- Verify proper async context manager usage

#### 3. MCP Protocol Issues
- Validate JSON schema definitions
- Check TextContent response format
- Verify proper error handling

### Debugging Tools

#### 1. Logging
```python
import logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Use throughout code
logger.debug("Debug information")
logger.info("Normal operation")
logger.warning("Warning condition")
logger.error("Error occurred")
```

#### 2. Development Server
```python
# Use test_server.py for simplified testing
python test_server.py
```

#### 3. Manual Testing
```bash
# Test Ollama connectivity
curl http://localhost:11434/api/tags

# Test MCP server manually
echo '{"jsonrpc": "2.0", "method": "tools/list", "id": 1}' | python src/ollama_mcp/server.py
```

## CI/CD Pipeline

### GitHub Actions Workflow
- **Code Quality**: Black, isort, flake8, mypy
- **Testing**: pytest on multiple Python versions
- **Platform Testing**: Windows, Linux, macOS
- **Security**: Dependency vulnerability scanning

### Local CI Simulation
```bash
# Run full CI pipeline locally
./scripts/ci-local.sh  # If available

# Or run individual steps
black --check src/ tests/
isort --check-only src/ tests/
flake8 src/ tests/
mypy src/
pytest --cov=src/ollama_mcp
```

## Performance Optimization

### Profiling
```bash
# Profile server startup
python -m cProfile -o profile.prof src/ollama_mcp/server.py

# Analyze profile
python -c "
import pstats
p = pstats.Stats('profile.prof')
p.sort_stats('cumulative').print_stats(20)
"
```

### Memory Analysis
```python
# Use memory_profiler for memory analysis
pip install memory-profiler
python -m memory_profiler src/ollama_mcp/server.py
```

### Async Performance
```python
# Monitor async operations
import asyncio
import time

async def timed_operation():
    start = time.time()
    result = await some_async_operation()
    end = time.time()
    print(f"Operation took {end - start:.2f} seconds")
    return result
```

## Contributing Guidelines

### Code Review Checklist
- [ ] Code follows project style guidelines
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] Error handling is appropriate
- [ ] Performance impact is considered
- [ ] Cross-platform compatibility maintained

### Pull Request Process
1. Create feature branch from main
2. Implement changes with tests
3. Update documentation
4. Run full test suite
5. Create pull request with description
6. Address review feedback
7. Merge after approval

### Documentation Updates
- Update README for user-facing changes
- Update architecture docs for design changes
- Add inline code documentation
- Update API documentation

## Release Process

### Version Management
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version in pyproject.toml
- Create git tag for releases
- Update CHANGELOG.md

### Release Checklist
- [ ] All tests pass
- [ ] Documentation is current
- [ ] Version number updated
- [ ] CHANGELOG updated
- [ ] Git tag created
- [ ] Release notes prepared

## Troubleshooting

### Common Development Issues

#### 1. Environment Issues
```bash
# Reset virtual environment
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -e ".[dev]"
```

#### 2. Test Issues
```bash
# Clear pytest cache
rm -rf .pytest_cache
pytest --cache-clear

# Run specific failing test
pytest tests/unit/test_client.py::TestOllamaClient::test_health_check -v -s
```

#### 3. Import Issues
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Test imports
python -c "from src.ollama_mcp.client import OllamaClient; print('Import successful')"
```

### Getting Help
- Check existing issues on GitHub
- Review project documentation
- Run diagnostics tools
- Ask questions in discussions 