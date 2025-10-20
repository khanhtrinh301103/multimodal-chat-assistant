"""
Image service - Business logic for image captioning and visual Q&A.
"""


async def generate_image_caption(image_url: str, question: str) -> str:
    """
    Generate caption or answer question about an image.
    
    TODO: Load HuggingFace image captioning model (e.g., Salesforce/blip-image-captioning-base)
    TODO: Download image from URL and preprocess
    TODO: Implement Q&A logic combining caption with question context
    
    Args:
        image_url: URL of the image to analyze
        question: User's question about the image
        
    Returns:
        Caption or answer text
    """
    # Stub implementation
    return f"[STUB] Image at '{image_url[:50]}...' - Question: '{question}' - Real vision model integration pending."