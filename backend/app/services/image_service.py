# backend/app/services/image_service.py
"""
Image analysis service using Google Gemini Vision (NEW SDK).
"""
from google import genai
import os
import logging
from PIL import Image
from io import BytesIO
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")

# Configure Gemini
if GOOGLE_API_KEY:
    client = genai.Client(api_key=GOOGLE_API_KEY)
    logger.info("✅ Gemini Vision client configured")
else:
    client = None
    logger.warning("⚠️ GOOGLE_API_KEY not configured")


async def analyze_image(image_data: bytes, question: str) -> dict:
    """
    Analyze image and answer question using Gemini Vision (NEW SDK).
    """
    if not client:
        return {
            "caption": "Image analysis unavailable",
            "answer": "⚠️ Google Gemini API key not configured. Please add GOOGLE_API_KEY to your .env file."
        }
    
    try:
        # Open image
        image = Image.open(BytesIO(image_data))
        
        logger.info(f"🖼️ Analyzing image: {image.size}, question: {question[:50]}...")
        
        # Generate caption
        caption_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=["Describe this image in one concise sentence.", image]
        )
        caption = caption_response.text.strip()
        
        # Answer question
        answer_response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[f"Based on this image, answer: {question}", image]
        )
        answer = answer_response.text.strip()
        
        logger.info(f"✅ Image analysis complete")
        
        return {
            "caption": caption,
            "answer": answer
        }
        
    except Exception as e:
        logger.error(f"❌ Image analysis error: {e}")
        return {
            "caption": "Error analyzing image",
            "answer": f"⚠️ Error: {str(e)}"
        }