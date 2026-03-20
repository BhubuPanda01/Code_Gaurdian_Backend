"""
Schemas for GitHub Repository Analysis
"""
from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class AnalyzeRequest(BaseModel):
    """Request schema for analyzing a GitHub repository"""
    github_url: str = Field(..., min_length=1, description="GitHub repository URL")

    @validator('github_url')
    def validate_github_url(cls, v):
        """Validate GitHub URL format"""
        if not v:
            raise ValueError("GitHub URL cannot be empty")
        if not v.startswith(('http://', 'https://')):
            raise ValueError("GitHub URL must start with http:// or https://")
        if 'github.com' not in v:
            raise ValueError("URL must be a GitHub repository URL")
        return v.strip()


class AnalyzeResponse(BaseModel):
    """Response schema for analyze request"""
    job_id: str = Field(..., description="Unique job identifier")
    status: str = Field(..., description="Job status")
    message: str = Field(..., description="Status message")

    class Config:
        from_attributes = True


class JobResponse(BaseModel):
    """Response schema for job details"""
    job_id: str
    github_url: str
    repository_name: str
    status: str
    result: Optional[str] = None
    error_message: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class JobResultResponse(BaseModel):
    """Response schema for job result data"""
    job_id: str
    status: str
    result: Optional[dict] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True
