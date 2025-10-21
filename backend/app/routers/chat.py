# backend/app/routers/chat.py
"""
Chat router - Multi-turn text conversation.
"""
from fastapi import APIRouter, HTTPException
from app.models.dto import ChatRequest, ChatReply
from app.services.chat_service import generate_chat_response
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)

# In-memory conversation storage
conversations = {}


@router.post("/", response_model=ChatReply)
async def chat_endpoint(request: ChatRequest):
    """
    Text chat with AI that remembers conversation history.
    Uses HuggingFace Inference API (Phi-3.5-mini-instruct).
    """
    try:
        # Create new conversation if needed
        conversation_id = request.conversation_id
        if not conversation_id or conversation_id not in conversations:
            conversation_id = str(uuid.uuid4())
            conversations[conversation_id] = []
            logger.info(f"Created new conversation: {conversation_id}")
        
        # Get conversation history
        history = conversations[conversation_id]
        
        # Add user message to history
        user_message = {
            "role": "user",
            "content": request.message,
            "timestamp": datetime.utcnow().isoformat()
        }
        history.append(user_message)
        
        # Generate AI response using HF Inference API
        ai_response = await generate_chat_response(request.message, history)
        
        # Add AI response to history
        assistant_message = {
            "role": "assistant",
            "content": ai_response,
            "timestamp": datetime.utcnow().isoformat()
        }
        history.append(assistant_message)
        
        # Update conversation
        conversations[conversation_id] = history
        
        logger.info(f"Chat exchange in conversation {conversation_id}")
        
        return ChatReply(
            reply=ai_response,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/history/{conversation_id}")
async def get_chat_history(conversation_id: str):
    """Get all messages in a conversation."""
    if conversation_id not in conversations:
        return {"conversation_id": conversation_id, "messages": []}
    
    return {
        "conversation_id": conversation_id,
        "messages": conversations[conversation_id]
    }