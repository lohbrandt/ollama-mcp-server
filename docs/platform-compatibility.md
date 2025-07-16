# Platform Compatibility Guide

## Overview

The Ollama MCP Server is designed for universal compatibility across Windows, Linux, and macOS platforms. This guide details platform-specific considerations, installation procedures, and troubleshooting steps.

## Supported Platforms

### ✅ Fully Supported
- **Windows 10/11** (x64, ARM64)
- **macOS 10.15+** (Intel and Apple Silicon)
- **Linux** (Ubuntu 18.04+, CentOS 7+, Debian 10+)

### ⚠️ Partially Tested
- **Windows Server 2019/2022**
- **Alpine Linux**
- **Arch Linux**
- **Fedora/RHEL 8+**

## Platform-Specific Features

### Windows
- **GPU Detection**: NVIDIA (nvidia-smi), AMD (wmic), Intel (wmic)
- **Installation Paths**: Program Files, AppData
- **Executable**: `ollama.exe`
- **Configuration**: `%APPDATA%\ollama\`

### macOS
- **GPU Detection**: Apple Silicon (system_profiler), discrete GPUs
- **Installation Paths**: `/usr/local/bin`, `/opt/homebrew/bin`
- **Executable**: `ollama`
- **Configuration**: `~/.ollama/`

### Linux
- **GPU Detection**: NVIDIA (nvidia-smi), AMD (lspci), Intel (lspci)
- **Installation Paths**: `/usr/local/bin`, `/usr/bin`, `~/.local/bin`
- **Executable**: `ollama`
- **Configuration**: `~/.ollama/`

## Installation Instructions

### Windows

#### Method 1: Download Installer
1. Visit https://ollama.com/download
2. Download Windows installer
3. Run installer as Administrator
4. Verify installation: `ollama --version`

#### Method 2: Package Manager
```powershell
# Using winget
winget install ollama

# Using chocolatey
choco install ollama
```

#### Python Package
```powershell
# Install Python 3.8+
python -m pip install ollama-mcp-server

# Or from source
git clone https://github.com/paolodalprato/ollama-mcp-server.git
cd ollama-mcp-server
python -m pip install -e .
```

### macOS

#### Method 1: Homebrew (Recommended)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Ollama
brew install ollama

# Install Python package
pip install ollama-mcp-server
```

#### Method 2: Download Installer
1. Visit https://ollama.com/download
2. Download macOS installer
3. Follow installation wizard
4. Verify installation: `ollama --version`

#### Apple Silicon Considerations
- Use native ARM64 versions when available
- Some Python packages may need Rosetta 2 compatibility
- GPU detection includes unified memory architecture
- Support for M1, M2, M3, and M4 chips
- Automatic detection of unified memory size

### Linux

#### Method 1: Install Script (Recommended)
```bash
# Install Ollama
curl -fsSL https://ollama.com/install.sh | sh

# Install Python package
pip install ollama-mcp-server

# Or using pip3
pip3 install ollama-mcp-server
```

#### Method 2: Package Managers
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3-pip
pip3 install ollama-mcp-server

# CentOS/RHEL/Fedora
sudo yum install python3-pip
pip3 install ollama-mcp-server

# Arch Linux
sudo pacman -S python-pip
pip install ollama-mcp-server
```

## Configuration

### Environment Variables

#### Cross-Platform Variables
```bash
# Ollama server URL
export OLLAMA_HOST=http://localhost:11434

# Custom data directory
export OLLAMA_DATA_DIR=/path/to/data

# Custom models directory
export OLLAMA_MODELS_DIR=/path/to/models
```

#### Windows-Specific
```powershell
# Set in PowerShell
$env:OLLAMA_HOST = "http://localhost:11434"

# Set permanently
[Environment]::SetEnvironmentVariable("OLLAMA_HOST", "http://localhost:11434", "User")
```

#### macOS/Linux-Specific
```bash
# Add to shell profile (.bashrc, .zshrc, etc.)
echo 'export OLLAMA_HOST=http://localhost:11434' >> ~/.bashrc
source ~/.bashrc
```

### MCP Client Configuration

#### Claude Desktop (All Platforms)
```json
{
  "mcpServers": {
    "ollama-mcp": {
      "command": "python",
      "args": [
        "/path/to/ollama-mcp-server/src/ollama_mcp/server.py"
      ],
      "env": {}
    }
  }
}
```

#### Platform-Specific Paths
```json
// Windows
{
  "mcpServers": {
    "ollama-mcp": {
      "command": "python",
      "args": [
        "C:\\Users\\YourName\\ollama-mcp-server\\src\\ollama_mcp\\server.py"
      ]
    }
  }
}

