"""Core domain models for the Ollama MCP Server.

This module contains all domain models using Pydantic for validation and serialization.
These models represent the core business entities and value objects.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional, Union, Any
from pydantic import BaseModel, Field, field_validator, model_validator
import re


class ModelSize(BaseModel):
    """Represents model size information."""
    bytes: int = Field(..., description="Size in bytes")
    
    @property
    def human_readable(self) -> str:
        """Return human-readable size string."""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if self.bytes < 1024.0:
                return f"{self.bytes:.1f}{unit}"
            self.bytes /= 1024.0
        return f"{self.bytes:.1f}PB"


class ModelInfo(BaseModel):
    """Represents an Ollama model with full metadata."""
    
    name: str = Field(..., description="Model name")
    size: ModelSize = Field(..., description="Model size information")
    digest: Optional[str] = Field(None, description="Model digest/hash")
    modified: datetime = Field(..., description="Last modified timestamp")
    families: Optional[List[str]] = Field(default_factory=list, description="Model families")
    format: Optional[str] = Field(None, description="Model format")
    parameter_size: Optional[str] = Field(None, description="Parameter size (e.g., '7B', '13B')")
    quantization_level: Optional[str] = Field(None, description="Quantization level")
    
    @field_validator('name')
    @classmethod
    def validate_model_name(cls, v: str) -> str:
        """Validate model name format."""
        if not v or not isinstance(v, str):
            raise ValueError("Model name must be a non-empty string")
        
        # Basic name validation - allow letters, numbers, dots, colons, hyphens
        if not re.match(r'^[a-zA-Z0-9._:-]+$', v):
            raise ValueError("Model name contains invalid characters")
        
        return v.strip()
    
    @property
    def display_name(self) -> str:
        """Return a user-friendly display name."""
        return self.name
    
    @property
    def size_human(self) -> str:
        """Return human-readable size."""
        return self.size.human_readable
    
    def __str__(self) -> str:
        return f"{self.name} ({self.size_human})"


class GPUVendor(str, Enum):
    """GPU vendor enumeration."""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    APPLE = "apple"
    UNKNOWN = "unknown"


class GPUInfo(BaseModel):
    """Represents GPU information."""
    
    name: str = Field(..., description="GPU name")
    vendor: GPUVendor = Field(default=GPUVendor.UNKNOWN, description="GPU vendor")
    memory_mb: Optional[int] = Field(None, description="GPU memory in MB")
    compute_capability: Optional[str] = Field(None, description="Compute capability version")
    driver_version: Optional[str] = Field(None, description="Driver version")
    
    @property
    def memory_gb(self) -> Optional[float]:
        """Return GPU memory in GB."""
        if self.memory_mb is None:
            return None
        return round(self.memory_mb / 1024, 1)
    
    @property
    def is_compatible(self) -> bool:
        """Check if GPU is compatible for AI workloads."""
        if self.vendor == GPUVendor.NVIDIA:
            return self.memory_mb is not None and self.memory_mb >= 4096  # 4GB minimum
        elif self.vendor == GPUVendor.APPLE:
            return True  # Apple Silicon generally compatible
        elif self.vendor == GPUVendor.AMD:
            return self.memory_mb is not None and self.memory_mb >= 8192  # 8GB minimum for AMD
        return False


class SystemResources(BaseModel):
    """Represents system resource information."""
    
    cpu_cores: int = Field(..., description="Number of CPU cores")
    total_memory_gb: float = Field(..., description="Total system memory in GB")
    available_memory_gb: float = Field(..., description="Available memory in GB")
    memory_usage_percent: float = Field(..., description="Memory usage percentage")
    disk_free_gb: float = Field(..., description="Free disk space in GB")
    disk_total_gb: float = Field(..., description="Total disk space in GB")
    platform: str = Field(..., description="Operating system platform")
    gpus: List[GPUInfo] = Field(default_factory=list, description="Available GPUs")
    
    @field_validator('total_memory_gb', 'available_memory_gb', 'disk_free_gb', 'disk_total_gb')
    @classmethod
    def validate_positive_values(cls, v: float) -> float:
        """Ensure values are positive."""
        if v < 0:
            raise ValueError("Resource values must be positive")
        return v
    
    @field_validator('memory_usage_percent')
    @classmethod
    def validate_percentage(cls, v: float) -> float:
        """Ensure percentage is within valid range."""
        if not 0 <= v <= 100:
            raise ValueError("Percentage must be between 0 and 100")
        return v
    
    @property
    def has_gpu(self) -> bool:
        """Check if system has compatible GPU."""
        return any(gpu.is_compatible for gpu in self.gpus)
    
    @property
    def gpu_count(self) -> int:
        """Return count of compatible GPUs."""
        return sum(1 for gpu in self.gpus if gpu.is_compatible)
    
    @property
    def is_ai_ready(self) -> bool:
        """Check if system meets minimum AI requirements."""
        return (
            self.available_memory_gb >= 4.0 and
            self.disk_free_gb >= 10.0 and
            self.cpu_cores >= 2
        )
    
    @property
    def recommended_model_size(self) -> str:
        """Recommend model size based on system resources."""
        if self.available_memory_gb >= 16:
            return "large (13B+)"
        elif self.available_memory_gb >= 8:
            return "medium (7B)"
        elif self.available_memory_gb >= 4:
            return "small (3B)"
        else:
            return "micro (1B)"


class HealthStatus(BaseModel):
    """Represents Ollama server health status."""
    
    healthy: bool = Field(..., description="Whether server is healthy")
    host: str = Field(..., description="Server host URL")
    models_count: int = Field(default=0, description="Number of available models")
    response_time_ms: Optional[float] = Field(None, description="Response time in milliseconds")
    error: Optional[str] = Field(None, description="Error message if unhealthy")
    last_checked: datetime = Field(default_factory=datetime.now, description="Last health check time")
    
    @property
    def status_text(self) -> str:
        """Return human-readable status."""
        return "HEALTHY" if self.healthy else "UNHEALTHY"
    
    @property
    def is_responsive(self) -> bool:
        """Check if server is responsive (< 5 seconds)."""
        return self.response_time_ms is not None and self.response_time_ms < 5000


class DownloadStatus(str, Enum):
    """Download status enumeration."""
    PENDING = "pending"
    DOWNLOADING = "downloading"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class DownloadProgress(BaseModel):
    """Represents model download progress."""
    
    job_id: str = Field(..., description="Unique job identifier")
    model_name: str = Field(..., description="Name of model being downloaded")
    status: DownloadStatus = Field(..., description="Current download status")
    progress_percent: float = Field(default=0.0, description="Progress percentage (0-100)")
    bytes_downloaded: int = Field(default=0, description="Bytes downloaded")
    total_bytes: Optional[int] = Field(None, description="Total bytes to download")
    download_speed_mbps: Optional[float] = Field(None, description="Download speed in Mbps")
    eta_seconds: Optional[int] = Field(None, description="Estimated time remaining")
    error_message: Optional[str] = Field(None, description="Error message if failed")
    started_at: datetime = Field(default_factory=datetime.now, description="Download start time")
    completed_at: Optional[datetime] = Field(None, description="Download completion time")
    
    @field_validator('progress_percent')
    @classmethod
    def validate_progress(cls, v: float) -> float:
        """Ensure progress is within valid range."""
        return max(0.0, min(100.0, v))
    
    @property
    def is_active(self) -> bool:
        """Check if download is currently active."""
        return self.status in [DownloadStatus.PENDING, DownloadStatus.DOWNLOADING]
    
    @property
    def is_completed(self) -> bool:
        """Check if download completed successfully."""
        return self.status == DownloadStatus.COMPLETED
    
    @property
    def size_human(self) -> str:
        """Return human-readable size progress."""
        if self.total_bytes is None:
            return f"{self.bytes_downloaded // (1024*1024)}MB downloaded"
        
        downloaded_mb = self.bytes_downloaded // (1024*1024)
        total_mb = self.total_bytes // (1024*1024)
        return f"{downloaded_mb}MB / {total_mb}MB"
    
    @property
    def eta_human(self) -> str:
        """Return human-readable ETA."""
        if self.eta_seconds is None:
            return "Unknown"
        
        if self.eta_seconds < 60:
            return f"{self.eta_seconds}s"
        elif self.eta_seconds < 3600:
            minutes = self.eta_seconds // 60
            return f"{minutes}m"
        else:
            hours = self.eta_seconds // 3600
            minutes = (self.eta_seconds % 3600) // 60
            return f"{hours}h {minutes}m"


class ChatRequest(BaseModel):
    """Represents a chat request."""
    
    model: str = Field(..., description="Model name to use for chat")
    message: str = Field(..., description="User message")
    temperature: float = Field(default=0.7, description="Generation temperature")
    max_tokens: Optional[int] = Field(None, description="Maximum tokens to generate")
    stream: bool = Field(default=False, description="Whether to stream response")
    context_window: Optional[int] = Field(None, description="Context window size")
    
    @field_validator('temperature')
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        """Ensure temperature is within valid range."""
        if not 0.0 <= v <= 2.0:
            raise ValueError("Temperature must be between 0.0 and 2.0")
        return v
    
    @field_validator('message')
    @classmethod
    def validate_message(cls, v: str) -> str:
        """Ensure message is not empty."""
        if not v or not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()
    
    @field_validator('max_tokens')
    @classmethod
    def validate_max_tokens(cls, v: Optional[int]) -> Optional[int]:
        """Ensure max_tokens is positive if specified."""
        if v is not None and v <= 0:
            raise ValueError("max_tokens must be positive")
        return v


class ChatResponse(BaseModel):
    """Represents a chat response."""
    
    response: str = Field(..., description="Generated response text")
    model: str = Field(..., description="Model used for generation")
    total_duration_ms: Optional[float] = Field(None, description="Total generation time")
    load_duration_ms: Optional[float] = Field(None, description="Model loading time")
    prompt_eval_count: Optional[int] = Field(None, description="Prompt tokens evaluated")
    prompt_eval_duration_ms: Optional[float] = Field(None, description="Prompt evaluation time")
    eval_count: Optional[int] = Field(None, description="Response tokens generated")
    eval_duration_ms: Optional[float] = Field(None, description="Response generation time")
    context_length: Optional[int] = Field(None, description="Context length used")
    
    @property
    def tokens_per_second(self) -> Optional[float]:
        """Calculate tokens per second generation rate."""
        if self.eval_count is None or self.eval_duration_ms is None:
            return None
        if self.eval_duration_ms == 0:
            return None
        return (self.eval_count * 1000) / self.eval_duration_ms
    
    @property
    def total_duration_human(self) -> str:
        """Return human-readable total duration."""
        if self.total_duration_ms is None:
            return "Unknown"
        
        seconds = self.total_duration_ms / 1000
        if seconds < 1:
            return f"{int(self.total_duration_ms)}ms"
        elif seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = int(seconds // 60)
            remaining_seconds = seconds % 60
            return f"{minutes}m {remaining_seconds:.1f}s"


class APIResponse(BaseModel):
    """Standard API response format."""
    
    success: bool = Field(..., description="Whether operation was successful")
    data: Optional[Any] = Field(None, description="Response data")
    error: Optional[str] = Field(None, description="Error message if unsuccessful")
    message: Optional[str] = Field(None, description="Additional message")
    timestamp: datetime = Field(default_factory=datetime.now, description="Response timestamp")
    
    @model_validator(mode='after')
    @classmethod
    def validate_response(cls, values):
        """Ensure response consistency."""
        if values.success and values.error:
            raise ValueError("Successful response cannot have an error")
        if not values.success and not values.error:
            raise ValueError("Unsuccessful response must have an error message")
        
        return values


class ModelRecommendation(BaseModel):
    """Represents a model recommendation."""
    
    model_name: str = Field(..., description="Recommended model name")
    score: float = Field(..., description="Recommendation score (0-100)")
    reasons: List[str] = Field(..., description="Reasons for recommendation")
    size: str = Field(..., description="Model size")
    min_ram_gb: float = Field(..., description="Minimum RAM requirement")
    estimated_speed: str = Field(..., description="Estimated inference speed")
    quality: str = Field(..., description="Expected output quality")
    use_cases: List[str] = Field(default_factory=list, description="Suitable use cases")
    
    @field_validator('score')
    @classmethod
    def validate_score(cls, v: float) -> float:
        """Ensure score is within valid range."""
        return max(0.0, min(100.0, v))
