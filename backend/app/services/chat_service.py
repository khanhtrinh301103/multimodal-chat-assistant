# backend/app/services/chat_service.py
"""
Chat service - Google Gemini API (NEW SDK)
"""
from google import genai
import os
import logging
from typing import List, Dict, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Configuration
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Configure Gemini Client
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    logger.info("✅ Gemini client configured for chat")
else:
    client = None
    logger.warning("⚠️ GOOGLE_API_KEY not configured")


async def generate_chat_response(
    message: str,
    conversation_history: List[Dict] = None,
    stream: bool = False,
    gen_params: Optional[Dict] = None
) -> str:
    """
    Generate AI response using Google Gemini (NEW SDK).
    """
    if not client:
        return "⚠️ Google Gemini API key not configured. Please add GOOGLE_API_KEY to your .env file."
    
    try:
        # Build conversation context
        context = _build_context(conversation_history, message)
        
        logger.info(f"🤖 Calling Gemini API...")
        logger.info(f"📝 Context length: {len(context)} chars")
        
        # Generate response using NEW SDK
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=context
        )
        
        ai_response = response.text.strip()
        
        logger.info(f"✅ Generated response: {len(ai_response)} chars")
        
        return ai_response
        
    except Exception as e:
        logger.error(f"❌ Gemini error: {e}")
        return _fallback_response(message, conversation_history)


def _build_context(history: List[Dict], current_message: str) -> str:
    """Build conversation context for Gemini."""
    context_parts = ["You are a helpful AI assistant. Be concise and natural.\n"]
    
    # Add recent history
    if history and len(history) > 0:
        recent = history[-10:] if len(history) > 10 else history
        
        for msg in recent:
            role = msg.get("role", "")
            content = msg.get("content", "")
            
            if role == "user":
                context_parts.append(f"User: {content}")
            elif role == "assistant":
                context_parts.append(f"Assistant: {content}")
    
    # Add current message
    context_parts.append(f"User: {current_message}")
    context_parts.append("Assistant:")
    
    return "\n".join(context_parts)


def _fallback_response(message: str, history: List[Dict] = None) -> str:
    """Smart fallback when API fails."""
    message_lower = message.lower()
    
    # Extract name from history
    user_name = None
    if history:
        for msg in history:
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                if "my name is" in content:
                    try:
                        name = content.split("my name is")[1].split()[0].strip('.,!?').title()
                        user_name = name
                    except:
                        pass
    
    # Smart responses
    if any(q in message_lower for q in ["what is my name", "my name", "who am i"]):
        if user_name:
            return f"Your name is {user_name}!"
        return "I don't think you've told me your name yet."
    
    if any(word in message_lower for word in ["hello", "hi", "hey"]):
        if user_name:
            return f"Hello {user_name}! How can I help you?"
        return "Hello! I'm your AI assistant. How can I help you today?"
    
    if "thank" in message_lower:
        return "You're welcome!"
    
    return "I'm here to help! What would you like to know?"