#!/usr/bin/env python3
"""
Simple test server for Ollama MCP
This bypasses the complex imports and tests basic functionality
"""

import asyncio
import logging
import sys
from typing import Any, Dict, List

# Add path for imports
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Simple configuration
OLLAMA_HOST = "http://localhost:11434"

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


class SimpleOllamaMCPServer:
    """Simple MCP server for Ollama management"""
    
    def __init__(self):
        self.server = Server("simple-ollama-mcp-server")
        self._register_handlers()
        logger.info("Simple Ollama MCP Server initialized")
    
    def _register_handlers(self):
        """Register basic MCP handlers"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            """Return available tools"""
            return [
                Tool(
                    name="health_check",
                    description="Check if Ollama server is running",
                    inputSchema={
                        "type": "object",
                        "properties": {},
                        "required": []
                    }
                ),
                Tool(
                    name="list_models",
                    description="List available Ollama models",
                    inputSchema={
                        "type": "object", 
                        "properties": {},
                        "required": []
                    }
                )
            ]
        
        @self.server.call_tool()
        async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
            """Handle tool calls"""
            try:
                if name == "health_check":
                    return await self._handle_health_check()
                elif name == "list_models":
                    return await self._handle_list_models()
                else:
                    return [TextContent(
                        type="text",
                        text=f"Unknown tool: {name}"
                    )]
            except Exception as e:
                logger.error(f"Error in tool {name}: {e}")
                return [TextContent(
                    type="text",
                    text=f"Error executing {name}: {str(e)}"
                )]
    
    async def _handle_health_check(self) -> List[TextContent]:
        """Simple health check"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OLLAMA_HOST}/api/tags", timeout=5.0)
                if response.status_code == 200:
                    data = response.json()
                    models_count = len(data.get("models", []))
                    result = {
                        "status": "healthy",
                        "host": OLLAMA_HOST,
                        "models_count": models_count,
                        "message": "Ollama server is running"
                    }
                else:
                    result = {
                        "status": "unhealthy",
                        "host": OLLAMA_HOST,
                        "error": f"HTTP {response.status_code}",
                        "message": "Ollama server responded with error"
                    }
        except Exception as e:
            result = {
                "status": "unhealthy",
                "host": OLLAMA_HOST,
                "error": str(e),
                "message": "Cannot connect to Ollama server"
            }
        
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def _handle_list_models(self) -> List[TextContent]:
        """List available models"""
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{OLLAMA_HOST}/api/tags", timeout=10.0)
                if response.status_code == 200:
                    data = response.json()
                    models = data.get("models", [])
                    result = {
                        "success": True,
                        "models": [
                            {
                                "name": model.get("name", ""),
                                "size": model.get("size", 0),
                                "modified": model.get("modified_at", "")
                            }
                            for model in models
                        ],
                        "count": len(models)
                    }
                else:
                    result = {
                        "success": False,
                        "error": f"HTTP {response.status_code}",
                        "models": []
                    }
        except Exception as e:
            result = {
                "success": False,
                "error": str(e),
                "models": []
            }
        
        import json
        return [TextContent(type="text", text=json.dumps(result, indent=2))]
    
    async def run(self):
        """Run the MCP server"""
        try:
            logger.info("Starting Simple Ollama MCP Server...")
            
            # Start MCP stdio server
            async with stdio_server() as (read_stream, write_stream):
                await self.server.run(
                    read_stream,
                    write_stream,
                    self.server.create_initialization_options()
                )
        except Exception as e:
            logger.error(f"Server error: {e}")
            raise


def main():
    """Main entry point"""
    try:
        server = SimpleOllamaMCPServer()
        asyncio.run(server.run())
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
