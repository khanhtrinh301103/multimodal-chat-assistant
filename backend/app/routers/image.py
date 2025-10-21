# backend/app/routers/image.py
"""
Image router - Upload image and ask questions about it.
"""
from fastapi import APIRouter, HTTPException, File, UploadFile, Form
from app.models.dto import ImageReply
from app.services.image_service import analyze_image
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ImageReply)
async def analyze_image_endpoint(
    image: UploadFile = File(...),
    question: str = Form(...)
):
    """
    Upload an image and ask a question about it.
    Uses Google Gemini Vision for analysis.
    """
    try:
        # Read image data
        image_data = await image.read()
        
        logger.info(f"📸 Processing image: {image.filename}, question: {question[:50]}...")
        
        # Analyze image
        result = await analyze_image(image_data, question)
        
        logger.info(f"✅ Image analysis complete")
        
        return ImageReply(
            caption=result["caption"],
            answer=result["answer"]
        )
        
    except Exception as e:
        logger.error(f"❌ Image analysis error: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Image analysis failed: {str(e)}"
        )