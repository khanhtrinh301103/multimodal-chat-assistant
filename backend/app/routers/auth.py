from fastapi import APIRouter, Request, HTTPException
from app.utils.jwt_verify import verify_bearer_or_401

router = APIRouter()


@router.get("/me")
async def get_current_user(request: Request):
    """
    Mock authentication endpoint.
    Verifies Bearer token format and returns a fake user.
    
    TODO: Replace with real JWT verification (Supabase/Firebase JWKS)
    """
    try:
        user_info = verify_bearer_or_401(request)
        return {
            "user_id": user_info["user_id"],
            "email": "demo@example.com",
            "authenticated": True
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth error: {str(e)}")