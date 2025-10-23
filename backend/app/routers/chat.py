# backend/app/routers/chat.py
"""
Chat router - Multi-turn text conversation.
"""
from fastapi import APIRouter, HTTPException, Depends
from app.models.dto import ChatRequest, ChatReply
from app.services.chat_service import generate_chat_response, load_conversation_from_db
from app.utils.jwt_verify import get_current_user
from datetime import datetime
import logging
import uuid

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatReply)
async def chat_endpoint(
    request: ChatRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Text chat with AI that remembers conversation history.
    Requires authentication.
    """
    try:
        # Create new conversation if needed
        conversation_id = request.conversation_id
        if not conversation_id:
            conversation_id = str(uuid.uuid4())
            logger.info(f"Created new conversation: {conversation_id}")
        
        # Generate AI response (service handles DB persistence)
        ai_response = await generate_chat_response(
            request.message,
            conversation_history=None,  # Service loads from DB
            user_id=user_id,
            conversation_id=conversation_id,
            save_to_db=True
        )
        
        logger.info(f"Chat exchange in conversation {conversation_id}")
        
        return ChatReply(
            reply=ai_response,
            conversation_id=conversation_id
        )
        
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")


@router.get("/history/{conversation_id}")
async def get_chat_history(
    conversation_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get all messages in a conversation from database.
    Requires authentication.
    """
    try:
        # Load conversation from database
        messages = await load_conversation_from_db(user_id, conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "messages": messages
        }
        
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to retrieve conversation history: {str(e)}"
        )