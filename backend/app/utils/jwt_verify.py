# backend/app/utils/jwt_verify.py
"""
JWT verification utilities.
"""
from fastapi import Request, HTTPException


def verify_bearer_or_401(request: Request) -> dict:
    """
    Mock JWT verification - checks Bearer token format only.
    
    TODO: Implement real JWT verification using:
    - Supabase: Verify JWT with Supabase JWKS endpoint
    - Firebase: Verify token with Firebase Admin SDK
    - Custom: Decode and verify signature with secret key
    
    Args:
        request: FastAPI request object
        
    Returns:
        dict with user information (currently mocked)
        
    Raises:
        HTTPException: 401 if Authorization header is missing or invalid format
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format. Expected 'Bearer <token>'"
        )
    
    token = auth_header.replace("Bearer ", "")
    
    if len(token) < 10:  # Basic sanity check
        raise HTTPException(
            status_code=401,
            detail="Invalid token format"
        )
    
    # Mock user info - replace with real JWT decode
    return {
        "user_id": "demo-user-12345",
        "token": token[:20] + "..."  # Truncated for logging
    }