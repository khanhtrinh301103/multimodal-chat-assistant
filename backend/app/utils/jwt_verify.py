# backend/app/utils/jwt_verify.py
"""
JWT verification utilities for Supabase Auth.
Supports both RSA (RS256) and EC (ES256) keys.
"""
import os
import jwt
import requests
from typing import Optional
from fastapi import HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from functools import lru_cache
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# Environment configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_JWT_AUD = os.getenv("SUPABASE_JWT_AUD", "authenticated")

# Security scheme for FastAPI docs
security = HTTPBearer()


@lru_cache(maxsize=1)
def get_jwks_url() -> str:
    """Get JWKS URL for Supabase project."""
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL not configured in environment")
    
    base_url = SUPABASE_URL.rstrip('/')
    return f"{base_url}/auth/v1/.well-known/jwks.json"


@lru_cache(maxsize=1)
def get_issuer() -> str:
    """Get expected JWT issuer for Supabase project."""
    if not SUPABASE_URL:
        raise ValueError("SUPABASE_URL not configured in environment")
    
    base_url = SUPABASE_URL.rstrip('/')
    return f"{base_url}/auth/v1"


@lru_cache(maxsize=1)
def fetch_jwks() -> dict:
    """
    Fetch JWKS (JSON Web Key Set) from Supabase.
    Cached for performance.
    """
    try:
        jwks_url = get_jwks_url()
        logger.info(f"Fetching JWKS from: {jwks_url}")
        
        response = requests.get(jwks_url, timeout=10)
        response.raise_for_status()
        
        jwks = response.json()
        logger.info(f"✅ JWKS fetched successfully ({len(jwks.get('keys', []))} keys)")
        return jwks
        
    except Exception as e:
        logger.error(f"❌ Failed to fetch JWKS: {e}")
        raise HTTPException(
            status_code=500,
            detail="Failed to fetch authentication keys"
        )


def get_signing_key(token: str) -> Optional[any]:
    """
    Get the signing key for JWT verification from JWKS.
    Supports both RSA (RS256) and EC (ES256) keys.
    
    Args:
        token: JWT token string
        
    Returns:
        Public key or None
    """
    try:
        # Decode header without verification to get kid and alg
        unverified_header = jwt.get_unverified_header(token)
        kid = unverified_header.get("kid")
        
        if not kid:
            logger.warning("⚠️ JWT missing 'kid' in header")
            return None
        
        # Get JWKS
        jwks = fetch_jwks()
        
        # Find matching key
        for key in jwks.get("keys", []):
            if key.get("kid") == kid:
                # Get algorithm from key
                alg = key.get("alg", "RS256")
                
                logger.info(f"🔑 Found matching key: kid={kid}, alg={alg}")
                
                # Convert JWK to public key based on algorithm
                if alg.startswith("RS"):
                    # RSA key
                    from jwt.algorithms import RSAAlgorithm
                    public_key = RSAAlgorithm.from_jwk(key)
                    return public_key
                elif alg.startswith("ES"):
                    # Elliptic Curve key
                    from jwt.algorithms import ECAlgorithm
                    public_key = ECAlgorithm.from_jwk(key)
                    return public_key
                else:
                    logger.warning(f"⚠️ Unsupported algorithm: {alg}")
                    return None
        
        logger.warning(f"⚠️ No matching key found for kid: {kid}")
        return None
        
    except Exception as e:
        logger.error(f"❌ Error getting signing key: {e}")
        return None


def verify_jwt(token: str) -> dict:
    """
    Verify Supabase JWT token using JWKS.
    Supports both RS256 (RSA) and ES256 (Elliptic Curve) algorithms.
    
    Args:
        token: JWT token string
        
    Returns:
        dict: Decoded JWT payload with claims
        
    Raises:
        HTTPException: 401 if token is invalid
    """
    if not SUPABASE_URL:
        raise HTTPException(
            status_code=500,
            detail="Supabase not configured. Please set SUPABASE_URL in environment."
        )
    
    try:
        # Get signing key
        signing_key = get_signing_key(token)
        
        if not signing_key:
            raise HTTPException(
                status_code=401,
                detail="Unable to verify token: signing key not found"
            )
        
        # Get expected issuer
        expected_issuer = get_issuer()
        
        # Detect algorithm from token header
        unverified_header = jwt.get_unverified_header(token)
        algorithm = unverified_header.get("alg", "RS256")
        
        logger.info(f"🔐 Verifying token with algorithm: {algorithm}")
        
        # Verify and decode JWT
        payload = jwt.decode(
            token,
            signing_key,
            algorithms=[algorithm],  # Use detected algorithm
            audience=SUPABASE_JWT_AUD,
            issuer=expected_issuer,
            options={
                "verify_signature": True,
                "verify_exp": True,
                "verify_aud": True,
                "verify_iss": True,
            }
        )
        
        # Validate required claims
        if "sub" not in payload:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing 'sub' claim"
            )
        
        logger.info(f"✅ JWT verified for user: {payload['sub'][:8]}...")
        return payload
        
    except jwt.ExpiredSignatureError:
        logger.warning("⚠️ Token expired")
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidIssuerError:
        logger.warning("⚠️ Invalid token issuer")
        raise HTTPException(
            status_code=401,
            detail="Invalid token issuer"
        )
    except jwt.InvalidAudienceError:
        logger.warning("⚠️ Invalid token audience")
        raise HTTPException(
            status_code=401,
            detail="Invalid token audience"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"⚠️ Invalid token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )
    except Exception as e:
        logger.error(f"❌ JWT verification error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Token verification failed"
        )


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> str:
    """
    FastAPI dependency to extract and verify user_id from JWT.
    
    Returns:
        str: User ID (from JWT 'sub' claim)
    """
    token = credentials.credentials
    
    # Verify JWT and extract payload
    payload = verify_jwt(token)
    
    # Extract user_id from 'sub' claim
    user_id = payload.get("sub")
    
    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="Invalid token: missing user identifier"
        )
    
    return user_id


# Backward compatibility
def verify_bearer_or_401(request) -> dict:
    """Legacy function for backward compatibility."""
    auth_header = request.headers.get("Authorization")
    
    if not auth_header:
        raise HTTPException(
            status_code=401,
            detail="Missing Authorization header"
        )
    
    if not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid Authorization header format"
        )
    
    token = auth_header.replace("Bearer ", "")
    payload = verify_jwt(token)
    
    return {
        "user_id": payload.get("sub"),
        "email": payload.get("email"),
        "token": token[:20] + "..."
    }