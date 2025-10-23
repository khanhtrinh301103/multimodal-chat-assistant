# backend/app/routers/image.py
"""
Image chat router - Upload image and have conversations about it.
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form, Depends
from app.models.dto import (
    ImageChatUploadResponse, 
    ImageChatRequest, 
    ImageChatReply,
    ImageSessionInfo
)
from app.services.image_service import (
    create_image_chat_session,
    chat_with_image,
    get_session_info,
    delete_session
)
from app.utils.jwt_verify import get_current_user
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

# TODO: Scope sessions by user_id when migrating to database


@router.post("/upload", response_model=ImageChatUploadResponse)
async def upload_image(
    image: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload an image to start a new chat session.
    Returns a session_id for ongoing conversations.
    
    Requires authentication.
    """
    try:
        # Validate file type
        if not image.content_type or not image.content_type.startswith('image/'):
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Please upload a PNG or JPG image."
            )
        
        # Read image data
        image_data = await image.read()
        
        if len(image_data) == 0:
            raise HTTPException(
                status_code=400,
                detail="Empty image file."
            )
        
        logger.info(f"📤 Uploading image: {image.filename} ({len(image_data)/1024:.2f} KB)")
        
        # Create chat session
        result = await create_image_chat_session(image_data, image.filename)
        
        logger.info(f"✅ Image chat session created: {result['session_id']}")
        
        return ImageChatUploadResponse(**result)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Image upload error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to upload image: {str(e)}"
        )


@router.post("/chat", response_model=ImageChatReply)
async def chat(
    request: ImageChatRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Send a message about the uploaded image.
    Maintains conversation history within the session.
    
    Requires authentication.
    """
    try:
        logger.info(f"💬 Image chat message - Session: {request.session_id[:8]}...")
        
        # Chat with image
        result = await chat_with_image(request.session_id, request.message)
        
        if "⚠️ Session not found" in result["reply"]:
            raise HTTPException(
                status_code=404,
                detail="Session not found. Please upload an image first."
            )
        
        logger.info(f"✅ Chat response generated")
        
        return ImageChatReply(
            session_id=request.session_id,
            reply=result["reply"],
            conversation_history=result["conversation_history"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Chat error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/session/{session_id}", response_model=ImageSessionInfo)
async def get_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get information about an image chat session.
    
    Requires authentication.
    """
    try:
        info = await get_session_info(session_id)
        
        if not info:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        return ImageSessionInfo(**info)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching session info: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to get session info: {str(e)}"
        )


@router.delete("/session/{session_id}")
async def delete_chat_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Delete an image chat session.
    
    Requires authentication.
    """
    try:
        success = await delete_session(session_id)
        
        if not success:
            raise HTTPException(
                status_code=404,
                detail="Session not found"
            )
        
        return {"message": "Session deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error deleting session: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to delete session: {str(e)}"
        )