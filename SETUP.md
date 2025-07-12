# Ollama MCP Server Setup

This directory contains the Ollama MCP Server installation and management scripts.

## Installation Complete

✅ **Ollama** - Installed via Homebrew and running as a service  
✅ **Ollama MCP Server** - Installed in development mode  
✅ **Service Management** - Automated startup/shutdown scripts created  

## Service Management

### Automatic Service Management (Recommended)

Use the `manage-service` script for system-level service management:

```bash
./manage-service install    # Install and start the service
./manage-service start      # Start the service  
./manage-service stop       # Stop the service
./manage-service restart    # Restart the service
./manage-service status     # Check service status
./manage-service logs       # View service logs
./manage-service load       # Load service (auto-start on login)
./manage-service unload     # Unload service
```

### Manual Service Management

Use the `ollama-mcp` script for manual control:

```bash
./ollama-mcp start          # Start the server manually
./ollama-mcp stop           # Stop the server
./ollama-mcp restart        # Restart the server
./ollama-mcp status         # Check server status
./ollama-mcp logs           # View server logs
```

## Service Details

- **Service Label**: `com.ollama.mcpserver`
- **Auto-start**: Enabled (starts on login)
- **Log Files**: 
  - Standard output: `/tmp/ollama_mcp_server.log`
  - Standard error: `/tmp/ollama_mcp_server_error.log`
- **PID File**: `/tmp/ollama_mcp_server.pid` (manual mode)

## Dependencies

- **Ollama**: Running on system via Homebrew
- **Python**: MCP server requires Python 3.8+
- **Modules**: All dependencies installed via pip

## Troubleshooting

### Check Service Status
```bash
./manage-service status
```

### View Logs
```bash
./manage-service logs
# or
tail -f /tmp/ollama_mcp_server.log
```

### Restart Everything
```bash
./manage-service restart
```

### Check if Ollama is Running
```bash
brew services list | grep ollama
```

## Directory Structure

```
/Volumes/dev/repositories/serve/ollama-mcp-server/
├── ollama-mcp          # Manual service management script
├── manage-service      # Automatic service management script
├── SETUP.md           # This file
└── src/               # Source code
```

## Notes

The service is configured to:
- Start automatically on login
- Restart automatically if it crashes
- Log all output to `/tmp/ollama_mcp_server.log`
- Run in the background as a daemon
