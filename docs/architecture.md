# Ollama MCP Server Architecture

## Overview

The Ollama MCP Server is a self-contained Model Context Protocol (MCP) server designed for comprehensive Ollama management. This document outlines the architectural decisions, component design, and system interactions.

## Design Principles

### 1. Self-Contained Architecture
- **Zero External Dependencies**: No external MCP servers required
- **Internal Implementation**: All MCP functionality implemented internally
- **Professional Grade**: Enterprise-quality error handling and logging
- **MIT License**: All code properly licensed and compatible

### 2. Resilient Design
- **Offline Start**: Server starts successfully even when Ollama is offline
- **Graceful Degradation**: Non-critical features fail gracefully
- **Comprehensive Error Handling**: Specific error types with actionable guidance
- **Resource Cleanup**: Proper async resource management

### 3. Cross-Platform First
- **Universal Compatibility**: Windows, Linux, macOS support
- **Platform Detection**: Automatic platform-specific behavior
- **Path Handling**: Consistent cross-platform file operations
- **Command Execution**: Platform-aware system command handling

## System Architecture

### High-Level Components

```
┌─────────────────────────────────────────────────────────────┐
│                    MCP Client                               │
│              (Claude Desktop, etc.)                        │
└─────────────────────────┬───────────────────────────────────┘
                          │ stdio/JSON-RPC
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Ollama MCP Server                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │   Base Tools    │  │ Advanced Tools  │  │   Server    │  │
│  │                 │  │                 │  │  Manager    │  │
│  │ • list_models   │  │ • download_model│  │             │  │
│  │ • chat         │  │ • suggest_models│  │             │  │
│  │ • health_check  │  │ • start_server  │  │             │  │
│  │ • system_check  │  │ • progress_track│  │             │  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
│                          │                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────┐  │
│  │  Ollama Client  │  │  Job Manager    │  │  Hardware   │  │
│  │                 │  │                 │  │  Checker    │  │
│  │ • HTTP Client   │  │ • Progress Track│  │             │  │
│  │ • Error Handling│  │ • Async Jobs    │  │ • GPU Detect│  │
│  │ • Timeouts      │  │ • Cancellation  │  │ • CPU/Memory│  │
│  └─────────────────┘  └─────────────────┘  └─────────────┘  │
└─────────────────────────┬───────────────────────────────────┘
                          │ HTTP/REST API
                          │
┌─────────────────────────▼───────────────────────────────────┐
│                  Ollama Server                              │
│            (Local AI Model Server)                         │
└─────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

#### 1. MCP Server Core (`server.py`)
- **Server Registration**: MCP protocol handler registration
- **Tool Routing**: Route tool calls to appropriate handlers
- **Initialization**: Resilient startup with offline Ollama support
- **stdio Management**: Handle MCP client communication

#### 2. Ollama Client (`client.py`)
- **HTTP Communication**: Async HTTP client for Ollama API
- **Error Classification**: Intelligent error categorization
- **Connection Management**: Resilient connection handling
- **Response Parsing**: Standardized response processing

#### 3. Tool Modules (`tools/`)
- **Base Tools**: Essential 4 tools for core functionality
- **Advanced Tools**: Extended 7 tools for advanced features
- **Tool Definition**: JSON schema definitions for MCP
- **Handler Implementation**: Async tool execution logic

#### 4. System Management
- **Hardware Checker**: Cross-platform GPU/CPU detection
- **Job Manager**: Progress tracking for long-running operations
- **Server Manager**: Ollama server lifecycle management
- **Configuration**: Environment and platform-specific settings

## Data Flow

### 1. Tool Execution Flow
```
MCP Client Request
       ↓
JSON-RPC via stdio
       ↓
MCP Server receives call_tool
       ↓
Route to appropriate tool handler
       ↓
Parameter validation
       ↓
Ollama Client API call
       ↓
Response processing
       ↓
JSON formatting
       ↓
TextContent response
       ↓
Back to MCP Client
```

### 2. Error Handling Flow
```
Exception occurs
       ↓
Classify error type
       ↓
Generate user-friendly message
       ↓
Add troubleshooting steps
       ↓
Log technical details
       ↓
