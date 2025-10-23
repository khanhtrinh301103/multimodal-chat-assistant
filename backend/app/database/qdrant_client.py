# backend/app/database/qdrant_client.py
"""
Qdrant client for vector database operations.
Handles embedding storage and retrieval with user-scoped filtering.
"""
import os
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Environment variables
QDRANT_URL = os.getenv("QDRANT_URL", "")
QDRANT_API_KEY = os.getenv("QDRANT_API_KEY", "")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")

# Collection configuration
DEFAULT_COLLECTION_NAME = "multimodal_docs"
EMBEDDING_DIMENSION = 384  # all-MiniLM-L6-v2 produces 384-dim vectors


def get_qdrant_client() -> QdrantClient | None:
    """
    Get Qdrant client for vector operations.
    
    Returns:
        QdrantClient instance or None if not configured
        
    Note:
        - For Qdrant Cloud: Requires both URL and API_KEY
        - For local: Only requires URL (usually http://localhost:6333)
    """
    if not QDRANT_URL:
        logger.warning(
            "⚠️ Qdrant not configured. "
            "Please set QDRANT_URL in .env"
        )
        return None
    
    try:
        # If URL is localhost, don't require API key
        if "localhost" in QDRANT_URL or "127.0.0.1" in QDRANT_URL:
            client = QdrantClient(url=QDRANT_URL)
            logger.info(f"✅ Qdrant client initialized (local): {QDRANT_URL}")
        else:
            # Cloud instance requires API key
            if not QDRANT_API_KEY:
                logger.warning("⚠️ QDRANT_API_KEY required for cloud instance")
                return None
            
            client = QdrantClient(
                url=QDRANT_URL,
                api_key=QDRANT_API_KEY
            )
            logger.info(f"✅ Qdrant client initialized (cloud): {QDRANT_URL}")
        
        return client
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize Qdrant client: {e}")
        return None


def ensure_collection(
    client: QdrantClient,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    dimension: int = EMBEDDING_DIMENSION,
    distance: Distance = Distance.COSINE
) -> bool:
    """
    Ensure collection exists with proper configuration.
    Creates collection if it doesn't exist.
    
    Args:
        client: Qdrant client instance
        collection_name: Name of the collection
        dimension: Vector dimension (default: 384 for all-MiniLM-L6-v2)
        distance: Distance metric (default: COSINE)
        
    Returns:
        True if collection exists or was created successfully
    """
    try:
        # Check if collection exists
        collections = client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if collection_name in collection_names:
            logger.info(f"✅ Collection '{collection_name}' already exists")
            return True
        
        # Create collection
        client.create_collection(
            collection_name=collection_name,
            vectors_config=VectorParams(
                size=dimension,
                distance=distance
            )
        )
        
        logger.info(
            f"✅ Created collection '{collection_name}' "
            f"(dim={dimension}, distance={distance.value})"
        )
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to ensure collection '{collection_name}': {e}")
        return False


# Singleton instance
_qdrant_client = None


def get_qdrant() -> QdrantClient | None:
    """
    Get singleton Qdrant client instance.
    Initializes on first call, returns cached instance thereafter.
    """
    global _qdrant_client
    
    if _qdrant_client is None:
        _qdrant_client = get_qdrant_client()
        
        # Ensure default collection exists
        if _qdrant_client:
            ensure_collection(_qdrant_client)
    
    return _qdrant_client