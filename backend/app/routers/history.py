# backend/app/routers/history.py
from fastapi import APIRouter, HTTPException
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/{conversation_id}")
async def get_conversation_history(conversation_id: str):
    """
    Get all messages for a conversation.
    
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
async def delete_conversation(conversation_id: str):
    """
    Delete a conversation and all its messages.
    
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