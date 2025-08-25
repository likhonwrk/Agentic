"""
Configuration management for AI Agent System
"""

import os
from typing import Optional
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    """Application settings"""
    
    # Server configuration
    host: str = Field(default="0.0.0.0", env="HOST")
    port: int = Field(default=8000, env="PORT")
    debug: bool = Field(default=False, env="DEBUG")
    
    # Database configuration
    redis_url: str = Field(default="redis://redis:6379", env="REDIS_URL")
    mongodb_url: str = Field(default="mongodb://admin:password@mongodb:27017", env="MONGODB_URL")
    
    # AI Model configuration
    openai_api_key: Optional[str] = Field(default=None, env="OPENAI_API_KEY")
    anthropic_api_key: Optional[str] = Field(default=None, env="ANTHROPIC_API_KEY")
    groq_api_key: Optional[str] = Field(default=None, env="GROQ_API_KEY")
    
    # Browser automation
    browser_headless: bool = Field(default=True, env="BROWSER_HEADLESS")
    browser_timeout: int = Field(default=30000, env="BROWSER_TIMEOUT")
    
    # MCP Server configuration
    mcp_config_path: str = Field(default="/app/mcp.json", env="MCP_CONFIG_PATH")
    
    # Security
    secret_key: str = Field(default="your-secret-key-change-in-production", env="SECRET_KEY")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="/app/logs/agent_system.log", env="LOG_FILE")
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
