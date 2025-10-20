from fastapi import APIRouter, HTTPException
from app.models.dto import ImageIn, ImageReply
from app.services.image_service import generate_image_caption
import logging

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/", response_model=ImageReply)
async def image_chat_endpoint(image_in: ImageIn):
    """
    Image caption and Q&A endpoint.
    
    TODO: Integrate HuggingFace image captioning model (e.g., BLIP, ViT-GPT2)
    TODO: Add image validation and size limits
    TODO: Support base64 encoded images in addition to URLs
    """
    try:
        logger.info(f"Received image Q&A request: {image_in.question[:30]}...")
        caption = await generate_image_caption(image_in.imageUrl, image_in.question)
        return ImageReply(caption=caption, answer=caption)
    except Exception as e:
        logger.error(f"Image processing error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")