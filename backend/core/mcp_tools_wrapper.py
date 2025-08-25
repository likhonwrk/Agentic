"""
MCP Tools Wrapper for ADK Integration
Provides ADK-compatible wrappers for MCP tools
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable

from pydantic import BaseModel, Field

from .mcp_integration import MCPServerManager, MCPTool

logger = logging.getLogger(__name__)


class MCPToolWrapper:
    """Wrapper to make MCP tools compatible with ADK agents"""
    
    def __init__(self, mcp_tool: MCPTool, mcp_manager: MCPServerManager):
        self.mcp_tool = mcp_tool
        self.mcp_manager = mcp_manager
        self.name = mcp_tool.name
        self.description = mcp_tool.description
        self.input_schema = mcp_tool.input_schema
    
    async def run_async(self, **kwargs) -> Dict[str, Any]:
        """Execute the MCP tool"""
        try:
            # Validate arguments against schema if needed
            validated_args = self._validate_arguments(kwargs)
            
            # Call the MCP tool
            result = await self.mcp_manager.call_tool(self.name, validated_args)
            
            return {
                "success": True,
                "result": result,
                "tool_name": self.name,
                "server_name": self.mcp_tool.server_name
            }
            
        except Exception as e:
            logger.error(f"Error executing MCP tool {self.name}: {e}")
            return {
                "success": False,
                "error": str(e),
                "tool_name": self.name,
                "server_name": self.mcp_tool.server_name
            }
    
    def _validate_arguments(self, kwargs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate arguments against the tool's input schema"""
        # Basic validation - in production, you might want more sophisticated validation
        if not self.input_schema:
            return kwargs
        
        # Extract required properties
        properties = self.input_schema.get("properties", {})
        required = self.input_schema.get("required", [])
        
        # Check required arguments
        for req_arg in required:
            if req_arg not in kwargs:
                raise ValueError(f"Missing required argument: {req_arg}")
        
        # Filter out unknown arguments
        validated = {}
        for key, value in kwargs.items():
            if key in properties:
                validated[key] = value
            else:
                logger.warning(f"Unknown argument {key} for tool {self.name}")
        
        return validated
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "name": self.name,
            "description": self.description,
            "input_schema": self.input_schema,
            "server_name": self.mcp_tool.server_name,
            "type": "mcp_tool"
        }


class MCPToolsetManager:
    """Manages collections of MCP tools for agents"""
    
    def __init__(self, mcp_manager: MCPServerManager):
        self.mcp_manager = mcp_manager
        self.tool_wrappers: Dict[str, MCPToolWrapper] = {}
        self.toolsets: Dict[str, List[MCPToolWrapper]] = {}
    
    async def initialize(self):
        """Initialize the toolset manager"""
        try:
            logger.info("Initializing MCP Toolset Manager...")
            
            # Create wrappers for all available MCP tools
            await self._create_tool_wrappers()
            
            # Create default toolsets
            await self._create_default_toolsets()
            
            logger.info(f"MCP Toolset Manager initialized with {len(self.tool_wrappers)} tools")
            
        except Exception as e:
            logger.error(f"Failed to initialize MCP Toolset Manager: {e}")
            raise
    
    async def _create_tool_wrappers(self):
        """Create ADK-compatible wrappers for all MCP tools"""
        for tool_name, mcp_tool in self.mcp_manager.tools.items():
            wrapper = MCPToolWrapper(mcp_tool, self.mcp_manager)
            self.tool_wrappers[tool_name] = wrapper
    
    async def _create_default_toolsets(self):
        """Create default toolsets based on tool categories"""
        # Browser automation tools
        browser_tools = []
        file_tools = []
        web_tools = []
        general_tools = []
        
        for tool_name, wrapper in self.tool_wrappers.items():
            # Categorize tools based on name patterns
            if any(keyword in tool_name.lower() for keyword in ['browser', 'page', 'click', 'screenshot']):
                browser_tools.append(wrapper)
            elif any(keyword in tool_name.lower() for keyword in ['file', 'read', 'write', 'directory']):
                file_tools.append(wrapper)
            elif any(keyword in tool_name.lower() for keyword in ['web', 'http', 'url', 'fetch']):
                web_tools.append(wrapper)
            else:
                general_tools.append(wrapper)
        
        # Store toolsets
        if browser_tools:
            self.toolsets["browser"] = browser_tools
        if file_tools:
            self.toolsets["filesystem"] = file_tools
        if web_tools:
            self.toolsets["web"] = web_tools
        if general_tools:
            self.toolsets["general"] = general_tools
        
        # All tools toolset
        self.toolsets["all"] = list(self.tool_wrappers.values())
    
    def get_tool(self, tool_name: str) -> Optional[MCPToolWrapper]:
        """Get a specific tool wrapper"""
        return self.tool_wrappers.get(tool_name)
    
    def get_toolset(self, toolset_name: str) -> List[MCPToolWrapper]:
        """Get a toolset by name"""
        return self.toolsets.get(toolset_name, [])
    
    def get_tools_for_agent(self, agent_type: str = "general") -> List[MCPToolWrapper]:
        """Get appropriate tools for a specific agent type"""
        if agent_type == "browser":
            return self.get_toolset("browser") + self.get_toolset("web")
        elif agent_type == "file":
            return self.get_toolset("filesystem")
        elif agent_type == "web":
            return self.get_toolset("web")
        else:
            return self.get_toolset("general")
    
    def list_available_tools(self) -> List[Dict[str, Any]]:
        """List all available tools"""
        return [wrapper.to_dict() for wrapper in self.tool_wrappers.values()]
    
    def list_toolsets(self) -> Dict[str, List[str]]:
        """List all available toolsets"""
        return {
            name: [tool.name for tool in tools]
            for name, tools in self.toolsets.items()
        }
    
    async def refresh_tools(self):
        """Refresh tools from MCP servers"""
        try:
            # Clear existing wrappers
            self.tool_wrappers.clear()
            self.toolsets.clear()
            
            # Recreate wrappers
            await self._create_tool_wrappers()
            await self._create_default_toolsets()
            
            logger.info("MCP tools refreshed successfully")
            
        except Exception as e:
            logger.error(f"Failed to refresh MCP tools: {e}")
            raise
