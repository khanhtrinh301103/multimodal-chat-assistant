from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import auth, chat, image, csv, history  # Add history
import logging

from app.routers import auth, chat, image, csv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Multi-Modal Chat Assistant API",
    description="Backend for text, image, and CSV-based conversational AI",
    version="0.1.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # Frontend origin
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/auth", tags=["auth"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(image.router, prefix="/image", tags=["image"])
app.include_router(csv.router, prefix="/csv", tags=["csv"])
app.include_router(history.router, prefix="/history", tags=["history"]) 


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "multimodal-chat-api"}


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Multi-Modal Chat Assistant API",
        "docs": "/docs",
        "health": "/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)