"""
Agent Management System
Handles AI agent lifecycle, routing, and coordination with ADK integration
"""

import asyncio
import logging
import uuid
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from enum import Enum

from pydantic import BaseModel, Field

from .session_manager import SessionManager
from .websocket_manager import WebSocketManager
from .mcp_integration import MCPServerManager
from .mcp_tools_wrapper import MCPToolsetManager

logger = logging.getLogger(__name__)


class AgentType(str, Enum):
    """Agent type enumeration"""
    LLM_AGENT = "llm_agent"
    BROWSER_AGENT = "browser_agent"
    DATA_AGENT = "data_agent"
    WORKFLOW_AGENT = "workflow_agent"
    CUSTOM_AGENT = "custom_agent"


class AgentStatus(str, Enum):
    """Agent status enumeration"""
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    OFFLINE = "offline"


class AgentCapability(BaseModel):
    """Agent capability definition"""
    name: str
    description: str
    parameters: Dict[str, Any] = {}
    required: bool = False


class AgentConfig(BaseModel):
    """Enhanced agent configuration model"""
    agent_id: str
    name: str
    type: AgentType
    model: str = "gpt-4"
    instructions: str
    tools: List[str] = []
    capabilities: List[AgentCapability] = []
    max_tokens: int = 4000
    temperature: float = 0.7
    context_window: int = 8000
    timeout: int = 300
    max_concurrent_sessions: int = 10
    auto_restart: bool = True
    metadata: Dict[str, Any] = {}
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class AgentInstance(BaseModel):
    """Running agent instance"""
    instance_id: str
    agent_id: str
    session_id: str
    status: AgentStatus = AgentStatus.IDLE
    current_task: Optional[str] = None
    start_time: datetime = Field(default_factory=datetime.utcnow)
    last_activity: datetime = Field(default_factory=datetime.utcnow)
    message_count: int = 0
    error_count: int = 0
    metadata: Dict[str, Any] = {}


class AgentResponse(BaseModel):
    """Enhanced agent response model"""
    response: str
    session_id: str
    agent_id: str
    instance_id: str
    response_time: float
    tokens_used: int = 0
    tools_called: List[str] = []
    metadata: Dict[str, Any] = {}
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class AgentMetrics(BaseModel):
    """Agent performance metrics"""
    agent_id: str
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    average_response_time: float = 0.0
    total_tokens_used: int = 0
    uptime_seconds: float = 0.0
    last_reset: datetime = Field(default_factory=datetime.utcnow)


