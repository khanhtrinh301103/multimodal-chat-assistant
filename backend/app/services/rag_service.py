# backend/app/services/rag_service.py
"""
RAG (Retrieval-Augmented Generation) service.
Handles text embedding, chunking, vector storage, and semantic search.
"""
import os
from typing import List, Dict, Optional
from sentence_transformers import SentenceTransformer
from qdrant_client.models import PointStruct, Filter, FieldCondition, MatchValue
import logging
from dotenv import load_dotenv
import uuid

load_dotenv()
logger = logging.getLogger(__name__)

# Configuration
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL", "sentence-transformers/all-MiniLM-L6-v2")
CHUNK_SIZE = 500  # Characters per chunk
CHUNK_OVERLAP = 50  # Overlap between chunks
DEFAULT_COLLECTION = "multimodal_docs"

# Load embedding model (cached globally)
_embedding_model = None


def get_embedding_model() -> SentenceTransformer:
    """
    Get or initialize the embedding model.
    Model is cached to avoid reloading on every request.
    """
    global _embedding_model
    
    if _embedding_model is None:
        try:
            logger.info(f"📥 Loading embedding model: {EMBEDDING_MODEL_NAME}")
            _embedding_model = SentenceTransformer(EMBEDDING_MODEL_NAME)
            logger.info(f"✅ Embedding model loaded: {EMBEDDING_MODEL_NAME}")
        except Exception as e:
            logger.error(f"❌ Failed to load embedding model: {e}")
            raise
    
    return _embedding_model


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> List[str]:
    """
    Split text into overlapping chunks.
    
    Args:
        text: Text to chunk
        chunk_size: Maximum characters per chunk
        overlap: Number of overlapping characters between chunks
        
    Returns:
        List of text chunks
    """
    if len(text) <= chunk_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        
        # Avoid cutting words in half
        if end < len(text) and text[end] not in [' ', '\n', '\t', '.', ',']:
            # Find last space before end
            last_space = chunk.rfind(' ')
            if last_space > 0:
                end = start + last_space
                chunk = text[start:end]
        
        chunks.append(chunk.strip())
        start = end - overlap
    
    return chunks


def embed_text(text: str) -> List[float]:
    """
    Generate embedding vector for text.
    
    Args:
        text: Text to embed
        
    Returns:
        384-dimensional embedding vector
    """
    model = get_embedding_model()
    embedding = model.encode(text, convert_to_numpy=True)
    return embedding.tolist()


def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Generate embedding vectors for multiple texts (batch processing).
    
    Args:
        texts: List of texts to embed
        
    Returns:
        List of 384-dimensional embedding vectors
    """
    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True, show_progress_bar=len(texts) > 10)
    return embeddings.tolist()


async def upsert_document(
    qdrant_client,
    user_id: str,
    file_id: str,
    text: str,
    metadata: Optional[Dict] = None,
    collection_name: str = DEFAULT_COLLECTION
) -> Dict:
    """
    Chunk text, embed, and upsert to Qdrant with user_id filtering.
    
    Args:
        qdrant_client: Qdrant client instance
        user_id: User ID for access control
        file_id: Unique file identifier
        text: Text content to process
        metadata: Additional metadata (filename, source, etc.)
        collection_name: Qdrant collection name
        
    Returns:
        dict with status, chunk_count, and file_id
    """
    try:
        # Chunk text
        chunks = chunk_text(text)
        logger.info(f"📄 Split document into {len(chunks)} chunks")
        
        # Generate embeddings (batch process for efficiency)
        embeddings = embed_texts(chunks)
        logger.info(f"🔢 Generated {len(embeddings)} embeddings")
        
        # Prepare points for Qdrant
        points = []
        for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
            point_id = str(uuid.uuid4())
            
            payload = {
                "user_id": user_id,
                "file_id": file_id,
                "chunk_index": i,
                "text": chunk,
                **(metadata or {})
            }
            
            point = PointStruct(
                id=point_id,
                vector=embedding,
                payload=payload
            )
            points.append(point)
        
        # Upsert to Qdrant
        qdrant_client.upsert(
            collection_name=collection_name,
            points=points
        )
        
        logger.info(f"✅ Upserted {len(points)} vectors to Qdrant (file_id={file_id})")
        
        return {
            "status": "success",
            "chunk_count": len(chunks),
            "file_id": file_id
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to upsert document: {e}")
        raise


async def search_similar(
    qdrant_client,
    user_id: str,
    query: str,
    limit: int = 5,
    collection_name: str = DEFAULT_COLLECTION
) -> List[Dict]:
    """
    Search for similar text chunks with user_id filtering.
    
    Args:
        qdrant_client: Qdrant client instance
        user_id: User ID for access control (REQUIRED)
        query: Search query text
        limit: Maximum number of results
        collection_name: Qdrant collection name
        
    Returns:
        List of matching chunks with scores and metadata
    """
    try:
        # Embed query
        query_embedding = embed_text(query)
        logger.info(f"🔍 Searching for: '{query[:50]}...'")
        
        # Search with user_id filter (SECURITY: prevents cross-user data access)
        results = qdrant_client.search(
            collection_name=collection_name,
            query_vector=query_embedding,
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="user_id",
                        match=MatchValue(value=user_id)
                    )
                ]
            ),
            limit=limit,
            with_payload=True
        )
        
        # Format results
        formatted_results = []
        for result in results:
            formatted_results.append({
                "text": result.payload.get("text", ""),
                "score": result.score,
                "file_id": result.payload.get("file_id", ""),
                "chunk_index": result.payload.get("chunk_index", 0),
                "metadata": {
                    k: v for k, v in result.payload.items()
                    if k not in ["text", "user_id", "file_id", "chunk_index"]
                }
            })
        
        logger.info(f"✅ Found {len(formatted_results)} matching chunks")
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"❌ Search failed: {e}")
        raise


async def delete_user_vectors(
    qdrant_client,
    user_id: str,
    file_id: Optional[str] = None,
    collection_name: str = DEFAULT_COLLECTION
) -> bool:
    """
    Delete vectors for a user (optionally filtered by file_id).
    
    Args:
        qdrant_client: Qdrant client instance
        user_id: User ID
        file_id: Optional file ID to delete specific file only
        collection_name: Qdrant collection name
        
    Returns:
        True if deletion succeeded
    """
    try:
        # Build filter
        filter_conditions = [
            FieldCondition(key="user_id", match=MatchValue(value=user_id))
        ]
        
        if file_id:
            filter_conditions.append(
                FieldCondition(key="file_id", match=MatchValue(value=file_id))
            )
        
        # Delete points matching filter
        qdrant_client.delete(
            collection_name=collection_name,
            points_selector=Filter(must=filter_conditions)
        )
        
        target = f"file {file_id}" if file_id else "all files"
        logger.info(f"🗑️ Deleted vectors for user {user_id} ({target})")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to delete vectors: {e}")
        return False