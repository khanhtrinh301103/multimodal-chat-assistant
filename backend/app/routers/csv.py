# backend/app/routers/csv.py
"""
CSV router - Upload CSV or provide URL for data analysis with AI chatbot capabilities.
"""
from fastapi import APIRouter, HTTPException, UploadFile, File, Depends
from app.models.dto import (
    CsvInUrl, CsvReply, 
    CsvUploadResponse, CsvChatRequest, CsvChatReply
)
from app.services.csv_service import (
    analyze_csv,
    create_csv_session,
    chat_with_csv,
    get_session_info
)
from app.utils.jwt_verify import get_current_user
import logging
import httpx

router = APIRouter()
logger = logging.getLogger(__name__)


# ============================================
# ORIGINAL ENDPOINTS (Backward Compatibility)
# TODO: Scope sessions by user_id when migrating to database
# ============================================

@router.post("/url", response_model=CsvReply)
async def analyze_csv_url(
    request: CsvInUrl,
    user_id: str = Depends(get_current_user)
):
    """
    Analyze CSV from a URL (single-shot analysis).
    Supports questions like: "Summarize", "Show stats", "Missing values", "Plot histogram"
    
    Requires authentication.
    Note: Use /chat endpoints for multi-turn conversations.
    """
    try:
        logger.info(f"📊 Fetching CSV from URL: {request.csvUrl}")
        
        # Fetch CSV from URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(request.csvUrl))
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch CSV from URL: {response.status_code}"
                )
            
            csv_content = response.text
        
        logger.info(f"✅ CSV fetched: {len(csv_content)} characters")
        
        # Analyze CSV
        result = await analyze_csv(csv_content, request.prompt)
        
        return CsvReply(
            summary=result["summary"],
            plot_base64=result.get("plot_base64")
        )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Error fetching CSV: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch CSV: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ CSV analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CSV analysis failed: {str(e)}"
        )


@router.post("/file", response_model=CsvReply)
async def analyze_csv_file(
    file: UploadFile = File(...),
    prompt: str = "Summarize this dataset",
    user_id: str = Depends(get_current_user)
):
    """
    Analyze an uploaded CSV file (single-shot analysis).
    Supports questions like: "Summarize", "Show stats", "Missing values", "Plot histogram"
    
    Requires authentication.
    Note: Use /chat endpoints for multi-turn conversations.
    """
    try:
        # Check file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file (.csv extension)"
            )
        
        logger.info(f"📊 Processing CSV file: {file.filename}")
        
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        logger.info(f"✅ CSV loaded: {len(csv_content)} characters")
        
        # Analyze CSV
        result = await analyze_csv(csv_content, prompt)
        
        return CsvReply(
            summary=result["summary"],
            plot_base64=result.get("plot_base64")
        )
        
    except UnicodeDecodeError:
        logger.error("❌ Invalid CSV encoding")
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file encoding. Please ensure the file is UTF-8 encoded."
        )
    except Exception as e:
        logger.error(f"❌ CSV analysis error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"CSV analysis failed: {str(e)}"
        )


# ============================================
# NEW CHAT ENDPOINTS (AI Chatbot)
# ============================================

