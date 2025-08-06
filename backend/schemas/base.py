from pydantic import BaseModel, Field, ConfigDict
from typing import Generic, TypeVar, Optional, Any, List
from datetime import datetime
import json

T = TypeVar('T')


class BaseResponse(BaseModel):
    """Base response schema."""
    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""
    items: List[T] = Field(..., description="List of items")
    total: int = Field(..., ge=0, description="Total number of items")
    page: int = Field(..., ge=1, description="Current page number")
    size: int = Field(..., ge=1, le=100, description="Number of items per page")
    total_pages: int = Field(..., ge=0, description="Total number of pages")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Error message")
    error_code: Optional[str] = Field(None, description="Error code")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="Error timestamp")

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={
            datetime: lambda v: v.isoformat() if v else None
        }
    )


class SuccessResponse(BaseModel):
    """Success response schema."""
    message: str = Field(..., description="Success message")
    data: Optional[Any] = Field(None, description="Response data")

    model_config = ConfigDict(from_attributes=True)


class FileUploadResponse(BaseModel):
    """File upload response schema."""
    file_url: str = Field(..., description="URL of uploaded file")
    file_name: str = Field(..., description="Name of uploaded file")
    file_size: int = Field(..., ge=0, description="Size of uploaded file in bytes")
    file_type: str = Field(..., description="MIME type of uploaded file")

    model_config = ConfigDict(from_attributes=True)