Return structured error response
```

## Technology Stack

### Core Technologies
- **Python 3.8+**: Primary development language
- **asyncio**: Async/await for non-blocking operations
- **MCP SDK**: Model Context Protocol implementation
- **httpx**: Modern async HTTP client
- **psutil**: Cross-platform system information

### Development Tools
- **pytest**: Testing framework with async support
- **black**: Code formatting (88 character line length)
- **mypy**: Type checking for code quality
- **isort**: Import organization
- **flake8**: Code linting

## Key Architectural Decisions

### 1. Async-First Design
**Decision**: Use async/await throughout the codebase
**Rationale**: 
- MCP protocol benefits from non-blocking operations
- Ollama API calls can be slow (model loading)
- Better resource utilization for concurrent requests
- Future-proof for streaming responses

### 2. Self-Contained Implementation
**Decision**: Implement all MCP functionality internally
**Rationale**:
- No external server dependencies
- Easier deployment and maintenance
- Better control over error handling
- Reduced security surface area

### 3. Resilient Startup
**Decision**: Start server even when Ollama is offline
**Rationale**:
- Better user experience (server always available)
- Diagnostic tools work even when Ollama is down
- Easier troubleshooting workflow
- More robust deployment scenarios

### 4. Tool Categorization
**Decision**: Separate base tools from advanced tools
**Rationale**:
- Clear separation of concerns
- Easier maintenance and testing
- Logical grouping for users
- Enables selective feature loading

## Performance Considerations

### 1. Connection Management
- **Connection Pooling**: httpx client with connection limits
- **Timeout Configuration**: Appropriate timeouts for different operations
- **Resource Cleanup**: Proper async context manager usage
- **Memory Management**: Efficient handling of large responses

### 2. Error Handling Performance
- **Early Validation**: Validate parameters before expensive operations
- **Caching**: Cache system information to avoid repeated detection
- **Lazy Loading**: Load components only when needed
- **Graceful Degradation**: Continue operation when non-critical features fail

## Security Considerations

### 1. Local Processing
- **No Cloud Dependencies**: All processing happens locally
- **Private Data**: User data never leaves the local machine
- **Secure Communication**: stdio-based communication with MCP client
- **No Network Exposure**: Server doesn't expose network ports

### 2. Input Validation
- **Parameter Validation**: Strict validation of all tool parameters
- **Type Checking**: Runtime type validation for safety
- **Command Injection Prevention**: Safe subprocess execution
- **Path Traversal Prevention**: Secure file path handling

## Testing Strategy

### 1. Test Categories
- **Unit Tests**: Individual function and class testing
- **Integration Tests**: Component interaction testing
- **End-to-End Tests**: Complete workflow testing
- **Cross-Platform Tests**: Platform-specific behavior testing

### 2. Testing Architecture
- **Mock Dependencies**: Mock external services for unit tests
- **Async Testing**: Proper async test patterns
- **Error Scenario Testing**: Comprehensive error condition testing
- **Performance Testing**: Resource usage and timing tests

## Deployment Architecture

### 1. Installation Methods
- **pip install**: Standard Python package installation
- **Git clone**: Development and custom installations
- **Docker**: Containerized deployment (future consideration)
- **Executable**: Standalone executable (future consideration)

### 2. Configuration Management
- **Environment Variables**: Runtime configuration
- **Platform Detection**: Automatic platform-specific settings
- **Default Values**: Sensible defaults for all configurations
- **Validation**: Configuration validation at startup

## Future Architecture Considerations

### 1. Scalability
- **Multiple Ollama Instances**: Support for multiple Ollama servers
- **Load Balancing**: Distribute requests across instances
- **Caching Layer**: Response caching for better performance
- **Streaming Support**: Real-time response streaming

### 2. Extension Points
- **Plugin Architecture**: Support for custom tools
- **Event System**: Extensible event handling
- **Custom Protocols**: Support for additional AI server protocols
- **Monitoring Integration**: Metrics and observability hooks

## Maintenance and Evolution

### 1. Code Quality
- **Continuous Integration**: Automated testing on multiple platforms
- **Code Coverage**: Maintain high test coverage
- **Documentation**: Keep architecture documentation current
- **Refactoring**: Regular code quality improvements

### 2. Dependency Management
- **Minimal Dependencies**: Keep dependency count low
- **Security Updates**: Regular security vulnerability scanning
- **Compatibility**: Maintain backward compatibility
- **Version Management**: Careful version management strategy 