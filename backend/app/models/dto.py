# backend/app/models/dto.py
"""
Data Transfer Objects (DTOs) for API requests and responses.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional, List, Dict
from datetime import datetime


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
# CSV DTOs (Original - Kept for backward compatibility)
# ============================================

class CsvInUrl(BaseModel):
    """CSV analysis request via URL"""
    csvUrl: HttpUrl = Field(..., description="URL of the CSV file")
    prompt: str = Field(..., min_length=1, max_length=1000, description="Analysis request")


class CsvReply(BaseModel):
    """CSV analysis response"""
    summary: str = Field(..., description="Analysis summary or insights")
    plot_base64: Optional[str] = Field(None, description="Base64-encoded plot (PNG)")


# ============================================
# CSV CHAT DTOs (New - For AI Chatbot)
# ============================================

class CsvChatMessage(BaseModel):
    """Single message in CSV conversation"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    plot_base64: Optional[str] = Field(None, description="Base64-encoded plot if included")
    timestamp: datetime = Field(default_factory=datetime.now, description="Message timestamp")


class CsvUploadResponse(BaseModel):
    """Response after CSV upload - creates new session"""
    session_id: str = Field(..., description="Unique session ID for this CSV conversation")
    message: str = Field(..., description="Confirmation message")
    csv_info: dict = Field(..., description="Basic CSV information (rows, columns, etc.)")


class CsvChatRequest(BaseModel):
    """Request for ongoing CSV conversation"""
    session_id: str = Field(..., description="Session ID from upload")
    message: str = Field(..., min_length=1, max_length=2000, description="User's question about the CSV")


class CsvChatReply(BaseModel):
    """AI response in CSV conversation"""
    session_id: str = Field(..., description="Session ID")
    reply: str = Field(..., description="AI-generated response")
    plot_base64: Optional[str] = Field(None, description="Base64-encoded plot if generated")
    conversation_history: List[CsvChatMessage] = Field(..., description="Full conversation history")


# ============================================
# IMAGE CHAT DTOs (NEW)
# ============================================

class ImageChatMessage(BaseModel):
    """Single message in image chat conversation"""
    role: str = Field(..., description="Message role: 'user' or 'assistant'")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(..., description="Message timestamp (ISO format)")


class ImageChatUploadResponse(BaseModel):
    """Response after image upload - creates new chat session"""
    session_id: str = Field(..., description="Unique session ID for this image chat")
    message: str = Field(..., description="Confirmation message")
    image_info: Dict = Field(..., description="Image information (size, format, etc.)")


class ImageChatRequest(BaseModel):
    """Request for ongoing image conversation"""
    session_id: str = Field(..., description="Session ID from upload")
    message: str = Field(..., min_length=1, max_length=2000, description="User's message about the image")


class ImageChatReply(BaseModel):
    """AI response in image conversation"""
    session_id: str = Field(..., description="Session ID")
    reply: str = Field(..., description="AI-generated response")
    conversation_history: List[ImageChatMessage] = Field(..., description="Full conversation history")


class ImageSessionInfo(BaseModel):
    """Information about an image chat session"""
    session_id: str = Field(..., description="Session ID")
    filename: str = Field(..., description="Original filename")
    image_info: Dict = Field(..., description="Image details")
    message_count: int = Field(..., description="Number of messages in conversation")
    created_at: str = Field(..., description="Session creation timestamp")


# ============================================
# DATABASE HOOKS (For Future Implementation)
# ============================================
# TODO: When implementing database storage:
# 1. Create table: csv_sessions (id, user_id, csv_file_url, created_at, metadata)
# 2. Create table: csv_conversations (id, session_id, role, content, plot_url, timestamp)
# 3. Replace in-memory storage with database queries
# 4. Store CSV files in Supabase Storage
# 5. Add user_id field to all CSV chat models