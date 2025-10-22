# backend/app/models/dto.py
"""
Data Transfer Objects (DTOs) for API requests and responses.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


# ============================================
# CHAT DTOs
# ============================================

class ChatRequest(BaseModel):
    """Request for chat with conversation tracking"""
    message: str = Field(..., min_length=1, max_length=5000, description="User's message")
    conversation_id: Optional[str] = Field(None, description="Conversation ID for context")


class ChatReply(BaseModel):
    """Chat response with conversation tracking"""
    reply: str = Field(..., description="AI-generated response")
    conversation_id: str = Field(..., description="Conversation ID")


# ============================================
# IMAGE DTOs
# ============================================

class ImageReply(BaseModel):
    """Image analysis response"""
    caption: str = Field(..., description="Image caption or description")
    answer: str = Field(..., description="Answer to the user's question")


# ============================================
# CSV DTOs
# ============================================

class CsvInUrl(BaseModel):
    """CSV analysis request via URL"""
    csvUrl: HttpUrl = Field(..., description="URL of the CSV file")
    prompt: str = Field(..., min_length=1, max_length=1000, description="Analysis request")


class CsvReply(BaseModel):
    """CSV analysis response"""
    summary: str = Field(..., description="Analysis summary or insights")
    plot_base64: Optional[str] = Field(None, description="Base64-encoded plot (PNG)")