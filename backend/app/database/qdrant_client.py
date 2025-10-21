# backend/app/database/qdrant_client.py
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams
import os
from dotenv import load_dotenv

load_dotenv()

qdrant_url = os.getenv("QDRANT_URL", "http://localhost:6333")
qdrant_api_key = os.getenv("QDRANT_API_KEY", None)

# Initialize Qdrant client (using in-memory for now, can switch to cloud)
qdrant: QdrantClient = None

try:
    if qdrant_api_key:
        qdrant = QdrantClient(url=qdrant_url, api_key=qdrant_api_key)
    else:
        # Use in-memory for development (no Docker needed)
        qdrant = QdrantClient(":memory:")
    
    # Create collection for chat embeddings
    try:
        qdrant.create_collection(
            collection_name="chat_embeddings",
            vectors_config=VectorParams(size=384, distance=Distance.COSINE)
        )
        print("✓ Qdrant collection 'chat_embeddings' created")
    except:
        print("✓ Qdrant collection already exists")
    
    print("✓ Qdrant connected successfully")
except Exception as e:
    print(f"⚠️ Qdrant connection failed: {e}")


def get_qdrant() -> QdrantClient:
    """Get Qdrant client instance"""
    if qdrant is None:
        raise Exception("Qdrant not initialized")
    return qdrant