class AgentManager:
    """Advanced AI agent management system"""
    
    def __init__(
        self,
        session_manager: SessionManager,
        browser_service: Any,
        mcp_manager: MCPServerManager,
        websocket_manager: WebSocketManager
    ):
        self.session_manager = session_manager
        self.browser_service = browser_service
        self.mcp_manager = mcp_manager
        self.websocket_manager = websocket_manager
        
        # Agent registry and instances
        self.agents: Dict[str, AgentConfig] = {}
        self.instances: Dict[str, AgentInstance] = {}
        self.metrics: Dict[str, AgentMetrics] = {}
        
        # Session to agent mapping
        self.session_agents: Dict[str, str] = {}  # session_id -> instance_id
        
        # MCP toolset manager
        self.mcp_toolset_manager: Optional[MCPToolsetManager] = None
        
        # Agent routing and load balancing
        self.agent_queues: Dict[str, asyncio.Queue] = {}
        self.worker_tasks: Dict[str, asyncio.Task] = {}
        
        # Setup default agents
        self._setup_default_agents()
    
    def _setup_default_agents(self):
        """Setup default agent configurations with enhanced capabilities"""
        default_agents = [
            AgentConfig(
                agent_id="general_assistant",
                name="General Assistant",
                type=AgentType.LLM_AGENT,
                model="gpt-4",
                instructions="""You are a helpful AI assistant with access to various tools and capabilities. 
                You can help with web browsing, data analysis, file operations, and general questions. 
                Always be helpful, accurate, and efficient in your responses.""",
                tools=["web_search", "calculator", "text_processing"],
                capabilities=[
                    AgentCapability(
                        name="general_conversation",
                        description="Handle general conversation and questions",
                        required=True
                    ),
                    AgentCapability(
                        name="web_search",
                        description="Search the web for information",
                        parameters={"max_results": 10}
                    ),
                    AgentCapability(
                        name="text_analysis",
                        description="Analyze and process text content"
                    )
                ]
            ),
            AgentConfig(
                agent_id="browser_specialist",
                name="Browser Automation Specialist",
                type=AgentType.BROWSER_AGENT,
                model="gpt-4",
                instructions="""You are specialized in web automation and browser tasks. 
                You can navigate websites, extract data, fill forms, take screenshots, and perform complex browser interactions.
                Always prioritize user safety and respect website terms of service.""",
                tools=["browser_automation", "screenshot", "web_scraping", "form_filling"],
                capabilities=[
                    AgentCapability(
                        name="web_navigation",
                        description="Navigate and interact with web pages",
                        required=True
                    ),
                    AgentCapability(
                        name="data_extraction",
                        description="Extract structured data from websites",
                        parameters={"formats": ["json", "csv", "xml"]}
                    ),
                    AgentCapability(
                        name="form_automation",
                        description="Fill and submit web forms automatically"
                    ),
                    AgentCapability(
                        name="screenshot_capture",
                        description="Capture screenshots of web pages"
                    )
                ]
            ),
            AgentConfig(
                agent_id="data_analyst",
                name="Data Analysis Agent",
                type=AgentType.DATA_AGENT,
                model="gpt-4",
                instructions="""You are a data analysis expert with advanced analytical capabilities.
                You can process data, create visualizations, perform statistical analysis, and provide insights.
                Always ensure data privacy and provide clear, actionable insights.""",
                tools=["data_processing", "visualization", "statistical_analysis", "file_operations"],
                capabilities=[
                    AgentCapability(
                        name="data_processing",
                        description="Process and clean various data formats",
                        required=True,
                        parameters={"supported_formats": ["csv", "json", "xlsx", "parquet"]}
                    ),
                    AgentCapability(
                        name="statistical_analysis",
                        description="Perform statistical analysis and modeling"
                    ),
                    AgentCapability(
                        name="data_visualization",
                        description="Create charts and visualizations",
                        parameters={"chart_types": ["bar", "line", "scatter", "heatmap"]}
                    )
                ]
            ),
            AgentConfig(
                agent_id="workflow_orchestrator",
                name="Workflow Orchestration Agent",
                type=AgentType.WORKFLOW_AGENT,
                model="gpt-4",
                instructions="""You are a workflow orchestration specialist that can coordinate multiple agents and tasks.
                You can break down complex requests into subtasks, delegate to appropriate agents, and manage execution flow.
                Always ensure efficient task distribution and proper error handling.""",
                tools=["agent_coordination", "task_scheduling", "workflow_management"],
                capabilities=[
                    AgentCapability(
                        name="task_decomposition",
                        description="Break complex tasks into manageable subtasks",
                        required=True
                    ),
                    AgentCapability(
                        name="agent_delegation",
                        description="Delegate tasks to appropriate specialized agents"
                    ),
                    AgentCapability(
                        name="workflow_monitoring",
                        description="Monitor and manage workflow execution"
                    )
                ]
            )
        ]
        
        for agent in default_agents:
            self.agents[agent.agent_id] = agent
            self.metrics[agent.agent_id] = AgentMetrics(agent_id=agent.agent_id)
            self.agent_queues[agent.agent_id] = asyncio.Queue()
    
    async def initialize(self):
        """Initialize the agent manager with enhanced capabilities"""
        try:
            logger.info("Initializing Advanced Agent Manager...")
            
            # Initialize MCP toolset manager
            if self.mcp_manager:
                self.mcp_toolset_manager = MCPToolsetManager(self.mcp_manager)
                await self.mcp_toolset_manager.initialize()
            
            # Start worker tasks for each agent
            await self._start_agent_workers()
            
            # Load custom agents from database
            await self._load_custom_agents()
            
            # Start monitoring tasks
            asyncio.create_task(self._monitor_agents())
            asyncio.create_task(self._cleanup_expired_instances())
            
            logger.info(f"Advanced Agent Manager initialized with {len(self.agents)} agents")
            
        except Exception as e:
            logger.error(f"Failed to initialize Advanced Agent Manager: {e}")
            raise
    
    async def _start_agent_workers(self):
        """Start worker tasks for processing agent requests"""
        for agent_id in self.agents.keys():
            worker_task = asyncio.create_task(self._agent_worker(agent_id))
            self.worker_tasks[agent_id] = worker_task
    
    async def _agent_worker(self, agent_id: str):
        """Worker task for processing agent requests"""
        queue = self.agent_queues[agent_id]
        
        while True:
            try:
                # Get next request from queue
                request_data = await queue.get()
                
                # Process the request
                await self._process_agent_request(agent_id, request_data)
                
                # Mark task as done
                queue.task_done()
                
            except Exception as e:
                logger.error(f"Error in agent worker {agent_id}: {e}")
                await asyncio.sleep(1)  # Brief pause before continuing
    
    async def _process_agent_request(self, agent_id: str, request_data: Dict[str, Any]):
        """Process an individual agent request"""
        try:
            instance_id = request_data["instance_id"]
            message = request_data["message"]
            session_id = request_data["session_id"]
            context = request_data.get("context", {})
            
            # Update instance status
            if instance_id in self.instances:
                self.instances[instance_id].status = AgentStatus.BUSY
                self.instances[instance_id].current_task = message[:100]
                self.instances[instance_id].last_activity = datetime.utcnow()
            
            # Get agent configuration
            agent_config = self.agents[agent_id]
            
            # Process with agent
            start_time = asyncio.get_event_loop().time()
            response_text = await self._execute_agent_logic(
                agent_config, message, session_id, context
            )
            end_time = asyncio.get_event_loop().time()
            response_time = end_time - start_time
            
            # Update metrics
            await self._update_metrics(agent_id, response_time, success=True)
            
            # Update instance
            if instance_id in self.instances:
                self.instances[instance_id].status = AgentStatus.IDLE
                self.instances[instance_id].current_task = None
                self.instances[instance_id].message_count += 1
                self.instances[instance_id].last_activity = datetime.utcnow()
            
            # Send response via WebSocket
            await self.websocket_manager.send_message(session_id, {
                "type": "agent_response",
                "response": response_text,
                "agent_id": agent_id,
                "instance_id": instance_id,
                "response_time": response_time,
                "session_id": session_id
            })
            
        except Exception as e:
            logger.error(f"Error processing agent request for {agent_id}: {e}")
            
            # Update metrics for failure
            await self._update_metrics(agent_id, 0, success=False)
            
            # Update instance status
            if instance_id in self.instances:
                self.instances[instance_id].status = AgentStatus.ERROR
                self.instances[instance_id].error_count += 1
    
    async def _execute_agent_logic(
        self,
        agent_config: AgentConfig,
        message: str,
        session_id: str,
        context: Dict[str, Any]
    ) -> str:
        """Execute agent-specific logic based on agent type"""
        
        try:
            # Get conversation history
            conversation_history = await self.session_manager.get_conversation_history(session_id)
            
            # Get appropriate tools for the agent
            available_tools = await self._get_agent_tools(agent_config)
            
            # Build agent context
            agent_context = {
                "message": message,
                "history": conversation_history[-10:],  # Last 10 messages
                "tools": available_tools,
                "instructions": agent_config.instructions,
                "capabilities": [cap.dict() for cap in agent_config.capabilities],
                "session_id": session_id,
                **context
            }
            
            # Execute based on agent type
            if agent_config.type == AgentType.BROWSER_AGENT:
                return await self._execute_browser_agent(agent_context)
            elif agent_config.type == AgentType.DATA_AGENT:
                return await self._execute_data_agent(agent_context)
            elif agent_config.type == AgentType.WORKFLOW_AGENT:
                return await self._execute_workflow_agent(agent_context)
            else:
                return await self._execute_llm_agent(agent_context)
                
        except Exception as e:
            logger.error(f"Error executing agent logic: {e}")
            return f"I apologize, but I encountered an error while processing your request: {str(e)}"
    
    async def _get_agent_tools(self, agent_config: AgentConfig) -> List[str]:
        """Get available tools for an agent"""
        tools = agent_config.tools.copy()
        
        # Add MCP tools if available
        if self.mcp_toolset_manager:
            mcp_tools = self.mcp_toolset_manager.get_tools_for_agent(agent_config.type.value)
            tools.extend([tool.name for tool in mcp_tools])
        
        return tools
    
    async def _execute_llm_agent(self, context: Dict[str, Any]) -> str:
        """Execute LLM agent logic"""
        # Simulate LLM processing
        await asyncio.sleep(0.1)
        
        message = context["message"]
        tools = context["tools"]
        
        return f"[LLM Agent] I understand your request: '{message}'. I have access to these tools: {', '.join(tools[:5])}{'...' if len(tools) > 5 else ''}. How can I help you further?"
    
    async def _execute_browser_agent(self, context: Dict[str, Any]) -> str:
        """Execute browser agent logic"""
        message = context["message"]
        
        # Check if this is a browser-related request
        browser_keywords = ["navigate", "click", "screenshot", "scrape", "website", "page"]
        if any(keyword in message.lower() for keyword in browser_keywords):
            return f"[Browser Agent] I can help you with web automation tasks. Your request: '{message}'. I'll use my browser automation capabilities to assist you."
        else:
            return f"[Browser Agent] I specialize in web automation. For general questions, you might want to use the General Assistant. However, I can still help with: '{message}'"
    
    async def _execute_data_agent(self, context: Dict[str, Any]) -> str:
        """Execute data analysis agent logic"""
        message = context["message"]
        
        # Check if this is a data-related request
        data_keywords = ["analyze", "data", "chart", "graph", "statistics", "csv", "excel"]
        if any(keyword in message.lower() for keyword in data_keywords):
            return f"[Data Agent] I can help you with data analysis tasks. Your request: '{message}'. I'll process your data and provide insights."
        else:
            return f"[Data Agent] I specialize in data analysis. Your request: '{message}'. If you have data to analyze, I'm here to help!"
    
    async def _execute_workflow_agent(self, context: Dict[str, Any]) -> str:
        """Execute workflow orchestration agent logic"""
        message = context["message"]
        
        return f"[Workflow Agent] I can help orchestrate complex tasks involving multiple agents. Your request: '{message}'. Let me break this down into manageable steps."
    
    async def process_message(
        self,
        message: str,
        session_id: Optional[str] = None,
        agent_type: str = "default",
        tools: List[str] = None,
        context: Dict = None
    ) -> AgentResponse:
        """Process a message with enhanced agent selection and management"""
        
        try:
            # Create session if not provided
            if not session_id:
                session_id = await self.session_manager.create_session()
            
            # Select appropriate agent
            agent_id = await self._select_optimal_agent(agent_type, tools or [], message)
            agent_config = self.agents.get(agent_id)
            
            if not agent_config:
                raise ValueError(f"Agent {agent_id} not found")
            
            # Create or get agent instance
            instance_id = await self._get_or_create_instance(agent_id, session_id)
            
            # Add message to conversation history
            await self.session_manager.add_message(
                session_id, "user", message, {"agent_id": agent_id, "instance_id": instance_id}
            )
            
            # Queue the request for processing
            request_data = {
                "instance_id": instance_id,
                "message": message,
                "session_id": session_id,
                "context": context or {},
                "tools": tools or []
            }
            
            await self.agent_queues[agent_id].put(request_data)
            
            # Return immediate response (actual response will come via WebSocket)
            return AgentResponse(
                response="Request queued for processing. You'll receive the response shortly.",
                session_id=session_id,
                agent_id=agent_id,
                instance_id=instance_id,
                response_time=0.0,
                metadata={
                    "agent_name": agent_config.name,
                    "model": agent_config.model,
                    "status": "queued"
                }
            )
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            raise
    
    async def _select_optimal_agent(self, agent_type: str, tools: List[str], message: str) -> str:
        """Select the most appropriate agent using enhanced logic"""
        
        # Analyze message content for better agent selection
        message_lower = message.lower()
        
        # Browser-related keywords
        if any(keyword in message_lower for keyword in ["website", "browser", "navigate", "click", "screenshot", "scrape"]):
            return "browser_specialist"
        
        # Data analysis keywords
        elif any(keyword in message_lower for keyword in ["analyze", "data", "chart", "statistics", "csv", "excel", "graph"]):
            return "data_analyst"
        
        # Workflow/complex task keywords
        elif any(keyword in message_lower for keyword in ["workflow", "multiple steps", "coordinate", "orchestrate", "complex task"]):
            return "workflow_orchestrator"
        
        # Tool-based selection
        elif "browser_automation" in tools:
            return "browser_specialist"
        elif any(tool in tools for tool in ["data_processing", "visualization"]):
            return "data_analyst"
        
        # Agent type-based selection
        elif agent_type == "browser":
            return "browser_specialist"
        elif agent_type == "analysis":
            return "data_analyst"
        elif agent_type == "workflow":
            return "workflow_orchestrator"
        
        # Default to general assistant
        else:
            return "general_assistant"
    
    async def _get_or_create_instance(self, agent_id: str, session_id: str) -> str:
        """Get existing or create new agent instance"""
        
        # Check if session already has an instance
        if session_id in self.session_agents:
            instance_id = self.session_agents[session_id]
            if instance_id in self.instances:
                return instance_id
        
        # Create new instance
        instance_id = str(uuid.uuid4())
        instance = AgentInstance(
            instance_id=instance_id,
            agent_id=agent_id,
            session_id=session_id,
            status=AgentStatus.IDLE
        )
        
        self.instances[instance_id] = instance
        self.session_agents[session_id] = instance_id
        
        logger.info(f"Created new agent instance: {instance_id} for agent {agent_id}")
        return instance_id
    
    async def _update_metrics(self, agent_id: str, response_time: float, success: bool):
        """Update agent performance metrics"""
        if agent_id not in self.metrics:
            self.metrics[agent_id] = AgentMetrics(agent_id=agent_id)
        
        metrics = self.metrics[agent_id]
        metrics.total_requests += 1
        
        if success:
            metrics.successful_requests += 1
            # Update average response time
            total_time = metrics.average_response_time * (metrics.successful_requests - 1) + response_time
            metrics.average_response_time = total_time / metrics.successful_requests
        else:
            metrics.failed_requests += 1
    
    async def _monitor_agents(self):
        """Monitor agent health and performance"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute
                
                current_time = datetime.utcnow()
                
                # Check for stuck instances
                for instance_id, instance in list(self.instances.items()):
                    if instance.status == AgentStatus.BUSY:
                        time_since_activity = (current_time - instance.last_activity).total_seconds()
                        if time_since_activity > 300:  # 5 minutes timeout
                            logger.warning(f"Instance {instance_id} appears stuck, resetting")
                            instance.status = AgentStatus.ERROR
                            instance.current_task = None
                
                # Log metrics
                for agent_id, metrics in self.metrics.items():
                    if metrics.total_requests > 0:
                        success_rate = (metrics.successful_requests / metrics.total_requests) * 100
                        logger.info(f"Agent {agent_id}: {metrics.total_requests} requests, {success_rate:.1f}% success rate, {metrics.average_response_time:.2f}s avg response")
                
            except Exception as e:
                logger.error(f"Error in agent monitoring: {e}")
    
    async def _cleanup_expired_instances(self):
        """Clean up expired agent instances"""
        while True:
            try:
                await asyncio.sleep(300)  # Check every 5 minutes
                
                current_time = datetime.utcnow()
                expired_instances = []
                
                for instance_id, instance in self.instances.items():
                    time_since_activity = (current_time - instance.last_activity).total_seconds()
                    if time_since_activity > 3600:  # 1 hour timeout
                        expired_instances.append(instance_id)
                
                # Remove expired instances
                for instance_id in expired_instances:
                    instance = self.instances[instance_id]
                    if instance.session_id in self.session_agents:
                        del self.session_agents[instance.session_id]
                    del self.instances[instance_id]
                    logger.info(f"Cleaned up expired instance: {instance_id}")
                
            except Exception as e:
                logger.error(f"Error in instance cleanup: {e}")
    
    async def _load_custom_agents(self):
        """Load custom agent configurations from database"""
        # This would load custom agents from configuration
        # For now, we'll use the default agents
        pass
    
    async def get_agent_info(self, agent_id: str) -> Optional[AgentConfig]:
        """Get information about a specific agent"""
        return self.agents.get(agent_id)
    
    async def list_agents(self) -> List[Dict[str, Any]]:
        """List all agents with their status"""
        agents_status = []
        for agent_id in self.agents.keys():
            status = await self.get_agent_status(agent_id)
            if status:
                agents_status.append(status)
        return agents_status
    
    async def get_agent_status(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed status of an agent"""
        if agent_id not in self.agents:
            return None
        
        agent_config = self.agents[agent_id]
        metrics = self.metrics.get(agent_id, AgentMetrics(agent_id=agent_id))
        
        # Count active instances
        active_instances = [
            instance for instance in self.instances.values()
            if instance.agent_id == agent_id and instance.status != AgentStatus.OFFLINE
        ]
        
        return {
            "agent_id": agent_id,
            "name": agent_config.name,
            "type": agent_config.type.value,
            "status": "online" if active_instances else "offline",
            "active_instances": len(active_instances),
            "total_requests": metrics.total_requests,
            "success_rate": (metrics.successful_requests / metrics.total_requests * 100) if metrics.total_requests > 0 else 0,
            "average_response_time": metrics.average_response_time,
            "capabilities": [cap.dict() for cap in agent_config.capabilities],
            "tools": agent_config.tools
        }
    
    async def create_custom_agent(self, config: AgentConfig) -> str:
        """Create a custom agent"""
        try:
            # Validate configuration
            if config.agent_id in self.agents:
                raise ValueError(f"Agent {config.agent_id} already exists")
            
            # Add to registry
            self.agents[config.agent_id] = config
            self.metrics[config.agent_id] = AgentMetrics(agent_id=config.agent_id)
            self.agent_queues[config.agent_id] = asyncio.Queue()
            
            logger.info(f"Created custom agent: {config.agent_id}")
            return config.agent_id
            
        except Exception as e:
            logger.error(f"Failed to create custom agent: {e}")
            raise
    
    async def cleanup(self):
        """Cleanup all agent resources"""
        try:
            # Stop all worker tasks
            for task in self.worker_tasks.values():
                task.cancel()
            
            # Wait for tasks to complete
            if self.worker_tasks:
                await asyncio.gather(*self.worker_tasks.values(), return_exceptions=True)
            
            logger.info("Advanced Agent Manager cleanup complete")
        except Exception as e:
            logger.error(f"Error during Advanced Agent Manager cleanup: {e}")
