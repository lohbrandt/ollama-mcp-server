"""Application settings and configuration management.

This module provides environment-based configuration using Pydantic BaseSettings
for type safety and validation.
"""

import os
from functools import lru_cache
from typing import Optional, Set
from pydantic import Field, field_validator, model_validator
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Ollama Server Configuration
    ollama_host: str = Field(
        default="localhost",
        env="OLLAMA_HOST",
        description="Ollama server host"
    )
    
    ollama_port: int = Field(
        default=11434,
        env="OLLAMA_PORT", 
        description="Ollama server port"
    )
    
    ollama_timeout: float = Field(
        default=30.0,
        env="OLLAMA_TIMEOUT",
        description="Request timeout in seconds"
    )
    
    # MCP Server Configuration
    mcp_server_name: str = Field(
        default="ollama-mcp-server",
        env="MCP_SERVER_NAME",
        description="MCP server name identifier"
    )
    
    # Logging Configuration
    log_level: str = Field(
        default="INFO",
        env="LOG_LEVEL",
        description="Logging level"
    )
    
    log_format: str = Field(
        default="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        env="LOG_FORMAT",
        description="Log message format"
    )
    
    # Performance Configuration
    max_concurrent_requests: int = Field(
        default=10,
        env="MAX_CONCURRENT_REQUESTS",
        description="Maximum concurrent requests"
    )
    
    connection_pool_size: int = Field(
        default=20,
        env="CONNECTION_POOL_SIZE", 
        description="HTTP connection pool size"
    )
    
    # Feature Flags
    enable_gpu_acceleration: bool = Field(
        default=True,
        env="ENABLE_GPU_ACCELERATION",
        description="Enable GPU acceleration detection"
    )
    
    enable_model_recommendations: bool = Field(
        default=True,
        env="ENABLE_MODEL_RECOMMENDATIONS",
        description="Enable AI model recommendations"
    )
    
    enable_auto_server_start: bool = Field(
        default=False,
        env="ENABLE_AUTO_SERVER_START",
        description="Automatically start Ollama server if not running"
    )
    
    # Development Configuration
    debug: bool = Field(
        default=False,
        env="DEBUG",
        description="Enable debug mode"
    )
    
    # Model Configuration
    default_chat_model: Optional[str] = Field(
        default=None,
        env="DEFAULT_CHAT_MODEL",
        description="Default model for chat if none specified"
    )
    
    model_download_timeout: float = Field(
        default=3600.0,  # 1 hour
        env="MODEL_DOWNLOAD_TIMEOUT",
        description="Model download timeout in seconds"
    )
    
    # System Monitoring
    system_monitor_interval: float = Field(
        default=30.0,
        env="SYSTEM_MONITOR_INTERVAL",
        description="System monitoring interval in seconds"
    )
    
    # Security
    allowed_models: Optional[Set[str]] = Field(
        default=None,
        env="ALLOWED_MODELS",
        description="Comma-separated list of allowed model names"
    )
    
    blocked_models: Optional[Set[str]] = Field(
        default=None,
        env="BLOCKED_MODELS", 
        description="Comma-separated list of blocked model names"
    )
    
    @field_validator("log_level")
    @classmethod
    def validate_log_level(cls, v: str) -> str:
        """Validate log level."""
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Invalid log level: {v}. Must be one of {valid_levels}")
        return v_upper
    
    @field_validator("ollama_port")
    @classmethod
    def validate_port(cls, v: int) -> int:
        """Validate port number."""
        if not 1 <= v <= 65535:
            raise ValueError("Port must be between 1 and 65535")
        return v
    
    @field_validator("ollama_timeout", "model_download_timeout", "system_monitor_interval")
    @classmethod
    def validate_positive_timeout(cls, v: float) -> float:
        """Ensure timeout values are positive."""
        if v <= 0:
            raise ValueError("Timeout values must be positive")
        return v
    
    @field_validator("max_concurrent_requests", "connection_pool_size")
    @classmethod
    def validate_positive_int(cls, v: int) -> int:
        """Ensure positive integer values."""
        if v <= 0:
            raise ValueError("Value must be positive")
        return v
    
    @field_validator("allowed_models", "blocked_models", mode="before")
    @classmethod
    def parse_model_lists(cls, v) -> Optional[Set[str]]:
        """Parse comma-separated model lists."""
        if v is None or v == "":
            return None
        if isinstance(v, str):
            return {model.strip() for model in v.split(",") if model.strip()}
        return v
    
    @property
    def ollama_url(self) -> str:
        """Get complete Ollama server URL."""
        return f"http://{self.ollama_host}:{self.ollama_port}"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development mode."""
        return self.debug or self.log_level == "DEBUG"
    
    def is_model_allowed(self, model_name: str) -> bool:
        """Check if a model is allowed to be used."""
        # If blocked list exists and model is in it, deny
        if self.blocked_models and model_name in self.blocked_models:
            return False
        
        # If allowed list exists, only allow models in it
        if self.allowed_models:
            return model_name in self.allowed_models
        
        # If no restrictions, allow all models
        return True
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        
        # Custom environment variable prefix
        env_prefix = ""
        
        # Allow extra fields for future expansion
        extra = "ignore"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance.
    
    This function uses lru_cache to ensure settings are loaded only once
    and cached for subsequent calls.
    """
    return Settings()


# Configuration validation helper
def validate_configuration() -> bool:
    """Validate current configuration and return True if valid."""
    try:
        settings = get_settings()
        
        # Additional runtime validation
        if settings.ollama_timeout < 1:
            raise ValueError("Ollama timeout too short (minimum 1 second)")
        
        if settings.max_concurrent_requests > 100:
            raise ValueError("Too many concurrent requests (maximum 100)")
        
        return True
        
    except Exception as e:
        print(f"Configuration validation failed: {e}")
        return False


def get_environment() -> str:
    """Get current environment (dev, test, prod)."""
    return os.getenv("ENVIRONMENT", "dev").lower()


def is_production() -> bool:
    """Check if running in production environment."""
    return get_environment() == "prod"


def is_testing() -> bool:
    """Check if running in test environment."""
    return get_environment() == "test"
