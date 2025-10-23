# backend/app/services/image_service.py
"""
Image chat service using Claude Sonnet 4.5 Vision API.
Supports multi-turn conversations about uploaded images.
"""
import anthropic
import os
import logging
import base64
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv
from typing import List, Dict
from datetime import datetime
import uuid

load_dotenv()
logger = logging.getLogger(__name__)

# Claude Sonnet 4.5 configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

if ANTHROPIC_API_KEY:
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    logger.info("✅ Claude Sonnet 4.5 configured for image chat")
else:
    client = None
    logger.warning("⚠️ ANTHROPIC_API_KEY not configured for image chat")

MODEL_NAME = "claude-sonnet-4-5-20250929"  # Fast, excellent vision quality
MAX_TOKENS = 4096

# In-memory storage for image chat sessions
# TODO: Replace with database (Redis/PostgreSQL) for production
image_chat_sessions = {}


def get_image_media_type(image_data: bytes) -> str:
    """
    Detect image media type from image data.
    """
    try:
        image = Image.open(BytesIO(image_data))
        format_lower = image.format.lower()
        
        if format_lower == "jpeg" or format_lower == "jpg":
            return "image/jpeg"
        elif format_lower == "png":
            return "image/png"
        elif format_lower == "gif":
            return "image/gif"
        elif format_lower == "webp":
            return "image/webp"
        else:
            return "image/jpeg"
    except Exception:
        return "image/jpeg"


async def create_image_chat_session(image_data: bytes, filename: str) -> Dict:
    """
    Create a new image chat session with uploaded image.
    
    Args:
        image_data: Raw image bytes
        filename: Original filename
        
    Returns:
        dict with session_id, message, and image_info
    """
    try:
        # Generate unique session ID
        session_id = str(uuid.uuid4())
        
        # Get image info
        image = Image.open(BytesIO(image_data))
        width, height = image.size
        format_name = image.format
        
        # Convert to base64 for storage and API
        image_base64 = base64.standard_b64encode(image_data).decode("utf-8")
        media_type = get_image_media_type(image_data)
        
        # Store session data
        image_chat_sessions[session_id] = {
            "session_id": session_id,
            "image_base64": image_base64,
            "media_type": media_type,
            "filename": filename,
            "image_info": {
                "width": width,
                "height": height,
                "format": format_name,
                "size_kb": len(image_data) / 1024
            },
            "conversation_history": [],
            "created_at": datetime.now().isoformat()
        }
        
        logger.info(f"✅ Created image chat session {session_id} for {filename}")
        
        return {
            "session_id": session_id,
            "message": f"Image uploaded successfully! You can now ask questions about this image.",
            "image_info": {
                "filename": filename,
                "width": width,
                "height": height,
                "format": format_name,
                "size_kb": round(len(image_data) / 1024, 2)
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to create image chat session: {e}")
        raise Exception(f"Failed to create image chat session: {str(e)}")


async def chat_with_image(session_id: str, user_message: str) -> Dict:
    """
    Continue conversation about the uploaded image.
    
    Args:
        session_id: Unique session ID
        user_message: User's question about the image
        
    Returns:
        dict with reply and conversation history
    """
    if not client:
        return {
            "reply": "⚠️ Anthropic API key not configured. Please add ANTHROPIC_API_KEY to your .env file.",
            "conversation_history": []
        }
    
    # Check if session exists
    if session_id not in image_chat_sessions:
        return {
            "reply": "⚠️ Session not found. Please upload an image first.",
            "conversation_history": []
        }
    
    session = image_chat_sessions[session_id]
    
    try:
        logger.info(f"💬 Image chat - Session {session_id[:8]}... - Question: {user_message[:50]}...")
        
        # Build conversation history for Claude
        # First message always includes the image
        messages = []
        
        # Add conversation history (without image in follow-ups to save tokens)
        for msg in session["conversation_history"]:
            messages.append({
                "role": msg["role"],
                "content": msg["content"]
            })
        
        # Add current user message with image reference
        # Include image in every request to maintain context
        current_content = [
            {
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": session["media_type"],
                    "data": session["image_base64"],
                },
            },
            {
                "type": "text",
                "text": user_message
            }
        ]
        
        messages.append({
            "role": "user",
            "content": current_content
        })
        
        # Call Claude API
        response = client.messages.create(
            model=MODEL_NAME,
            max_tokens=MAX_TOKENS,
            messages=messages
        )
        
        assistant_reply = response.content[0].text.strip()
        
        # Add to conversation history
        session["conversation_history"].append({
            "role": "user",
            "content": user_message,
            "timestamp": datetime.now().isoformat()
        })
        
        session["conversation_history"].append({
            "role": "assistant",
            "content": assistant_reply,
            "timestamp": datetime.now().isoformat()
        })
        
        logger.info(f"✅ Image chat response generated for session {session_id[:8]}...")
        
        return {
            "reply": assistant_reply,
            "conversation_history": session["conversation_history"]
        }
        
    except anthropic.RateLimitError as e:
        logger.error(f"⚠️ Rate limit exceeded: {e}")
        return {
            "reply": "⚠️ Rate limit reached (5 requests/min). Please wait a moment and try again.",
            "conversation_history": session["conversation_history"]
        }
    except anthropic.APIError as e:
        logger.error(f"❌ Anthropic API error: {e}")
        return {
            "reply": f"⚠️ API error: {str(e)}",
            "conversation_history": session["conversation_history"]
        }
    except Exception as e:
        logger.error(f"❌ Image chat error: {e}")
        return {
            "reply": f"⚠️ Error: {str(e)}",
            "conversation_history": session["conversation_history"]
        }


async def get_session_info(session_id: str) -> Dict:
    """
    Get information about an image chat session.
    """
    if session_id not in image_chat_sessions:
        return None
    
    session = image_chat_sessions[session_id]
    return {
        "session_id": session_id,
        "filename": session["filename"],
        "image_info": session["image_info"],
        "message_count": len(session["conversation_history"]),
        "created_at": session["created_at"]
    }


async def delete_session(session_id: str) -> bool:
    """
    Delete an image chat session.
    """
    if session_id in image_chat_sessions:
        del image_chat_sessions[session_id]
        logger.info(f"🗑️ Deleted image chat session {session_id}")
        return True
    return False