@router.post("/chat/upload-url", response_model=CsvUploadResponse)
async def upload_csv_url_for_chat(
    request: CsvInUrl,
    user_id: str = Depends(get_current_user)
):
    """
    Upload CSV from URL and start a new chat session.
    Returns session_id for ongoing conversation.
    
    Requires authentication.
    
    Example:
    POST /csv/chat/upload-url
    {
        "csvUrl": "https://example.com/data.csv",
        "prompt": "I want to analyze this dataset"
    }
    """
    try:
        logger.info(f"🆕 Creating chat session from URL: {request.csvUrl}")
        
        # Fetch CSV from URL
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(str(request.csvUrl))
            
            if response.status_code != 200:
                raise HTTPException(
                    status_code=400,
                    detail=f"Failed to fetch CSV from URL: {response.status_code}"
                )
            
            csv_content = response.text
        
        # Create chat session
        session_data = await create_csv_session(
            csv_content=csv_content,
            source_type="url",
            source_value=str(request.csvUrl),
            initial_message=request.prompt
        )
        
        return CsvUploadResponse(
            session_id=session_data["session_id"],
            message=session_data["message"],
            csv_info=session_data["csv_info"]
        )
        
    except httpx.RequestError as e:
        logger.error(f"❌ Error fetching CSV: {e}")
        raise HTTPException(
            status_code=400,
            detail=f"Failed to fetch CSV: {str(e)}"
        )
    except Exception as e:
        logger.error(f"❌ Session creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post("/chat/upload-file", response_model=CsvUploadResponse)
async def upload_csv_file_for_chat(
    file: UploadFile = File(...),
    user_id: str = Depends(get_current_user)
):
    """
    Upload CSV file and start a new chat session.
    Returns session_id for ongoing conversation.
    
    Requires authentication.
    
    Example:
    POST /csv/chat/upload-file
    Form data: file=data.csv
    """
    try:
        # Check file extension
        if not file.filename.endswith('.csv'):
            raise HTTPException(
                status_code=400,
                detail="File must be a CSV file (.csv extension)"
            )
        
        logger.info(f"🆕 Creating chat session from file: {file.filename}")
        
        # Read CSV content
        content = await file.read()
        csv_content = content.decode('utf-8')
        
        # Create chat session
        session_data = await create_csv_session(
            csv_content=csv_content,
            source_type="file",
            source_value=file.filename,
            initial_message="I've uploaded a CSV file. Please give me an overview."
        )
        
        return CsvUploadResponse(
            session_id=session_data["session_id"],
            message=session_data["message"],
            csv_info=session_data["csv_info"]
        )
        
    except UnicodeDecodeError:
        logger.error("❌ Invalid CSV encoding")
        raise HTTPException(
            status_code=400,
            detail="Invalid CSV file encoding. Please ensure the file is UTF-8 encoded."
        )
    except Exception as e:
        logger.error(f"❌ Session creation error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to create session: {str(e)}"
        )


@router.post("/chat/message", response_model=CsvChatReply)
async def send_chat_message(
    request: CsvChatRequest,
    user_id: str = Depends(get_current_user)
):
    """
    Send a message in an ongoing CSV chat session.
    AI will respond based on conversation history and CSV data.
    
    Requires authentication.
    
    Example:
    POST /csv/chat/message
    {
        "session_id": "csv_1234567890",
        "message": "What are the top 5 values in the price column?"
    }
    """
    try:
        logger.info(f"💬 Chat message for session: {request.session_id}")
        
        # Process chat message
        result = await chat_with_csv(
            session_id=request.session_id,
            user_message=request.message
        )
        
        return CsvChatReply(
            session_id=result["session_id"],
            reply=result["reply"],
            plot_base64=result.get("plot_base64"),
            conversation_history=result["conversation_history"]
        )
        
    except ValueError as e:
        # Session not found
        logger.error(f"❌ Invalid session: {e}")
        raise HTTPException(
            status_code=404,
            detail=str(e)
        )
    except Exception as e:
        logger.error(f"❌ Chat error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat failed: {str(e)}"
        )


@router.get("/chat/session/{session_id}")
async def get_chat_session(
    session_id: str,
    user_id: str = Depends(get_current_user)
):
    """
    Get information about a chat session.
    Returns CSV info and conversation history.
    
    Requires authentication.
    """
    try:
        session_info = get_session_info(session_id)
        
        if not session_info:
            raise HTTPException(
                status_code=404,
                detail=f"Session not found: {session_id}"
            )
        
        return session_info
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error fetching session: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch session: {str(e)}"
        )


# ============================================
# DATABASE MIGRATION NOTES
# ============================================
# TODO: When implementing database storage:
# 
# 1. Replace in-memory sessions with database queries:
#    - create_csv_session() → INSERT into csv_sessions table
#    - chat_with_csv() → INSERT into csv_conversations table
#    - get_session_info() → SELECT from both tables
#
# 2. Store CSV files in Supabase Storage:
#    - Upload CSV to storage bucket
#    - Store file URL in csv_sessions.csv_file_url
#    - Load from URL when needed
#
# 3. Add user authentication:
#    - Add user_id to all session operations
#    - Filter sessions by user_id
#
# 4. Add cleanup/expiration:
#    - Delete old sessions after 24 hours
#    - Archive completed conversations