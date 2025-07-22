# Ollama MCP Server

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![MCP Compatible](https://img.shields.io/badge/MCP-Compatible-green.svg)](https://modelcontextprotocol.io/)
[![Pydantic v2](https://img.shields.io/badge/Pydantic-v2.0+-green.svg)](https://docs.pydantic.dev/)
[![Status: Production Ready](https://img.shields.io/badge/Status-Production%20Ready-brightgreen.svg)](https://github.com/paolodalprato/ollama-mcp-server)

A comprehensive **Model Context Protocol (MCP) server** for Ollama management built on modern Python architecture with Pydantic v2, full async support, and enterprise-grade reliability.

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Quick Start](#-quick-start)
- [Installation](#-installation)
- [Configuration](#️-configuration)
- [Usage](#-usage)
- [Available Tools](#available-tools)
- [Client Setup](#-client-setup)
- [Development](#️-development)
- [Troubleshooting](#troubleshooting)
- [Contributing](#-contributing)
- [License](#-license)

## 🎯 Overview

Ollama MCP Server provides a complete interface for managing Ollama through MCP-compatible clients like Claude Desktop. It offers 11 powerful tools for model management, server control, and system analysis.

### Key Benefits

- **🚀 Zero Dependencies**: Self-contained with no external MCP servers required
- **🛡️ Enterprise-Grade**: Professional error handling with actionable troubleshooting
- **🌐 Cross-Platform**: Windows, Linux, macOS with automatic platform detection
- **⚡ Complete Management**: Download, chat, monitor, and optimize your Ollama setup

## ✨ Features

### 🔧 Core Capabilities

- **Model Management**: Download, remove, list, and search models
- **Direct Chat**: Communicate with local models through natural language
- **Server Control**: Start, monitor, and troubleshoot Ollama server
- **System Analysis**: Hardware compatibility assessment and resource monitoring

### 🎛️ Advanced Features

- **AI-Powered Recommendations**: Get model suggestions based on your needs
- **Progress Tracking**: Monitor downloads with real-time progress indicators
- **Multi-GPU Support**: NVIDIA, AMD, Intel, and Apple Silicon detection
- **Intelligent Fallbacks**: Automatic model selection and error recovery

## 🚀 Quick Start

### Prerequisites

- **Python 3.8+**
- **Ollama** installed and accessible
- **MCP-compatible client** (Claude Desktop, etc.)

### 1. Install Ollama MCP Server

```bash
# Clone the repository
git clone https://github.com/lohbrandt/ollama-mcp-server.git
cd ollama-mcp-server

# Install in development mode
pip install -e ".[dev]"
```

### 2. Configure Your MCP Client

Add to your MCP client configuration (e.g., Claude Desktop `config.json`):

```json
{
  "mcpServers": {
    "ollama": {
      "command": "ollama-mcp-server",
      "args": [],
      "env": {
        "OLLAMA_HOST": "localhost",
        "OLLAMA_PORT": "11434",
        "OLLAMA_TIMEOUT": "30"
      }
    }
  }
}
```

### 3. Start Using

Restart your MCP client and start using natural language commands:

- *"List my installed Ollama models"*
- *"Download qwen2.5-coder for coding tasks"*
- *"Chat with llama3.2: explain machine learning"*
- *"Check if Ollama is running properly"*

## 📦 Installation

### Standard Installation

```bash
# Clone and install
git clone https://github.com/lohbrandt/ollama-mcp-server.git
cd ollama-mcp-server
pip install -e .
```

### Development Installation

```bash
# Install with development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Code formatting
black src/
isort src/
```

### Verify Installation

```bash
# Test the server
ollama-mcp-server --help

# Test MCP protocol
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | ollama-mcp-server
```

## ⚙️ Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_HOST` | `localhost` | Ollama server host |
| `OLLAMA_PORT` | `11434` | Ollama server port |
| `OLLAMA_TIMEOUT` | `30` | Request timeout in seconds |

### Advanced Configuration

```bash
# Custom host and port
export OLLAMA_HOST="192.168.1.100"
export OLLAMA_PORT="8080"

# Extended timeout for large models
export OLLAMA_TIMEOUT="120"
```

### Platform-Specific Notes

- **Windows**: Supports Program Files and AppData detection
- **Linux**: XDG configuration support with package manager integration
- **macOS**: Homebrew detection with Apple Silicon GPU support

## 💬 Usage

### How It Works

Ollama MCP Server works through your MCP client - you interact using **natural language**, and the client automatically calls the appropriate tools.

### Basic Commands

#### Model Management

```
"Show me my installed models"
"Download llama3.2 for general tasks"
"Remove the old mistral model"
"Search for coding-focused models"
```

#### Chat and Interaction

```
"Chat with qwen2.5: write a Python function to sort a list"
"Use deepseek-coder to debug this code: [paste code]"
"Ask phi3.5 to explain quantum computing"
```

#### System Operations

```
"Check if Ollama is running"
"Start the Ollama server"
"Analyze my system for AI model compatibility"
"Recommend a model for creative writing"
```

### Real-World Examples

#### Complete Workflow Setup

> I need to set up local AI for coding. Check my system, recommend a good coding model, download it, and test it.

This automatically triggers:

1. `system_resource_check` - Verify hardware capability
2. `suggest_models` - Get coding model recommendations
3. `download_model` - Download the recommended model
4. `local_llm_chat` - Test with a coding question

#### Model Management Session

> Show me what models I have, see what new coding models are available, and clean up old models.

Triggers:

1. `list_local_models` - Current inventory
2. `search_available_models` - Browse new options
3. `remove_model` - Cleanup unwanted models

## 🛠️ Available Tools

### Base Tools (4)

| Tool | Description | Use Case |
|------|-------------|----------|
| `list_local_models` | List installed models with details | Inventory management |
| `local_llm_chat` | Chat directly with local models | AI interaction |
| `ollama_health_check` | Comprehensive server diagnostics | Troubleshooting |
| `system_resource_check` | Hardware compatibility analysis | System assessment |

### Advanced Tools (7)

| Tool | Description | Use Case |
|------|-------------|----------|
| `suggest_models` | AI-powered model recommendations | Model selection |
| `download_model` | Download models with progress tracking | Model acquisition |
| `check_download_progress` | Monitor download progress | Progress tracking |
| `remove_model` | Safely remove models from storage | Storage management |
| `search_available_models` | Search Ollama Hub by category | Model discovery |
| `start_ollama_server` | Start Ollama server | Server management |
| `select_chat_model` | Interactive model selection | Model switching |

## 🔧 Client Setup

### Claude Desktop

```json
{
  "mcpServers": {
    "ollama": {
      "command": "ollama-mcp-server",
      "args": [],
      "env": {
        "OLLAMA_HOST": "localhost",
        "OLLAMA_PORT": "11434"
      }
    }
  }
}
```

### Other MCP Clients

```json
{
  "servers": {
    "ollama-mcp": {
      "command": "ollama-mcp-server",
      "cwd": "/path/to/ollama-mcp-server"
    }
  }
}
```

### Testing Your Setup

```bash
# Test server initialization
echo '{"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "test", "version": "1.0.0"}}}' | ollama-mcp-server

# List available tools
echo '{"jsonrpc": "2.0", "id": 2, "method": "tools/list"}' | ollama-mcp-server
```

## 🏗️ Development

### Project Structure

```
ollama-mcp-server/
├── src/ollama_mcp/
│   ├── server.py              # Main MCP server implementation
│   ├── client.py              # Ollama client interface
│   ├── tools/
│   │   ├── base_tools.py      # Essential 4 tools
│   │   └── advanced_tools.py  # Extended 7 tools
│   ├── config.py              # Configuration management
│   ├── model_manager.py       # Model operations
│   ├── job_manager.py         # Background task management
│   └── hardware_checker.py    # System analysis
├── tests/                     # Test suite
├── docs/                      # Documentation
└── pyproject.toml            # Project configuration
```

### Development Commands

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run with coverage
pytest --cov=src/ollama_mcp

# Code formatting
black src/
isort src/

# Type checking
mypy src/

# Linting
flake8 src/
```

### Testing

```bash
# Run all tests
pytest

# Run specific test categories
pytest tests/unit/
pytest tests/integration/

# Run with verbose output
pytest -v

# Run with coverage report
pytest --cov=src/ollama_mcp --cov-report=html
```

#### Ollama Not Found

### Common Issues

#### Ollama Not Found

```bash
# Verify Ollama installation
ollama --version

# Check PATH configuration
which ollama  # Linux/macOS
where ollama  # Windows
```

#### Server Connection Issues

```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# Start Ollama manually
ollama serve
```

#### Permission Issues

- **Windows**: Run as Administrator if needed
- **Linux/macOS**: Check user permissions for service management

### Platform-Specific Issues

#### Windows

- Ensure Ollama is installed in Program Files or AppData
- Check Windows Defender/firewall settings
- Run PowerShell as Administrator if needed

#### Linux

- Verify Ollama service is running: `systemctl status ollama`
- Check user permissions for service management
- Ensure proper PATH configuration

#### macOS

- Verify Homebrew installation if using Homebrew
- Check Apple Silicon compatibility for GPU detection
- Ensure proper permissions for system monitoring

## Troubleshooting

If you encounter issues:

1. **Check the logs**: Look for error messages in your MCP client
2. **Verify Ollama**: Ensure Ollama is running and accessible
3. **Test connectivity**: Use `curl http://localhost:11434/api/tags`
4. **Report issues**: Create a GitHub issue with:
   - Operating system and version
   - Python version
   - Ollama version
   - Complete error output

## 🤝 Contributing

We welcome contributions! Here's how you can help:

### Areas Needing Help

- **Platform Testing**: Different OS and hardware configurations
- **GPU Support**: Additional vendor-specific detection
- **Performance Optimization**: Startup time and resource usage
- **Documentation**: Usage examples and integration guides
- **Testing**: Edge cases and error condition validation

### Development Setup

```bash
# Fork and clone
git clone https://github.com/your-username/ollama-mcp-server.git
cd ollama-mcp-server

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or
.venv\Scripts\activate     # Windows

# Install dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Make your changes and test
# Submit a pull request
```

### Testing Needs

- **Linux**: Ubuntu, Fedora, Arch with various GPU configurations
- **macOS**: Intel and Apple Silicon Macs
- **GPU Vendors**: AMD ROCm, Intel Arc, Apple unified memory
- **Edge Cases**: Different Python versions, various Ollama installations

## 📊 Performance

### Typical Response Times

| Operation | Time | Notes |
|-----------|------|-------|
| Health Check | <500ms | Server status verification |
| Model List | <1s | Inventory retrieval |
| Server Start | 1-15s | Hardware dependent |
| Model Chat | 2-30s | Model and prompt dependent |
| Model Download | Variable | Network and model size dependent |

### Resource Usage

- **Memory**: <50MB for MCP server process
- **CPU**: Minimal when idle, scales with operations
- **Storage**: Configuration files and logs only

## 🔐 Security

- **Local Processing**: All operations happen locally
- **No Data Collection**: No telemetry or data collection
- **MIT License**: Open source and auditable
- **Minimal Permissions**: Only requires Ollama access

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

### Special Thanks

**This project is built upon the excellent foundation provided by [Paolo Dalprato's Ollama MCP Server](https://github.com/paolodalprato/ollama-mcp-server).**

We are deeply grateful to Paolo for:

- 🏗️ **Creating the original architecture** - The comprehensive MCP server design with 11 powerful tools
- 💡 **Innovative approach** - Zero external dependencies and self-contained design philosophy  
- 🔧 **Cross-platform foundation** - Windows, Linux, macOS compatibility framework
- 🚀 **Enterprise-grade patterns** - Professional error handling and robust system design
- 📖 **Excellent documentation** - Clear usage examples and thorough troubleshooting guides
- 🤝 **Open source contribution** - Making this powerful tool available to the community

Paolo's original work provided the solid foundation that made this enhanced version possible. The current repository builds upon his vision with Pydantic v2 migration, additional features, and continued development.

### Additional Thanks

- **Ollama Team**: For the excellent local AI platform
- **MCP Project**: For the Model Context Protocol specification
- **Claude Desktop**: For MCP client implementation
- **Community**: For testing, feedback, and contributions

## 📞 Support

- **Bug Reports**: [GitHub Issues](https://github.com/lohbrandt/ollama-mcp-server/issues)
- **Feature Requests**: [GitHub Issues](https://github.com/lohbrandt/ollama-mcp-server/issues)
- **Community Discussion**: [GitHub Discussions](https://github.com/lohbrandt/ollama-mcp-server/discussions)

---

**Status**: Beta on Windows, Other Platforms Need Testing  
**Testing**: Windows 11 + RTX 4090 validated, Linux/macOS require community validation  
**License**: MIT  
**Dependencies**: Zero external MCP servers required
