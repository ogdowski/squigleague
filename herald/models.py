# herald/models.py
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CreateExchangeRequest(BaseModel):
    """Request model for creating a new exchange"""

    list_content: str = Field(
        ..., min_length=1, max_length=50000, description="Army list content"
    )

    @validator("list_content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("List content cannot be empty")
        return v.strip()


class RespondExchangeRequest(BaseModel):
    """Request model for responding to an exchange"""

    list_content: str = Field(
        ..., min_length=1, max_length=50000, description="Army list content"
    )

    @validator("list_content")
    def validate_content(cls, v):
        if not v.strip():
            raise ValueError("List content cannot be empty")
        return v.strip()


class CreateExchangeResponse(BaseModel):
    """Response model after creating an exchange"""

    exchange_id: str
    url: str
    full_url: str


class ExchangeStatusResponse(BaseModel):
    """Response model for exchange status check"""

    ready: bool


class HealthCheckResponse(BaseModel):
    """Response model for health check"""

    status: str
    module: str
    database: str


class ResourcesResponse(BaseModel):
    """Response model for resource monitoring"""

    cpu_percent: float
    memory: dict
    disk: dict
