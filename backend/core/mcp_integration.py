"""
Model Context Protocol (MCP) Server Integration
Manages MCP servers, tools, and client connections for AI agents
"""

import asyncio
import json
import logging
import os
import subprocess
import uuid
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from pathlib import Path

import websockets
import httpx
from pydantic import BaseModel

logger = logging.getLogger(__name__)


@dataclass
class MCPServerConfig:
    """Configuration for an MCP server"""
    name: str
    command: str
    args: List[str]
    env: Dict[str, str]
    timeout: int = 30
    auto_restart: bool = True
    connection_type: str = "stdio"  # stdio, websocket, http


class MCPTool(BaseModel):
    """MCP tool definition"""
    name: str
    description: str
    input_schema: Dict[str, Any]
    server_name: str


class MCPServerProcess:
    """Manages an MCP server process"""
    
    def __init__(self, config: MCPServerConfig):
        self.config = config
        self.process: Optional[subprocess.Popen] = None
        self.is_running = False
        self.tools: List[MCPTool] = []
        self.websocket_url: Optional[str] = None
        self.http_url: Optional[str] = None
    
    async def start(self):
        """Start the MCP server process"""
        try:
            logger.info(f"Starting MCP server: {self.config.name}")
            
            # Prepare environment
            env = os.environ.copy()
            env.update(self.config.env)
            
            # Start process
            self.process = subprocess.Popen(
                [self.config.command] + self.config.args,
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=0
            )
            
            # Wait a moment for process to start
            await asyncio.sleep(1)
            
            # Check if process is still running
            if self.process.poll() is None:
                self.is_running = True
                logger.info(f"MCP server {self.config.name} started successfully")
                
                # Discover tools
                await self._discover_tools()
            else:
                stderr_output = self.process.stderr.read() if self.process.stderr else "No error output"
                raise RuntimeError(f"MCP server {self.config.name} failed to start: {stderr_output}")
                
        except Exception as e:
            logger.error(f"Failed to start MCP server {self.config.name}: {e}")
            await self.stop()
            raise
    
    async def _discover_tools(self):
        """Discover available tools from the MCP server"""
        try:
            if self.config.connection_type == "stdio":
                await self._discover_tools_stdio()
            elif self.config.connection_type == "websocket":
                await self._discover_tools_websocket()
            elif self.config.connection_type == "http":
                await self._discover_tools_http()
                
        except Exception as e:
            logger.error(f"Failed to discover tools for {self.config.name}: {e}")
    
    async def _discover_tools_stdio(self):
        """Discover tools via stdio communication"""
        if not self.process or not self.process.stdin or not self.process.stdout:
            return
        
        try:
            # Send list_tools request
            request = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/list",
                "params": {}
            }
            
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            # Read response with timeout
            response_line = await asyncio.wait_for(
                asyncio.to_thread(self.process.stdout.readline),
                timeout=self.config.timeout
            )
            
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response and "tools" in response["result"]:
                    for tool_data in response["result"]["tools"]:
                        tool = MCPTool(
                            name=tool_data["name"],
                            description=tool_data.get("description", ""),
                            input_schema=tool_data.get("inputSchema", {}),
                            server_name=self.config.name
                        )
                        self.tools.append(tool)
                    
                    logger.info(f"Discovered {len(self.tools)} tools from {self.config.name}")
                    
        except Exception as e:
            logger.error(f"Error discovering tools via stdio for {self.config.name}: {e}")
    
    async def _discover_tools_websocket(self):
        """Discover tools via WebSocket communication"""
        # Implementation for WebSocket-based tool discovery
        pass
    
    async def _discover_tools_http(self):
        """Discover tools via HTTP communication"""
        # Implementation for HTTP-based tool discovery
        pass
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the MCP server"""
        try:
            if self.config.connection_type == "stdio":
                return await self._call_tool_stdio(tool_name, arguments)
            elif self.config.connection_type == "websocket":
                return await self._call_tool_websocket(tool_name, arguments)
            elif self.config.connection_type == "http":
                return await self._call_tool_http(tool_name, arguments)
            else:
                raise ValueError(f"Unsupported connection type: {self.config.connection_type}")
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} on {self.config.name}: {e}")
            raise
    
    async def _call_tool_stdio(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call tool via stdio communication"""
        if not self.process or not self.process.stdin or not self.process.stdout:
            raise RuntimeError("MCP server process not available")
        
        try:
            # Send tool call request
            request = {
                "jsonrpc": "2.0",
                "id": uuid.uuid4().hex,
                "method": "tools/call",
                "params": {
                    "name": tool_name,
                    "arguments": arguments
                }
            }
            
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            
            # Read response with timeout
            response_line = await asyncio.wait_for(
                asyncio.to_thread(self.process.stdout.readline),
                timeout=self.config.timeout
            )
            
            if response_line:
                response = json.loads(response_line.strip())
                if "result" in response:
                    return response["result"]
                elif "error" in response:
                    raise RuntimeError(f"MCP tool error: {response['error']}")
                else:
                    raise RuntimeError("Invalid MCP response format")
            else:
                raise RuntimeError("No response from MCP server")
                
        except Exception as e:
            logger.error(f"Error calling tool {tool_name} via stdio: {e}")
            raise
    
    async def _call_tool_websocket(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call tool via WebSocket communication"""
        # Implementation for WebSocket-based tool calls
        pass
    
    async def _call_tool_http(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call tool via HTTP communication"""
        # Implementation for HTTP-based tool calls
        pass
    
    async def stop(self):
        """Stop the MCP server process"""
        try:
            if self.process:
                self.process.terminate()
                
                # Wait for graceful shutdown
                try:
                    await asyncio.wait_for(
                        asyncio.to_thread(self.process.wait),
                        timeout=5.0
                    )
                except asyncio.TimeoutError:
                    # Force kill if graceful shutdown fails
                    self.process.kill()
                    await asyncio.to_thread(self.process.wait)
                
                self.process = None
            
            self.is_running = False
            logger.info(f"MCP server {self.config.name} stopped")
            
        except Exception as e:
            logger.error(f"Error stopping MCP server {self.config.name}: {e}")
    
    def get_tool(self, tool_name: str) -> Optional[MCPTool]:
        """Get a specific tool by name"""
        for tool in self.tools:
            if tool.name == tool_name:
                return tool
        return None


class MCPServerManager:
    """Manages multiple MCP servers and their tools"""
    
    def __init__(self, config_path: str = "/app/mcp-config.json"):
        self.config_path = config_path
        self.servers: Dict[str, MCPServerProcess] = {}
        self.tools: Dict[str, MCPTool] = {}  # tool_name -> tool
        self.server_configs: Dict[str, MCPServerConfig] = {}
    
    async def initialize(self):
        """Initialize MCP server manager"""
        try:
            logger.info("Initializing MCP Server Manager...")
            
            # Load configuration
            await self._load_config()
            
            # Start configured servers
            await self._start_servers()
            
            logger.info(f"MCP Server Manager initialized with {len(self.servers)} servers")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP Server Manager: {e}")
            raise
    
    async def _load_config(self):
        """Load MCP server configurations"""
        try:
            if not os.path.exists(self.config_path):
                logger.warning(f"MCP config file not found: {self.config_path}")
                return
            
            with open(self.config_path, 'r') as f:
                config_data = json.load(f)
            
            mcp_servers = config_data.get("mcpServers", {})
            
            for server_name, server_config in mcp_servers.items():
                config = MCPServerConfig(
                    name=server_name,
                    command=server_config["command"],
                    args=server_config.get("args", []),
                    env=server_config.get("env", {}),
                    timeout=server_config.get("timeout", 30),
                    auto_restart=server_config.get("auto_restart", True),
                    connection_type=server_config.get("connection_type", "stdio")
                )
                
                self.server_configs[server_name] = config
                
            logger.info(f"Loaded {len(self.server_configs)} MCP server configurations")
            
        except Exception as e:
            logger.error(f"Failed to load MCP config: {e}")
            raise
    
    async def _start_servers(self):
        """Start all configured MCP servers"""
        for server_name, config in self.server_configs.items():
            try:
                server = MCPServerProcess(config)
                await server.start()
                
                self.servers[server_name] = server
                
                # Register tools
                for tool in server.tools:
                    self.tools[tool.name] = tool
                
            except Exception as e:
                logger.error(f"Failed to start MCP server {server_name}: {e}")
                # Continue with other servers
    
    async def add_server(self, config: MCPServerConfig) -> bool:
        """Add and start a new MCP server"""
        try:
            if config.name in self.servers:
                logger.warning(f"MCP server {config.name} already exists")
                return False
            
            server = MCPServerProcess(config)
            await server.start()
            
            self.servers[config.name] = server
            self.server_configs[config.name] = config
            
            # Register tools
            for tool in server.tools:
                self.tools[tool.name] = tool
            
            logger.info(f"Added MCP server: {config.name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add MCP server {config.name}: {e}")
            return False
    
    async def remove_server(self, server_name: str) -> bool:
        """Remove and stop an MCP server"""
        try:
            if server_name not in self.servers:
                logger.warning(f"MCP server {server_name} not found")
                return False
            
            server = self.servers[server_name]
            await server.stop()
            
            # Remove tools
            tools_to_remove = [name for name, tool in self.tools.items() if tool.server_name == server_name]
            for tool_name in tools_to_remove:
                del self.tools[tool_name]
            
            del self.servers[server_name]
            if server_name in self.server_configs:
                del self.server_configs[server_name]
            
            logger.info(f"Removed MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove MCP server {server_name}: {e}")
            return False
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a tool on the appropriate MCP server"""
        tool = self.tools.get(tool_name)
        if not tool:
            raise ValueError(f"Tool {tool_name} not found")
        
        server = self.servers.get(tool.server_name)
        if not server:
            raise RuntimeError(f"Server {tool.server_name} not available")
        
        return await server.call_tool(tool_name, arguments)
    
    async def list_tools(self) -> List[Dict[str, Any]]:
        """List all available tools from all servers"""
        tools_list = []
        
        for tool in self.tools.values():
            tools_list.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": tool.input_schema,
                "server_name": tool.server_name
            })
        
        return tools_list
    
    async def get_tool_info(self, tool_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a specific tool"""
        tool = self.tools.get(tool_name)
        if not tool:
            return None
        
        return {
            "name": tool.name,
            "description": tool.description,
            "input_schema": tool.input_schema,
            "server_name": tool.server_name
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Check the health of all MCP servers"""
        health_status = {
            "total_servers": len(self.servers),
            "running_servers": 0,
            "total_tools": len(self.tools),
            "servers": {}
        }
        
        for server_name, server in self.servers.items():
            is_healthy = server.is_running and (server.process is None or server.process.poll() is None)
            
            if is_healthy:
                health_status["running_servers"] += 1
            
            health_status["servers"][server_name] = {
                "running": is_healthy,
                "tools_count": len(server.tools),
                "connection_type": server.config.connection_type
            }
        
        return health_status
    
    async def restart_server(self, server_name: str) -> bool:
        """Restart a specific MCP server"""
        try:
            if server_name not in self.servers:
                logger.warning(f"MCP server {server_name} not found")
                return False
            
            server = self.servers[server_name]
            config = server.config
            
            # Stop current server
            await server.stop()
            
            # Remove old tools
            tools_to_remove = [name for name, tool in self.tools.items() if tool.server_name == server_name]
            for tool_name in tools_to_remove:
                del self.tools[tool_name]
            
            # Start new server
            new_server = MCPServerProcess(config)
            await new_server.start()
            
            self.servers[server_name] = new_server
            
            # Register new tools
            for tool in new_server.tools:
                self.tools[tool.name] = tool
            
            logger.info(f"Restarted MCP server: {server_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to restart MCP server {server_name}: {e}")
            return False
    
    async def cleanup(self):
        """Stop all MCP servers and cleanup resources"""
        try:
            logger.info("Stopping all MCP servers...")
            
            # Stop all servers
            for server in self.servers.values():
                await server.stop()
            
            self.servers.clear()
            self.tools.clear()
            self.server_configs.clear()
            
            logger.info("MCP Server Manager cleanup complete")
            
        except Exception as e:
            logger.error(f"Error during MCP cleanup: {e}")
