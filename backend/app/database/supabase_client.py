# backend/app/database/supabase_client.py
"""
Supabase client for backend (server-side operations).
Uses SERVICE_ROLE_KEY for full access to database and storage.

SECURITY: This client should NEVER be exposed to the frontend.
"""
import os
from supabase import create_client, Client
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Environment variables
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY", "")


def get_supabase_client() -> Client | None:
    """
    Get Supabase client for backend operations.
    
    Returns:
        Supabase client instance or None if not configured
        
    Security:
        - Uses SERVICE_ROLE_KEY (bypasses RLS for admin operations)
        - Should only be used in backend, never exposed to frontend
        - All user-scoped operations must filter by user_id explicitly
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        logger.warning(
            "⚠️ Supabase not configured. "
            "Please set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env"
        )
        return None
    
    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
        logger.info("✅ Supabase client initialized (server-side)")
        return client
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")
        return None


# Singleton instance
_supabase_client = None


def get_supabase() -> Client | None:
    """
    Get singleton Supabase client instance.
    Initializes on first call, returns cached instance thereafter.
    """
    global _supabase_client
    
    if _supabase_client is None:
        _supabase_client = get_supabase_client()
    
    return _supabase_client