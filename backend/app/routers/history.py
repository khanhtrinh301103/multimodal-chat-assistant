# backend/app/routers/history.py
from fastapi import APIRouter, HTTPException, Depends
from app.utils.jwt_verify import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{conversation_id}")
async def get_conversation_history(
    conversation_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get all messages for a conversation.
    
    Requires authentication.
    TODO: Implement database retrieval when Supabase is configured
    """
    try:
        logger.info(f"Fetching history for conversation: {conversation_id}")
        
        # Stub implementation - return empty for now
        return {
            "conversation_id": conversation_id,
            "messages": []
        }
    except Exception as e:
        logger.error(f"History retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve history: {str(e)}")


@router.delete("/{conversation_id}")
async def delete_conversation(
    conversation_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete a conversation and all its messages.
    
    Requires authentication.
    TODO: Implement database deletion when Supabase is configured
    """
    try:
        logger.info(f"Deleting conversation: {conversation_id}")
        
        return {
            "message": "Conversation deleted",
            "conversation_id": conversation_id
        }
    except Exception as e:
        logger.error(f"Deletion error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete conversation: {str(e)}")