// macOS/Linux
{
  "mcpServers": {
    "ollama-mcp": {
      "command": "python",
      "args": [
        "/Users/YourName/ollama-mcp-server/src/ollama_mcp/server.py"
      ]
    }
  }
}
```

## GPU Support

### NVIDIA GPUs
- **Requirements**: NVIDIA drivers, CUDA toolkit (optional)
- **Detection**: nvidia-smi command
- **Support**: All platforms
- **Memory**: Automatic VRAM detection

### AMD GPUs
- **Windows**: WMI query detection
- **Linux**: lspci and ROCm detection
- **macOS**: Limited support (discrete GPUs only)
- **Memory**: Best-effort detection

### Intel GPUs
- **Windows**: WMI query detection
- **Linux**: lspci detection
- **macOS**: Limited support
- **Memory**: Integrated graphics detection

### Apple Silicon (M1/M2/M3)
- **Detection**: system_profiler command
- **Memory**: Unified memory architecture
- **Performance**: Optimized for Apple Silicon
- **Support**: macOS only

## Troubleshooting

### Common Issues

#### 1. Ollama Not Found
**Symptoms**: "Ollama executable not found"

**Windows Solutions**:
```powershell
# Check PATH
echo $env:PATH

# Find Ollama installation
where ollama

# Add to PATH if needed
$env:PATH += ";C:\Program Files\Ollama"
```

**macOS/Linux Solutions**:
```bash
# Check PATH
echo $PATH

# Find Ollama installation
which ollama

# Add to PATH if needed
export PATH="/usr/local/bin:$PATH"
```

#### 2. Permission Errors
**Windows**: Run as Administrator
**macOS**: Check executable permissions
**Linux**: Use `sudo` for system-wide installation

#### 3. Python Path Issues
```bash
# Check Python installation
python --version
python3 --version

# Check pip installation
pip --version
pip3 --version

# Install in user directory
pip install --user ollama-mcp-server
```

#### 4. GPU Detection Failures
**NVIDIA**: Install nvidia-smi
**AMD**: Install appropriate drivers
**Intel**: Update graphics drivers
**Apple Silicon**: Update macOS

### Platform-Specific Troubleshooting

#### Windows
```powershell
# Check Windows version
systeminfo | findstr /B /C:"OS Name" /C:"OS Version"

# Check .NET Framework
reg query "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\NET Framework Setup\NDP\v4\Full\" /v Release

# Check Python installation
py -0  # List Python versions
```

#### macOS
```bash
# Check macOS version
sw_vers

# Check Xcode Command Line Tools
xcode-select --print-path

# Check Homebrew
brew doctor

# Check Python installation
python3 --version
which python3

# Check Apple Silicon (if applicable)
uname -m
sysctl -n machdep.cpu.brand_string

# Check unified memory
sysctl -n hw.memsize
```

#### Linux
```bash
# Check distribution
cat /etc/os-release

# Check Python installation
python3 --version
python3 -m pip --version

# Check system dependencies
ldd --version
```

## Performance Optimization

### System Requirements

#### Minimum Requirements
- **CPU**: 2+ cores
- **RAM**: 4GB
- **Storage**: 2GB free space
- **Network**: Internet connection for model downloads

#### Recommended Requirements
- **CPU**: 4+ cores
- **RAM**: 8GB+
- **Storage**: 10GB+ free space
- **GPU**: Dedicated GPU with 4GB+ VRAM

### Platform-Specific Optimizations

#### Windows
- Enable Windows Subsystem for Linux (WSL2) for better performance
- Use Windows Terminal for better console experience
- Configure Windows Defender exclusions for Ollama directory

#### macOS
- Use Homebrew for package management
- Enable Rosetta 2 for Intel compatibility on Apple Silicon
- Configure Time Machine exclusions for model storage

#### Linux
- Use package managers for system dependencies
- Configure systemd services for automatic startup
- Optimize filesystem for large model files

## Testing

### Automated Testing
```bash
# Run platform-specific tests
pytest tests/platform/

# Run cross-platform tests
pytest tests/integration/

# Run GPU detection tests
pytest tests/unit/test_hardware_checker.py
```

### Manual Testing
```bash
# Test Ollama connectivity
curl http://localhost:11434/api/tags

# Test MCP server
python src/ollama_mcp/server.py

# Test specific tools
python -c "
from src.ollama_mcp.tools.base_tools import handle_base_tool
print('Tools available')
"
```

## Development Notes

### Cross-Platform Development
- Use `pathlib.Path` for file operations
- Handle platform-specific executable names
- Test on multiple platforms before release
- Use GitHub Actions for CI/CD

### Platform Detection
```python
import platform

system = platform.system()
if system == "Windows":
    # Windows-specific code
elif system == "Darwin":
    # macOS-specific code
else:
    # Linux/Unix-specific code
```

### Testing Matrix
- **Python Versions**: 3.8, 3.9, 3.10, 3.11, 3.12
- **Operating Systems**: Windows, macOS, Linux
- **Architectures**: x64, ARM64
- **GPU Types**: NVIDIA, AMD, Intel, Apple Silicon

## Future Compatibility

### Upcoming Features
- Docker container support
- Kubernetes deployment
- ARM64 Linux support
- Windows ARM64 support

### Deprecation Notices
- Python 3.7 support will be removed in future versions
- Windows 7/8 support is not guaranteed
- 32-bit platform support may be discontinued 