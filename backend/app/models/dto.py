"""
Data Transfer Objects - Pydantic models for request/response validation.
"""
from pydantic import BaseModel, Field, HttpUrl
from typing import Optional


# Chat DTOs
class MessageIn(BaseModel):
    message: str = Field(..., min_length=1, max_length=5000, description="User's chat message")


class ChatReply(BaseModel):
    reply: str = Field(..., description="AI-generated response")


# Image DTOs
class ImageIn(BaseModel):
    imageUrl: HttpUrl = Field(..., description="URL of the image to analyze")
    question: str = Field(..., min_length=1, max_length=500, description="Question about the image")


class ImageReply(BaseModel):
    caption: str = Field(..., description="Image caption or description")
    answer: str = Field(..., description="Answer to the user's question")


# CSV DTOs
class CsvInUrl(BaseModel):
    csvUrl: HttpUrl = Field(..., description="URL of the CSV file")
    prompt: str = Field(..., min_length=1, max_length=1000, description="Analysis request or question")


class CsvReply(BaseModel):
    summary: str = Field(..., description="Analysis summary or insights")
    plot_base64: Optional[str] = Field(None, description="Base64-encoded plot image (PNG)")