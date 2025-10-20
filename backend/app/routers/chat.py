from fastapi import APIRouter, HTTPException
from app.models.dto import MessageIn, ChatReply
from app.services.chat_service import generate_chat_response
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ChatReply)
async def chat_endpoint(message_in: MessageIn):
    """
    Text-based multi-turn chat endpoint.
    
    TODO: Integrate HuggingFace text generation model (e.g., GPT-2, Flan-T5)
    TODO: Implement conversation history tracking with user sessions
    """
    try:
        logger.info(f"Received chat message: {message_in.message[:50]}...")
        reply_text = await generate_chat_response(message_in.message)
        return ChatReply(reply=reply_text)
    except Exception as e:
        logger.error(f"Chat error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Chat processing failed: {str(e)}")